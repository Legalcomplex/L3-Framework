#!/usr/bin/env python3
"""
generate_world_packs.py: source-grounded S3 packs for every jurisdiction in the
world-law catalog.

For each country in labs/world-law-catalog/world-law-catalog.json that has at
least one status="complete" legislation or case_law source with readable sample
documents on disk (labs/legal-sources/sources/{CC}/{SourceName}/sample/), this
script emits packs/world/{cc}-source-grounded.json: a True/False pack of purely
BIBLIOGRAPHIC claims (title, date, publishing source, identifier) grounded
verbatim in the collected sample records.

Anti-hallucination contract
---------------------------
No legal doctrine is ever asserted. Statements only bind metadata that was read
from a real collected document: its title (quoted verbatim, possibly truncated),
its recorded date, the official source that published it, and its identifier.

Item construction
-----------------
TRUE items (verify_status=high, repo-grounded):
  S1  "'{title}' was published via {source name} ({date})."          (non case law)
  S2  "Decision '{title}' ({date}) is published by {source name}."   (case law)
  S3  "In the collection of {source name}, identifier '{id}'
       corresponds to '{title}' ({date})."                           (id available)

FALSE items (verify_status=high, false by construction), one controlled
mutation of the SAME real docs per item:
  date-shift   : recorded date shifted by 1-3 years (claim shape S1/S2)
  wrong-source : doc attributed to a real official source of a DIFFERENT
                 (neighboring-region) country, the cross-jurisdiction trap
  id-mutation  : last digit group of the real identifier incremented (shape S3,
                 the claim binds the mutated id to the real title, so it stays
                 false even if the mutated id happens to exist for another doc)

Safety guards built in (see packs/world/README.md for the full rationale):
  * duplicate ("generic") titles within a country pool are only used with an
    identifier binding; they are never used for date-shift / wrong-source traps
  * wrong-source claimed sources are always from a different country, never a
    known multi-jurisdiction aggregator (BAILII, CourtListener, OpenJur, ...),
    and never share a root domain with the true source
  * date-shift prefers court decisions whose title does not embed the year
  * mutated identifiers are checked against every identifier seen in the
    country pool to avoid colliding with another real record

Determinism
-----------
All sampling uses random.Random(f"s3-world-v1:{CC}") and sorted iteration, so
regeneration is byte-identical for an unchanged catalog + sample snapshot. The
"generated" stamp is the catalog's own meta.generated date (not wall clock).

Tier convention
---------------
Existing packs use date-based tiers (T1-established / T2-uncertain /
T3-post-cutoff). Dates here are claim CONTENT, not recency probes, so every
item carries the single tier value "source" (documented choice per pack _doc).

Dependencies: Python 3 stdlib only. config.yaml files are NOT read (the catalog
plus the sample JSON records carry everything needed), so pyyaml is not required.

Usage:
  python3 generate_world_packs.py                 # generate all packs + index
  python3 generate_world_packs.py --only NL,DE    # subset (index still rewritten
                                                  #         for the subset only)
  python3 generate_world_packs.py --dry-run       # stats only, write nothing
"""

import argparse
import json
import os
import random
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
LABS = os.path.abspath(os.path.join(HERE, "..", ".."))
CATALOG_PATH = os.path.join(LABS, "world-law-catalog", "world-law-catalog.json")
SOURCES_ROOT = os.path.join(LABS, "legal-sources", "sources")
OUT_DIR = os.path.join(HERE, "packs", "world")

SEED_NS = "s3-world-v1"
MAX_DOCS = 6            # up to 6 docs -> 6 True + 6 False = 12 items
MIN_DOCS = 2            # below 2 docs (4 items) the country is skipped
TITLE_TRUNC = 110       # truncation budget for statement titles
TITLE_TRUNC_MAX = 170   # extended budget when truncation causes collisions

DATA_TYPES = {"legislation", "case_law"}

