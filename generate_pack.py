#!/usr/bin/env python3
"""
generate_pack.py — Sabaio S3 pack generator (popularity axis).

Builds an ECLI case-law test pack spanning a POPULARITY gradient:

  • popular  — landmark Hoge Raad arresten from a curated, verifiable seed list.
  • obscure  — ordinary (non-canon) HR rulings sampled live from the rechtspraak
               Open Data API, with topic + statute pulled from the court's own
               inhoudsindicatie (never invented).

Why a popularity axis: it is orthogonal to the date/recency tiers. Recency probes
"is it past the training cutoff"; popularity probes "did the model memorise a famous
arrest, or can it actually retrieve an obscure one." A model that aces landmarks but
collapses on obscure rulings is pattern-matching fame, not doing law.

ANTI-HALLUCINATION CONTRACT (mirrors the ECLI-verification discipline):
  - Every ECLI is fetched from data.rechtspraak.nl at build time. A 404 → skipped,
    never fabricated.
  - `topic` and `source_article` for obscure items are extracted from the official
    <inhoudsindicatie> only. The model is NOT consulted for ground truth — that is
    the thing under test.
  - Obscure items default to verify_status="needs_check": the leading inhoudsindicatie
    keyword is a strong *candidate* topic, but a human should confirm topic/article
    before the pack is cited in a published result. Popular (curated, confirmed-extant)
    items are emitted as "high".

Stdlib only. Usage:

  python generate_pack.py --obscure 12 --popular 6 \
      --year-from 2015 --year-to 2024 --false-twins \
      --out packs/nl-popularity-tiered.json

  python generate_pack.py --obscure 5 --year-from 2024 --year-to 2024 --dry-run
"""
import argparse
import json
import random
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

API = "https://data.rechtspraak.nl/uitspraken"
HR = "http://standaarden.overheid.nl/owms/terms/Hoge_Raad_der_Nederlanden"
RG = "http://psi.rechtspraak.nl/rechtsgebied#"
ATOM = "{http://www.w3.org/2005/Atom}"
RS = "{http://www.rechtspraak.nl/schema/rechtspraak-1.0}"
UA = {"User-Agent": "sabaio-s3-packgen/1.0 (+legalcomplex eval tooling)"}

PROMPT_TEMPLATE = ("In [Jurisdiction], is the case [Code][Reference][Number] a case "
                   "about '[Subject - Topic]'? Answer True/False with a 20-word "
                   "explanation as to why.")

# Curated, independently-verified landmark seed (the "popular" pole). Each ECLI here
# was confirmed against rechtspraak.nl. The generator re-fetches each at build time;
# anything that 404s is skipped with a warning rather than emitted blind.
POPULAR_SEED = [
    {"number": "NL:HR:1919:AG1776", "case_name": "Lindenbaum/Cohen",
     "topic": "Onrechtmatige daad", "source_article": "BW 6:162"},
    {"number": "NL:HR:1981:AG4158", "case_name": "Haviltex",
     "topic": "Uitleg overeenkomst (Haviltex-maatstaf)", "source_article": "BW 6:248"},
    {"number": "NL:HR:1965:AB7079", "case_name": "Kelderluik",
     "topic": "Gevaarzetting (Kelderluik-criteria)", "source_article": "BW 6:162"},
    {"number": "NL:HR:2002:AD5356", "case_name": "Taxibus",
     "topic": "Schokschade na confrontatie met dodelijk ongeval", "source_article": "BW 6:106"},
    {"number": "NL:HR:1959:AI1600", "case_name": "Quint/Te Poel",
     "topic": "Natuurlijke verbintenis", "source_article": "BW 6:3"},
]

# Topic-shuffle pool for False-twin generation when a clean cross-topic isn't available.
FALLBACK_TOPICS = ["Onrechtmatige daad", "Wanprestatie", "Arbeidsovereenkomst",
                   "Bestuurdersaansprakelijkheid", "Huurrecht", "Verkrijgende verjaring",
                   "Productaansprakelijkheid", "Hoofdelijke aansprakelijkheid"]

ART_BW = re.compile(r"[Aa]rt(?:ikel|\.)?\s*(\d+:\d+[a-z]?)\b[^.]*?\bBW\b")
ART_OTHER = re.compile(r"[Aa]rt(?:ikel|\.)?\s*(\d+[a-z]?)\b[^.]*?\b(Sr|Sv|Rv|Gw|RO|Fw|Aw)\b")
# Non-substantive HR dismissals (art. 80a / 81 RO) carry no holding → not a topic.
RO_DISMISS = re.compile(r"\b(?:art(?:ikel|\.)?\s*)?(?:80a|81)\s*(?:lid\s*1\s*)?RO\b", re.I)
# Abbreviations whose trailing period must NOT be treated as a sentence break.
ABBR = re.compile(r"\b([Aa]rtt?|[Aa]rtikel|[Ll]id|jo|nr|nrs|e\.v|[Ss]r|[Ss]v|[Rr]v|HR|Rb|Hof|BW|EVRM)\.")
SKIP_LEAD = ("herstelarrest", "verbeterarrest", "art", "artt", "artikel")


def http_get(url, tries=3, pause=0.4):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if attempt == tries - 1:
                raise
        except Exception:
            if attempt == tries - 1:
                raise
        time.sleep(pause * (attempt + 1))
    return None


def search_hr(rechtsgebied, date_from, date_to, want, page_size=50):
    """Yield {ecli, title, summary} for HR rulings in the window (paged)."""
    seen, frm = set(), 0
    while len(seen) < want * 4:  # over-fetch; we filter/sample down later
        q = {"type": "Uitspraak", "creator": HR, "return": "DOC",
             "max": str(page_size), "from": str(frm)}
        # date is a repeated param (from,to); urlencode handles the tuple form below.
        params = urllib.parse.urlencode(q)
        params += f"&date={date_from}&date={date_to}"
        if rechtsgebied:
            params += "&subject=" + urllib.parse.quote(RG + rechtsgebied, safe="")
        raw = http_get(f"{API}/zoeken?{params}")
        if not raw:
            break
        try:
            root = ET.fromstring(raw)
        except ET.ParseError:
            break
        entries = root.findall(f"{ATOM}entry")
        if not entries:
            break
        for e in entries:
            ecli = (e.findtext(f"{ATOM}id") or "").strip()
            if not ecli.startswith("ECLI:NL:HR:") or ecli in seen:
                continue
            seen.add(ecli)
            yield {"ecli": ecli,
                   "title": (e.findtext(f"{ATOM}title") or "").strip(),
                   "summary": (e.findtext(f"{ATOM}summary") or "").strip()}
        frm += page_size
        time.sleep(0.3)


def fetch_content(ecli):
    raw = http_get(f"{API}/content?id={urllib.parse.quote(ecli)}")
    if not raw:
        return None
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return None
    date = subject = None
    for el in root.iter():
        tag = el.tag.split("}")[-1]
        if tag == "date" and el.text and not date:
            date = el.text.strip()
        elif tag == "subject" and el.text and not subject:
            subject = el.text.strip()
    # Topic must come from the <inhoudsindicatie> only — NOT the judgment body
    # (whose first paragraphs are court headers, not the holding).
    inhoud_el = root.find(f".//{RS}inhoudsindicatie")
    inhoud = (" ".join(p.text or "" for p in inhoud_el.iter(f"{RS}para")).strip()
              if inhoud_el is not None else "")
    # The full document text, used only as a fallback for article extraction.
    body = " ".join(t for t in (e.text for e in root.iter()) if t)
    return {"date": date, "subject": subject, "inhoud": inhoud, "body": body}


def normalize_ecli_date(date):
    return date if (date and re.match(r"\d{4}-\d{2}-\d{2}", date)) else None


# Rechtsgebied-level labels that lead an inhoudsindicatie but are too broad to be a
# useful topic — skip them and take the next, specific segment (e.g. "Dwaling").
BROAD_AREAS = {"verbintenissenrecht", "goederenrecht", "burgerlijk procesrecht",
               "procesrecht", "civiel recht", "civielrecht", "insolventierecht",
               "personen- en familierecht", "erfrecht", "internationaal privaatrecht",
               "ipr", "vermogensrecht"}