# Identifier fields considered "official-looking" (in priority order). The
# repo-internal _id is used only when it looks like a clean official identifier
# (no slashes, e.g. BWBR0001827 or ECLI:...), since claims about identifiers
# must be claims about the SOURCE's scheme, not our collection's.
IDENT_FIELDS = (
    "ecli", "neutral_citation", "case_number", "doc_id", "decision_id",
    "systematic_number", "resolution_number", "celex", "bwb_id",
)
CLEAN_ID_RE = re.compile(r"^(ECLI:[A-Za-z0-9:.\-]+|[A-Z]{2,8}[0-9]{3,})$")

# Multi-jurisdiction aggregators / databases must never be the CLAIMED source
# of a wrong-source trap (they may genuinely host foreign documents).
AGGREGATOR_RE = re.compile(
    r"(?i)(\blii\b|lii\)|bailii|canlii|austlii|saflii|paclii|worldlii|commonlii|"
    r"asianlii|hklii|nzlii|courtlistener|caselaw|case\s*law\s*access|openjur|"
    r"openlegaldata|legiscan|openstates|pileoflaw|publicresource|govinfo|recap\b|"
    r"juriscraper|vlex|hudoc|eur-?lex|n-lex|natlex|faolex|ecolex|wipo|worldcourts|"
    r"legislationline|global.?regulation|un\s*treaty|official\s*document\s*system|"
    r"juricaf|lawphil|lexum)"
)

# Pseudo-jurisdictions whose sources are inherently multi-country; they get
# packs of their own but are excluded from the wrong-source claimed pool.
INTL_CODES = {"EU", "UN", "INTL", "CoE"}

# Coarse region map (ISO-3166-ish codes as used by the catalog) for picking a
# "neighboring country" in wrong-source traps. Trap plausibility only; the
# correctness of an item never depends on this map.
REGIONS = {
    "eu_w": ["AD", "AT", "BE", "CH", "DE", "ES", "FR", "GG", "GI", "IE", "IM",
              "IT", "JE", "LI", "LU", "MC", "MT", "NL", "PT", "SM", "UK", "VA"],
    "nordics": ["AX", "DK", "FI", "FO", "GL", "IS", "NO", "SE"],
    "eu_e": ["AL", "AM", "AZ", "BA", "BG", "BY", "CY", "CZ", "EE", "GE", "GR",
              "HR", "HU", "LT", "LV", "MD", "ME", "MK", "PL", "RO", "RS", "RU",
              "SI", "SK", "TR", "UA", "XK"],
    "mideast": ["AE", "BH", "IL", "IQ", "IR", "JO", "KW", "LB", "OM", "PS",
                 "QA", "SA", "SY", "YE"],
    "c_asia": ["KG", "KZ", "TJ", "TM", "UZ"],
    "s_asia": ["AF", "BD", "BT", "IN", "LK", "MV", "NP", "PK"],
    "e_asia": ["CN", "HK", "JP", "KR", "MN", "MO", "TW"],
    "se_asia": ["BN", "ID", "KH", "LA", "MM", "MY", "PH", "SG", "TH", "TL", "VN"],
    "oceania": ["AS", "AU", "CK", "FJ", "FM", "GU", "KI", "MH", "MP", "NC",
                 "NF", "NR", "NU", "NZ", "PF", "PG", "PN", "PW", "SB", "TO",
                 "TV", "VU", "WF", "WS"],
    "nam": ["CA", "PM", "US"],
    "carib": ["AG", "AI", "AW", "BB", "BL", "BM", "BQ", "BS", "CU", "CW", "DM",
               "DO", "GD", "HT", "JM", "KN", "KY", "LC", "MF", "MS", "PR", "SX",
               "TC", "TT", "VC", "VG", "VI"],
    "cam": ["BZ", "CR", "GT", "HN", "MX", "NI", "PA", "SV"],
    "sam": ["AR", "BO", "BR", "CL", "CO", "EC", "FK", "GY", "PE", "PY", "SR",
             "UY", "VE"],
    "afr_n": ["DZ", "EG", "LY", "MA", "TN"],
    "afr_w": ["BF", "BJ", "CI", "CV", "GH", "GM", "GN", "GW", "LR", "ML", "MR",
               "NE", "NG", "SL", "SN", "TG"],
    "afr_c": ["AO", "CD", "CF", "CG", "CM", "GA", "GQ", "ST", "TD"],
    "afr_e": ["BI", "DJ", "ER", "ET", "KE", "KM", "MG", "MU", "MW", "MZ", "RW",
               "SC", "SD", "SO", "SS", "TZ", "UG"],
    "afr_s": ["BW", "LS", "NA", "SH", "SZ", "ZA", "ZM", "ZW"],
    "intl": ["CoE", "EU", "INTL", "UN"],
}
REGION_OF = {cc: region for region, ccs in REGIONS.items() for cc in ccs}
# Sources of the intl pseudo-jurisdictions sit in Europe institutionally, so
# their wrong-source traps draw on western-European national sources.
NEIGHBOR_REGION_FOR_INTL = "eu_w"