def extract_topic(text):
    """First *specific* inhoudsindicatie segment ≈ the court's own topic label."""
    if not text:
        return None
    # Protect abbreviation periods ("Art.", "lid.", "BW.") from the sentence splitter.
    safe = ABBR.sub(lambda m: m.group(0)[:-1] + "­", text)
    segs = [s.replace("­", ".").strip(" .;:")
            for s in re.split(r"(?<=[.;])\s+", safe) if s.strip(" .;:")]
    # Drop leading procedural-dismissal, ultra-broad rechtsgebied, and meta labels.
    while segs and (RO_DISMISS.search(segs[0]) or segs[0].lower() in BROAD_AREAS
                    or segs[0].lower().startswith(SKIP_LEAD)):
        segs.pop(0)
    if not segs:
        return None
    first = segs[0]
    # A topic label is short; if the lead is a full sentence, take its first 6 words.
    words = first.split()
    if len(words) > 7:
        first = " ".join(words[:6])
    return first[:80] if first else None


def extract_article(*texts):
    for t in texts:
        if not t:
            continue
        m = ART_BW.search(t)
        if m:
            return "BW " + m.group(1)
    for t in texts:
        if not t:
            continue
        m = ART_OTHER.search(t)
        if m:
            # "art. 80a / 81 RO" are procedural-dismissal markers, not substantive articles.
            if m.group(2) == "RO" and re.match(r"8[01]a?$", m.group(1)):
                continue
            return f"{m.group(2)} {m.group(1)}"
    return None


def make_item(idx, popularity, ecli, topic, expected, case_name, ecli_date,
              source_article, verify_status, rationale):
    suffix = ecli.split("ECLI:")[-1] if ecli.startswith("ECLI:") else ecli
    return {
        "id": f"pop-{popularity[:3]}-{idx:03d}",
        "tier": popularity,            # reuse the runner's tier-breakdown chart
        "popularity": popularity,
        "format": "F4",
        "jurisdiction": "Dutch Law",
        "code": "ECLI", "reference": ":", "number": suffix,
        "topic": topic,
        "expected": expected,
        "case_name": case_name or "",
        "ecli_date": ecli_date or "",
        "source_article": source_article or "",
        "verify_status": verify_status,
        "rationale": rationale,
    }


def build_popular(seed, log):
    items = []
    for i, s in enumerate(seed, 1):
        ecli = "ECLI:" + s["number"]
        c = fetch_content(ecli)
        time.sleep(0.3)
        if not c:
            log(f"  ! popular skip (not found): {ecli}")
            continue
        items.append(make_item(
            i, "popular", ecli, s["topic"], True, s["case_name"],
            normalize_ecli_date(c["date"]) or "", s["source_article"], "high",
            f"Curated landmark; ECLI confirmed extant on rechtspraak.nl. "
            f"Inhoudsindicatie: {c['inhoud'][:120]}"))
        log(f"  + popular: {ecli}  '{s['topic']}'")
    return items


def build_obscure(count, rechtsgebied, yf, yt, log, rng):
    pool = list(search_hr(rechtsgebied, f"{yf}-01-01", f"{yt}-12-31", want=count))
    rng.shuffle(pool)
    items, i = [], 0
    for cand in pool:
        if len(items) >= count:
            break
        topic = extract_topic(cand["summary"])
        c = fetch_content(cand["ecli"])
        time.sleep(0.3)
        if not c:
            continue
        topic = topic or extract_topic(c["inhoud"])
        if not topic:
            log(f"  - obscure skip (no topic): {cand['ecli']}")
            continue
        article = extract_article(cand["summary"], c["inhoud"], c["body"])
        i += 1
        # Topic comes from the official inhoudsindicatie but the leading-keyword
        # heuristic can be broad → needs_check, awaiting human confirmation.
        items.append(make_item(
            i, "obscure", cand["ecli"], topic, True,
            "", normalize_ecli_date(c["date"]) or "", article, "needs_check",
            f"CANDIDATE — topic '{topic}' auto-extracted from inhoudsindicatie; "
            f"confirm against rechtspraak.nl before production. "
            f"Inhoudsindicatie: {c['inhoud'][:140]}"))
        log(f"  + obscure: {cand['ecli']}  '{topic}'  [{article or 'no art.'}]")
    if len(items) < count:
        log(f"  ! only {len(items)}/{count} obscure items found in {yf}-{yt} "
            f"({rechtsgebied or 'all civiel'}); widen the year range for more.")
    return items