YEAR_RE = re.compile(r"\b(1[5-9]\d{2}|20[0-2]\d)\b")
WS_RE = re.compile(r"\s+")


# ---------------------------------------------------------------- utilities --

def norm_ws(s):
    return WS_RE.sub(" ", s).strip()


def root_domain(url):
    if not isinstance(url, str) or not url:
        return ""
    host = re.sub(r"^[a-z]+://", "", url.strip(), flags=re.I).split("/")[0]
    host = host.split("@")[-1].split(":")[0].lower()
    if host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def display_date(raw):
    """Normalize a recorded date string to YYYY[-MM[-DD]] for display."""
    if not isinstance(raw, str):
        return None
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", raw.strip())
    if m:
        return m.group(0)
    m = re.match(r"^(\d{4})-(\d{2})$", raw.strip())
    if m:
        return m.group(0)
    m = YEAR_RE.search(raw)
    return m.group(1) if m else None


def year_of(display):
    return int(display[:4])


def is_leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def shift_date(display, delta):
    """Shift the year of a display date by delta, fixing Feb 29 if needed."""
    y = year_of(display) + delta
    shifted = f"{y:04d}" + display[4:]
    if shifted[5:10] == "02-29" and not is_leap(y):
        shifted = shifted[:8] + "28"
    return shifted


def truncate_title(title, limit):
    if len(title) <= limit:
        return title
    cut = title[:limit]
    if " " in cut[40:]:
        cut = cut[: cut.rindex(" ")]
    return cut.rstrip(" ,;:.") + "…"


def official_identifier(doc):
    """Best official-looking identifier of a record, or None."""
    for field in IDENT_FIELDS:
        v = doc.get(field)
        if isinstance(v, str):
            v = v.strip()
            # 4+ chars keeps out bare row indexes like "17", which are not
            # official citation schemes.
            if v and any(ch.isdigit() for ch in v) and 4 <= len(v) <= 80:
                return v
    v = doc.get("_id")
    if (isinstance(v, str) and CLEAN_ID_RE.match(v.strip())
            and any(ch.isdigit() for ch in v)):
        return v.strip()
    return None


def increment_identifier(ident, known_idents):
    """Increment the LAST digit group of an identifier.

    Collision avoidance against identifiers seen in the country pool is
    best-effort only: even a colliding mutation stays FALSE, because the claim
    binds the mutated identifier to THIS doc's title, and a colliding
    identifier belongs to a different document. Callers guarantee `ident`
    contains at least one digit (official_identifier enforces it).
    """
    m = list(re.finditer(r"\d+", ident))[-1]
    first = None
    for bump in range(1, 6):
        new_num = str(int(m.group(0)) + bump).zfill(len(m.group(0)))
        cand = ident[: m.start()] + new_num + ident[m.end():]
        first = first or cand
        if cand not in known_idents:
            return cand
    return first


# ----------------------------------------------------------- sample loading --

def load_sample_docs(sample_dir, stats):
    """Read every *.json in a sample dir; tolerate dict or list shapes; dedupe."""
    docs, seen = [], set()
    try:
        files = sorted(os.listdir(sample_dir))
    except OSError:
        return docs
    for fn in files:
        if not fn.endswith(".json"):
            continue
        path = os.path.join(sample_dir, fn)
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError, UnicodeDecodeError):
            stats["unreadable_files"] += 1
            continue
        records = data if isinstance(data, list) else [data]
        for rec in records:
            if not isinstance(rec, dict):
                continue
            title = rec.get("title")
            date_raw = rec.get("date")
            if not isinstance(title, str):
                continue
            title = norm_ws(title)
            if len(title) < 5:
                continue
            disp = display_date(date_raw) if isinstance(date_raw, str) else None
            if not disp or not (1500 <= year_of(disp) <= 2027):
                continue
            key = rec.get("_id") or (title[:80], disp)
            if key in seen:
                continue
            seen.add(key)
            url = rec.get("url")
            docs.append({
                "title": title,
                "date_raw": date_raw,
                "date": disp,
                "url": url if isinstance(url, str) else None,
                "doc_type": rec.get("_type"),
                "ident": official_identifier(rec),
                "rec_id": rec.get("_id"),
            })
    return docs


# --------------------------------------------------------------- statements --

def statement_for(doc, source_name, date=None, ident=None):
    """Build the claim sentence. Same surface shapes for True and False items."""
    date = date or doc["date"]
    if ident is not None:
        return (f"In the collection of {source_name}, identifier '{ident}' "
                f"corresponds to '{doc['title_disp']}' ({date}).")
    if doc["doc_type"] == "case_law":
        return f"Decision '{doc['title_disp']}' ({date}) is published by {source_name}."
    return f"'{doc['title_disp']}' was published via {source_name} ({date})."


def shape_of(doc, ident):
    if ident is not None:
        return "S3-identifier"
    return "S2-decision" if doc["doc_type"] == "case_law" else "S1-published-via"


# --------------------------------------------------------------- generation --

def build_claimed_pool(catalog):
    """All complete, non-aggregator, nationally-scoped sources: wrong-source pool."""
    pool = []
    for cc in sorted(catalog["countries"]):
        if cc in INTL_CODES:
            continue
        country = catalog["countries"][cc]
        for src in country["sources"]:
            if src.get("status") != "complete":
                continue
            name = src.get("name") or ""
            if not name or AGGREGATOR_RE.search(name) or AGGREGATOR_RE.search(src.get("id", "")):
                continue
            pool.append({
                "cc": cc,
                "country_name": country.get("name", cc),
                "region": REGION_OF.get(cc, "world"),
                "id": src["id"],
                "name": name,
                "domain": root_domain(src.get("url", "")),
                "dataTypes": src.get("dataTypes", []),
                "priority": src.get("priority", 9),
            })
    return pool


def pick_wrong_source(doc_cc, doc_type, true_domain, claimed_pool, rng, used):
    """A real official source of a DIFFERENT (neighboring-region) country.

    Plausibility tiering for a strong trap: prefer sources of the same data
    type (court decision -> a foreign courts portal) and catalog priority 1
    (national flagship sources), before falling back to anything safe. `used`
    keeps claimed sources varied within one pack when alternatives exist.
    """
    region = (NEIGHBOR_REGION_FOR_INTL if doc_cc in INTL_CODES
              else REGION_OF.get(doc_cc, "world"))
    def ok(c):
        return c["cc"] != doc_cc and c["domain"] and c["domain"] != true_domain
    pool_ok = [c for c in claimed_pool if ok(c)]
    base = [c for c in pool_ok if c["region"] == region] or pool_ok
    if not base:
        return None
    typed = ([c for c in base if doc_type in c["dataTypes"]]
             if doc_type in ("legislation", "case_law") else [])
    flagship = [c for c in (typed or base) if c["priority"] <= 1]
    candidates = flagship or typed or base
    fresh = [c for c in candidates if c["id"] not in used]
    candidates = fresh or candidates
    return rng.choice(sorted(candidates, key=lambda c: (c["cc"], c["id"])))