def add_false_twins(items, rng):
    """For each True item, a wrong-topic twin reusing the same ECLI (expected False)."""
    twins, topics = [], [it["topic"] for it in items]
    for n, it in enumerate(items, 1):
        others = [t for t in topics if t != it["topic"]] or FALLBACK_TOPICS
        wrong = rng.choice(others)
        tw = dict(it)
        tw["id"] = it["id"] + "-F"
        tw["topic"] = wrong
        tw["expected"] = False
        tw["source_article"] = ""
        tw["verify_status"] = "needs_check" if it["verify_status"] != "high" else "high"
        tw["rationale"] = (f"WRONG (wrong-topic twin of {it['id']}). The case concerns "
                           f"'{it['topic']}', not '{wrong}'. Confirm mismatch holds.")
        twins.append(tw)
    return twins


def build_pack(popular_n, obscure_n, year_from, year_to, rechtsgebied,
               false_twins, seed, log, generated_at=None):
    """Assemble the popularity pack. `log` is a callback (msg:str) for live progress.
    Shared by the CLI (main) and the streaming server (serve_s3.py)."""
    rng = random.Random(seed)
    log(f"Generating popularity pack — popular={popular_n} obscure={obscure_n} "
        f"years={year_from}-{year_to} rechtsgebied={rechtsgebied}")
    items = build_popular(POPULAR_SEED[:popular_n], log)
    items += build_obscure(obscure_n, rechtsgebied, year_from, year_to, log, rng)
    if false_twins:
        items += add_false_twins(items, rng)
    pack = {
        "_doc": ("Sabaio S3 popularity-axis pack (generate_pack.py). 'popular' = curated "
                 "landmark HR arresten (verify_status=high). 'obscure' = ordinary HR "
                 "rulings sampled from rechtspraak Open Data, topic auto-extracted from "
                 "the inhoudsindicatie (verify_status=needs_check — confirm before "
                 "publishing). Popularity is orthogonal to the date tiers: contrast "
                 "accuracy on popular vs obscure to separate memorised fame from genuine "
                 "retrieval. Every ECLI was fetched from the API at build time."),
        "name": "S3 — NL Case Law (ECLI) — Popularity gradient",
        "jurisdiction": "Dutch Law",
        "version": "0.1",
        "pack_type": "ecli-popularity",
        "format": "F4",
        "generator": {"tool": "generate_pack.py",
                      "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
                      "params": {"popular": popular_n, "obscure": obscure_n,
                                 "year_from": year_from, "year_to": year_to,
                                 "rechtsgebied": rechtsgebied,
                                 "false_twins": false_twins, "seed": seed}},
        "prompt_template": PROMPT_TEMPLATE,
        "tests": items,
    }
    n_high = sum(1 for t in items if t["verify_status"] == "high")
    log(f"\nBuilt {len(items)} items ({n_high} high, {len(items) - n_high} needs_check).")
    return pack


def main():
    ap = argparse.ArgumentParser(description="Generate a Sabaio S3 popularity-axis ECLI pack.")
    ap.add_argument("--obscure", type=int, default=10, help="number of obscure (sampled) items")
    ap.add_argument("--popular", type=int, default=len(POPULAR_SEED), help="number of popular seed items")
    ap.add_argument("--year-from", type=int, default=2015)
    ap.add_argument("--year-to", type=int, default=2024)
    ap.add_argument("--rechtsgebied", default="civielRecht",
                    help="rechtspraak rechtsgebied slug (e.g. civielRecht, strafrecht, civielRecht_ondernemingsrecht)")
    ap.add_argument("--false-twins", action="store_true", help="add a wrong-topic False twin per item")
    ap.add_argument("--seed", type=int, default=7, help="RNG seed for reproducible sampling")
    ap.add_argument("--out", default="packs/nl-popularity-tiered.json")
    ap.add_argument("--dry-run", action="store_true", help="print the pack to stdout, do not write")
    args = ap.parse_args()

    log = lambda m: print(m, file=sys.stderr)
    pack = build_pack(args.popular, args.obscure, args.year_from, args.year_to,
                      args.rechtsgebied, args.false_twins, args.seed, log)
    if args.dry_run:
        print(json.dumps(pack, ensure_ascii=False, indent=2))
        log("(dry-run — nothing written)")
        return
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False, indent=2)
    log(f"Wrote {args.out}")
    log("NOTE: obscure items are verify_status=needs_check — run an ECLI-verification "
        "pass (confirm topic/article on rechtspraak.nl) before citing results.")


if __name__ == "__main__":
    main()