def select_docs(per_source_docs, rng, want):
    """Round-robin across sources (shuffled within each) up to `want` docs."""
    queues = []
    for src, docs in per_source_docs:
        docs = list(docs)
        rng.shuffle(docs)
        queues.append((src, docs))
    picked, seen_titles = [], {}
    qi = 0
    while len(picked) < want and any(d for _, d in queues):
        src, docs = queues[qi % len(queues)]
        qi += 1
        if not docs:
            continue
        doc = docs.pop(0)
        # Unique truncated title within the pack (extend budget on collision);
        # an identical full title means the same doc reached us twice via two
        # sources: skip the second copy.
        disp = truncate_title(doc["title"], TITLE_TRUNC)
        if disp in seen_titles:
            if seen_titles[disp] == doc["title"]:
                continue
            disp = truncate_title(doc["title"], TITLE_TRUNC_MAX)
            if disp in seen_titles:
                continue
        seen_titles[disp] = doc["title"]
        doc = dict(doc)
        doc["title_disp"] = disp
        doc["source"] = src
        picked.append(doc)
    return picked


def assign_mutations(docs, rng):
    """One mutation class per doc: ~even split, respecting per-doc feasibility."""
    n = len(docs)
    base, extra = divmod(n, 3)
    targets = {"id-mutation": base, "wrong-source": base, "date-shift": base}
    for cls in ("date-shift", "wrong-source", "id-mutation")[:extra]:
        targets[cls] += 1

    assignment = {}
    remaining = list(range(n))

    def feasible(i, cls):
        d = docs[i]
        if cls == "id-mutation":
            return d["ident"] is not None
        if d["generic"]:        # duplicate-title docs: identifier binding only
            return False
        return True

    # A date-shift on a title that embeds its own year ("Women's Act 2010")
    # self-contradicts inside the statement: still false, but trivially easy.
    # Such docs are kept out of the date-shift fill phase and steered to
    # wrong-source in the leftover pass.
    def year_in_title(d):
        return d["date"][:4] in d["title"]
    def id_in_title(d):
        return bool(d["ident"]) and d["ident"] in d["title"]

    # Most-constrained first: id-mutation (generic docs first, it is their only
    # feasible class; then docs whose title does not embed the identifier, so
    # the mismatch is not visible inside the statement itself), then date-shift,
    # then wrong-source.
    for cls, prefer, extra_ok in (
        ("id-mutation", lambda d: (0 if d["generic"] else 1, 1 if id_in_title(d) else 0),
         lambda d: True),
        # Prefer court decisions for date-shift: decision dates are
        # single-valued, while legislation portals re-version laws under new
        # effective dates, which could make a shifted date accidentally real.
        ("date-shift", lambda d: 0 if d["doc_type"] == "case_law" else 1,
         lambda d: not year_in_title(d)),
        ("wrong-source", lambda d: 0, lambda d: True),
    ):
        want = targets[cls]
        cands = sorted((i for i in remaining if feasible(i, cls) and extra_ok(docs[i])),
                       key=lambda i: (prefer(docs[i]), i))
        for i in cands[:want]:
            assignment[i] = cls
            remaining.remove(i)

    # Anything left over: first feasible class, steering year-in-title docs
    # away from date-shift.
    for i in list(remaining):
        order = (("wrong-source", "date-shift", "id-mutation")
                 if year_in_title(docs[i])
                 else ("date-shift", "wrong-source", "id-mutation"))
        for cls in order:
            if feasible(i, cls):
                assignment[i] = cls
                remaining.remove(i)
                break
    return assignment  # docs with no feasible class are dropped from FALSE side


def build_pack(cc, country, per_source_docs, claimed_pool, generated, rng):
    # Mark generic (duplicate) titles within the whole country pool, BEFORE
    # selection: a duplicate title (e.g. the standard Japanese case-type names,
    # or one decision collected by two sources) is only safely mutable through
    # an identifier binding, so generic docs without an identifier are excluded
    # from selection up front instead of wasting picks.
    title_counts = Counter()
    for _, ds in per_source_docs:
        for d in ds:
            title_counts[d["title"].casefold()] += 1
    feasible_per_source = []
    for src, ds in per_source_docs:
        kept_docs = []
        for d in ds:
            duplicated = title_counts[d["title"].casefold()] > 1
            # Short undated titles ("THE REPUBLIC OF KENYA", "Penal Code") are
            # boilerplate-prone: even if unique in our small sample, the live
            # source may carry many docs under the same heading, so treat them
            # like duplicates (identifier binding required).
            boilerplate = (len(d["title"].split()) <= 4
                           and not any(ch.isdigit() for ch in d["title"]))
            d["generic"] = duplicated or boilerplate
            if (not d["generic"]) or d["ident"]:
                kept_docs.append(d)
        if kept_docs:
            feasible_per_source.append((src, kept_docs))
    if not feasible_per_source:
        return None

    docs = select_docs(feasible_per_source, rng, MAX_DOCS)
    if len(docs) < MIN_DOCS:
        return None

    mutations = assign_mutations(docs, rng)
    kept = sorted(mutations)
    docs = [docs[i] for i in kept]
    mutations = {new_i: mutations[old_i] for new_i, old_i in enumerate(kept)}
    if len(docs) < MIN_DOCS:
        return None

    # Every identifier seen in the country pool, for mutation collision checks.
    pool_idents = {d["ident"] for _, ds in per_source_docs for d in ds if d["ident"]}

    cn = country.get("name", cc)
    tests = []

    # ---- TRUE items: verbatim record metadata.
    for i, doc in enumerate(docs):
        src = doc["source"]
        use_ident = doc["ident"] is not None and (doc["generic"] or i % 3 == 2)
        ident = doc["ident"] if use_ident else None
        stmt = statement_for(doc, src["name"], ident=ident)
        tests.append({
            "id": f"{cc.lower()}-src-t{i + 1:02d}",
            "tier": "source",
            "format": "F5",
            "jurisdiction": cn,
            "code": src["name"],
            "reference": "",
            "number": ident or "",
            "topic": stmt,
            "expected": True,
            "verify_status": "high",
            "shape": shape_of(doc, ident),
            "data_type": doc["doc_type"],
            "source_id": src["id"],
            "source_name": src["name"],
            "source_url": src.get("url"),
            "doc_title": doc["title"],
            "doc_date": doc["date"],
            "doc_url": doc["url"],
            "doc_identifier": doc["ident"],
            "rationale": (
                f"Grounded in the collected sample record for {src['id']} "
                f"(worldwidelaw/legal-sources snapshot): title and date are "
                f"verbatim record metadata."
                + (f" Record URL: {doc['url']}" if doc["url"] else "")
            ),
        })

    # ---- FALSE items: controlled mutations of the same docs.
    used_claimed = set()
    for i, doc in enumerate(docs):
        src = doc["source"]
        cls = mutations[i]
        short = truncate_title(doc["title"], 60)
        item = {
            "id": f"{cc.lower()}-src-f{i + 1:02d}",
            "tier": "source",
            "format": "F5",
            "jurisdiction": cn,
            "code": src["name"],
            "reference": "",
            "number": "",
            "expected": False,
            "verify_status": "high",
            "mutation": cls,
            "data_type": doc["doc_type"],
            "source_id": src["id"],
            "source_name": src["name"],
            "source_url": src.get("url"),
            "doc_title": doc["title"],
            "doc_date": doc["date"],
            "doc_url": doc["url"],
            "doc_identifier": doc["ident"],
        }
        if cls == "wrong-source":
            claimed = pick_wrong_source(cc, doc["doc_type"],
                                        root_domain(src.get("url", "")),
                                        claimed_pool, rng, used_claimed)
            if claimed is None:        # no safe foreign candidate: fall back
                cls = "date-shift"
            else:
                used_claimed.add(claimed["id"])
        if cls == "date-shift":
            deltas = [d for d in (-3, -2, -1, 1, 2, 3)
                      if 1000 <= year_of(doc["date"]) + d <= 2026]
            delta = rng.choice(deltas)
            claimed_date = shift_date(doc["date"], delta)
            item["mutation"] = "date-shift"
            item["topic"] = statement_for(doc, src["name"], date=claimed_date)
            item["shape"] = shape_of(doc, None)
            item["claimed_date"] = claimed_date
            item["rationale"] = (
                f"WRONG (date-shift mutation): the collected record for "
                f"'{short}' on {src['name']} is dated {doc['date']}, not "
                f"{claimed_date} (year shifted by {delta:+d})."
            )
        elif cls == "wrong-source":
            item["topic"] = statement_for(doc, claimed["name"])
            item["shape"] = shape_of(doc, None)
            item["claimed_source_id"] = claimed["id"]
            item["claimed_source_name"] = claimed["name"]
            item["claimed_source_country"] = claimed["cc"]
            item["rationale"] = (
                f"WRONG (wrong-source mutation): '{short}' is a record of "
                f"{src['name']} ({cn}), not of {claimed['name']} "
                f"({claimed['country_name']}). Cross-jurisdiction trap."
            )
        else:  # id-mutation
            mutated = increment_identifier(doc["ident"], pool_idents)
            item["topic"] = statement_for(doc, src["name"], ident=mutated)
            item["shape"] = "S3-identifier"
            item["number"] = mutated
            item["claimed_identifier"] = mutated
            item["rationale"] = (
                f"WRONG (identifier mutation): in the collected {src['name']} "
                f"record, '{short}' has identifier '{doc['ident']}'; "
                f"'{mutated}' is a constructed near-miss (last digit group "
                f"incremented)."
            )
        tests.append(item)

    n_true = len(docs)
    pack = {
        "_doc": (
            f"S3 source-grounded pack for {cn} ({cc}), generated by "
            f"generate_world_packs.py (seed namespace '{SEED_NS}', deterministic) "
            f"from the worldwidelaw/legal-sources sample snapshot via "
            f"world-law-catalog.json. {n_true} True items quote title/date/source/"
            f"identifier VERBATIM from real collected documents; {n_true} False "
            f"items are controlled mutations of those same documents (date-shift, "
            f"wrong-source cross-jurisdiction trap, identifier near-miss). "
            f"Bibliographic claims only, no legal doctrine, which is the "
            f"anti-hallucination contract: every True fact exists in the repo, "
            f"every False item is false by construction and its rationale states "
            f"the mutation plus the true fact. tier is the single value 'source' "
            f"(dates here are claim content, not recency probes, so the date-tier "
            f"convention of nl-ecli-tiered.json does not apply). 50/50 True/False "
            f"balance prevents 'always answer X' gaming. See packs/world/README.md."
        ),
        "name": f"S3 — {cn} — Source-Grounded Citation Reliability ({cc})",
        "jurisdiction": cn,
        "version": "1.0",
        "pack_type": "source-grounded",
        "format": "F5-biblio",
        "generated": generated,
        "source_basis": {
            "catalog": "labs/world-law-catalog/world-law-catalog.json",
            "samples": "labs/legal-sources/sources/{CC}/{SourceName}/sample/",
            "repo": "worldwidelaw/legal-sources",
        },
        "prompt_template": (
            "Jurisdiction: [Jurisdiction]. Evaluate the following bibliographic "
            "claim about an official legal source. [Subject - Topic] Answer "
            "True/False with a 20-word explanation as to why."
        ),
        "tests": tests,
        "scoring_notes": {
            "expected_perfect_score": f"{len(tests)}/{len(tests)} across all consistency rounds",
            "balance": f"{n_true} True / {n_true} False",
            "scope": (
                "Citation reliability about sources and documents only "
                "(bibliographic facts). Doctrinal knowledge is NOT tested here; "
                "doctrinal packs (e.g. nl-adjacent-article.json) remain hand-curated."
            ),
        },
    }
    return pack


# --------------------------------------------------------------------- main --

def main():
    ap = argparse.ArgumentParser(description="Generate source-grounded S3 packs for all catalog jurisdictions.")
    ap.add_argument("--catalog", default=CATALOG_PATH)
    ap.add_argument("--sources-root", default=SOURCES_ROOT)
    ap.add_argument("--out", default=OUT_DIR)
    ap.add_argument("--only", help="Comma-separated country codes (e.g. NL,DE).")
    ap.add_argument("--dry-run", action="store_true", help="Stats only, write nothing.")
    args = ap.parse_args()

    with open(args.catalog, encoding="utf-8") as fh:
        catalog = json.load(fh)
    generated = catalog.get("meta", {}).get("generated", "unknown")

    only = {c.strip().upper() for c in args.only.split(",")} if args.only else None
    claimed_pool = build_claimed_pool(catalog)

    stats = Counter()
    manifest, skipped = [], []
    mutation_hist = Counter()
    shape_hist = Counter()

    for cc in sorted(catalog["countries"]):
        if only and cc.upper() not in only:
            continue
        country = catalog["countries"][cc]
        per_source_docs = []
        for src in sorted(country["sources"],
                          key=lambda s: (s.get("priority", 9), s.get("id", ""))):
            if src.get("status") != "complete":
                continue
            if not set(src.get("dataTypes", [])) & DATA_TYPES:
                continue
            sample_dir = os.path.join(args.sources_root, src["id"], "sample")
            if not os.path.isdir(sample_dir):
                stats["sources_no_sample_dir"] += 1
                continue
            docs = load_sample_docs(sample_dir, stats)
            if docs:
                docs.sort(key=lambda d: (d["rec_id"] or "", d["title"]))
                per_source_docs.append((src, docs))
                stats["sources_used"] += 1

        if not per_source_docs:
            skipped.append((cc, "no readable sample docs"))
            continue

        rng = random.Random(f"{SEED_NS}:{cc}")
        pack = build_pack(cc, country, per_source_docs, claimed_pool, generated, rng)
        if pack is None:
            skipped.append((cc, "fewer than %d viable docs" % MIN_DOCS))
            continue

        fname = f"{cc.lower()}-source-grounded.json"
        if not args.dry_run:
            os.makedirs(args.out, exist_ok=True)
            with open(os.path.join(args.out, fname), "w", encoding="utf-8") as fh:
                json.dump(pack, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
        n = len(pack["tests"])
        manifest.append({
            "file": fname,
            "country": cc,
            "countryName": country.get("name", cc),
            "flag": country.get("flag", ""),
            "items": n,
            "generated": generated,
        })
        stats["packs"] += 1
        stats["items"] += n
        stats["true_items"] += sum(1 for t in pack["tests"] if t["expected"])
        stats["false_items"] += sum(1 for t in pack["tests"] if not t["expected"])
        for t in pack["tests"]:
            if not t["expected"]:
                mutation_hist[t["mutation"]] += 1
            shape_hist[t.get("shape", "?")] += 1

    # index.json is only (re)written on a FULL run; an --only subset run would
    # otherwise clobber the manifest down to the subset.
    if not args.dry_run and manifest and not only:
        with open(os.path.join(args.out, "index.json"), "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, ensure_ascii=False)
            fh.write("\n")

    verb = "built (dry-run)" if args.dry_run else "written"
    print(f"Packs {verb}:".ljust(22) + f"{stats['packs']}  ->  {args.out}")
    print(f"Total items:          {stats['items']} "
          f"({stats['true_items']} True / {stats['false_items']} False)")
    print(f"Sources used:         {stats['sources_used']} "
          f"(catalog-complete sources missing a sample dir: {stats['sources_no_sample_dir']})")
    print(f"Unreadable files:     {stats['unreadable_files']}")
    print(f"False-item mutations: {dict(sorted(mutation_hist.items()))}")
    print(f"Statement shapes:     {dict(sorted(shape_hist.items()))}")
    if skipped:
        print(f"Skipped countries ({len(skipped)}): "
              + ", ".join(f"{cc} ({why})" for cc, why in skipped))
    if not args.dry_run and not only:
        print("Manifest:             index.json "
              f"({len(manifest)} packs, generated stamp = catalog meta.generated '{generated}')")
    elif only:
        print("Note: --only run, index.json NOT rewritten (full runs only).")


if __name__ == "__main__":
    main()
