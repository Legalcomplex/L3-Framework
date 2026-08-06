#!/usr/bin/env python3
"""
World Law Catalog builder.

Reads the Legal Data Hunter open-source catalog (labs/legal-sources, a clone of
worldwidelaw/legal-sources) and emits two artifacts:

  world-law-catalog.json       Full catalog: every country, every legislation +
                               case-law source with status/url/license. Consumed
                               by the S3 benchmark generator and the Saga Lab
                               research agent.

  world-law-catalog.slim.json  UI-ready slice: per-country name/flag/counts and
                               the top sources (priority-ranked, max 6). Shipped
                               to legalcomplex `src/lib/legal/` and served via
                               /api/legal/coverage.

Source of truth: legal-sources/docs/status.json (generated from their live DB).
Doctrine-only sources are excluded — the research UI links legislation and
case law; doctrine stays available in the full repo.

Usage: python3 build_catalog.py
"""

import json
import re
from datetime import date
from pathlib import Path

import yaml

LABS = Path(__file__).resolve().parent.parent
STATUS = LABS / "legal-sources" / "docs" / "status.json"
SOURCES_DIR = LABS / "legal-sources" / "sources"
OUT_FULL = Path(__file__).resolve().parent / "world-law-catalog.json"
OUT_SLIM = Path(__file__).resolve().parent / "world-law-catalog.slim.json"

KEEP_TYPES = {"legislation", "case_law"}
MAX_SLIM_SOURCES = 6

# ─── Direct-API extraction (from per-source config.yaml) ─────
# Every collection script documents the OFFICIAL endpoint it reads from
# (e.g. api.lovdata.no for Norway, wetten.sr WP REST for Suriname). We mine
# those into the catalog so adapters and agents call governments directly —
# never a hosted third-party search API.

SEARCHABLE_HINTS = re.compile(
    r"search|[?&]q=|query|zoekterm|searchRetrieve|/wp-json/|delivery/api|filter=|[?&]s=|find",
    re.IGNORECASE,
)

KIND_RULES = [
    (re.compile(r"sru", re.I), "sru"),
    (re.compile(r"sparql", re.I), "sparql"),
    (re.compile(r"graphql", re.I), "graphql"),
    (re.compile(r"rss|feed|atom", re.I), "rss"),
    (re.compile(r"rest|json", re.I), "rest"),
    (re.compile(r"\bapi\b", re.I), "rest"),
    (re.compile(r"bulk|download|ftp|dump", re.I), "bulk"),
    (re.compile(r"sitemap", re.I), "sitemap"),
    (re.compile(r"scrap|html|browser|spa", re.I), "scrape"),
]

DIRECT_KINDS = {"rest", "sru", "sparql", "graphql", "rss", "bulk"}


def classify_kind(api: dict) -> str | None:
    declared = str(api.get("type") or "")
    for pattern, kind in KIND_RULES:
        if pattern.search(declared):
            return kind
    endpoints_text = " ".join(str(v) for v in (api.get("endpoints") or {}).values())
    if "/wp-json/" in endpoints_text:
        return "rest"
    if re.search(r"sitemap", endpoints_text, re.I):
        return "sitemap"
    if api.get("bulk_files"):
        return "bulk"
    fmt = str(api.get("response_format") or "")
    if re.search(r"json|xml", fmt, re.I) and api.get("endpoints"):
        return "rest"
    if api.get("seed_paths"):
        return "scrape"
    return None


def extract_api(source_id: str) -> dict | None:
    """Read the api block from sources/{CC}/{Name}/config.yaml, normalized."""
    cfg_path = SOURCES_DIR / source_id / "config.yaml"
    if not cfg_path.is_file():
        return None
    try:
        cfg = yaml.safe_load(cfg_path.read_text()) or {}
    except Exception:
        return None
    api = cfg.get("api")
    if not isinstance(api, dict):
        return None

    raw_endpoints = api.get("endpoints") or {}
    if isinstance(raw_endpoints, list):
        raw_endpoints = {f"endpoint_{i}": v for i, v in enumerate(raw_endpoints)}
    elif not isinstance(raw_endpoints, dict):
        raw_endpoints = {}
    endpoints = {
        str(k): str(v)[:200]
        for k, v in raw_endpoints.items()
        if v is not None and not isinstance(v, (dict, list))
    }
    kind = classify_kind(api)
    searchable = bool(SEARCHABLE_HINTS.search(" ".join(endpoints.values()))) and kind in DIRECT_KINDS

    cfg_auth = cfg.get("auth")
    auth_value = (
        api.get("auth")
        or (cfg_auth.get("type") if isinstance(cfg_auth, dict) else cfg_auth)
        or "none"
    )
    out = {
        "kind": kind,
        "baseUrl": str(api.get("base_url") or "").strip() or None,
        "auth": str(auth_value).strip() or "none",
        "format": str(api.get("response_format") or "").strip() or None,
        "endpoints": endpoints,
        "searchable": searchable,
    }
    if out["baseUrl"] is None and not endpoints:
        return None
    return out


def iso_flag(code: str) -> str:
    """Compute the emoji flag from a 2-letter ISO code (regional indicators).
    Upstream status.json only carries flags for European countries; the rest
    (67 of 236, e.g. SR, GY, BR) come back empty."""
    if len(code) != 2 or not code.isalpha():
        return ""
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in code.upper())


# ISO-3166 names for the codes upstream leaves as bare codes (name == code).
FALLBACK_NAMES = {
    "AF": "Afghanistan", "AG": "Antigua and Barbuda", "AI": "Anguilla",
    "AS": "American Samoa", "AW": "Aruba", "AX": "Åland Islands",
    "BL": "Saint Barthélemy", "BM": "Bermuda", "BN": "Brunei",
    "BQ": "Caribbean Netherlands", "BT": "Bhutan", "BZ": "Belize",
    "CK": "Cook Islands", "CR": "Costa Rica", "CW": "Curaçao",
    "DM": "Dominica", "FK": "Falkland Islands", "FM": "Micronesia",
    "FO": "Faroe Islands", "GD": "Grenada", "GG": "Guernsey",
    "GI": "Gibraltar", "GL": "Greenland", "GT": "Guatemala", "GU": "Guam",
    "GY": "Guyana", "HK": "Hong Kong", "HN": "Honduras", "IM": "Isle of Man",
    "JE": "Jersey", "KI": "Kiribati", "KN": "Saint Kitts and Nevis",
    "KY": "Cayman Islands", "LC": "Saint Lucia", "MF": "Saint Martin",
    "MH": "Marshall Islands", "MO": "Macao", "MP": "Northern Mariana Islands",
    "MS": "Montserrat", "MV": "Maldives", "NC": "New Caledonia",
    "NF": "Norfolk Island", "NI": "Nicaragua", "NR": "Nauru", "NU": "Niue",
    "PA": "Panama", "PF": "French Polynesia", "PM": "Saint Pierre and Miquelon",
    "PN": "Pitcairn Islands", "PR": "Puerto Rico", "PW": "Palau",
    "SB": "Solomon Islands", "SH": "Saint Helena", "SR": "Suriname",
    "SV": "El Salvador", "SX": "Sint Maarten", "TC": "Turks and Caicos Islands",
    "TL": "Timor-Leste", "TO": "Tonga", "TV": "Tuvalu",
    "VC": "Saint Vincent and the Grenadines", "VG": "British Virgin Islands",
    "VI": "U.S. Virgin Islands", "VU": "Vanuatu", "WF": "Wallis and Futuna",
    "WS": "Samoa",
}


def main() -> None:
    data = json.loads(STATUS.read_text())
    by_country = data["by_country"]
    sources = data["sources"]

    countries: dict[str, dict] = {}
    for code, info in by_country.items():
        name = info["name"]
        if name == code:
            name = FALLBACK_NAMES.get(code, name)
        countries[code] = {
            "code": code,
            "name": name,
            "flag": info.get("flag") or iso_flag(code),
            "sources": [],
        }

    kept = 0
    api_count = 0
    searchable_count = 0
    for s in sources:
        dts = [t for t in (s.get("data_types") or []) if t in KEEP_TYPES]
        if not dts:
            continue
        code = s.get("country")
        if code not in countries:
            countries[code] = {"code": code, "name": code, "flag": "", "sources": []}
        api = extract_api(s["id"])
        if api and api["kind"] in DIRECT_KINDS:
            api_count += 1
            if api["searchable"]:
                searchable_count += 1
        countries[code]["sources"].append({
            "id": s["id"],
            "name": s.get("name") or s["id"],
            "dataTypes": dts,
            "status": s.get("status") or "unknown",
            "url": s.get("url"),
            "auth": s.get("auth") or "none",
            "priority": s.get("priority") if s.get("priority") is not None else 9,
            "preferredFor": s.get("preferred_for") or [],
            "notes": (s.get("notes") or "")[:240],
            "api": api,
        })
        kept += 1

    # Drop countries that ended up with no legislation/case-law sources
    countries = {c: v for c, v in countries.items() if v["sources"]}

    for v in countries.values():
        # Direct APIs first within each status band — they're the adapter candidates
        v["sources"].sort(key=lambda s: (
            s["status"] != "complete",
            not (s.get("api") and s["api"]["kind"] in DIRECT_KINDS),
            s["priority"],
            s["name"],
        ))
        v["counts"] = {
            "total": len(v["sources"]),
            "complete": sum(1 for s in v["sources"] if s["status"] == "complete"),
            "legislation": sum(1 for s in v["sources"] if "legislation" in s["dataTypes"]),
            "caseLaw": sum(1 for s in v["sources"] if "case_law" in s["dataTypes"]),
            "directApis": sum(1 for s in v["sources"] if s.get("api") and s["api"]["kind"] in DIRECT_KINDS),
        }

    meta = {
        "generated": date.today().isoformat(),
        "sourceRepo": "worldwidelaw/legal-sources",
        "sourceGeneratedAt": data.get("generated_at"),
        "countries": len(countries),
        "sources": kept,
        "directApis": api_count,
        "searchableApis": searchable_count,
    }

    full = {"meta": meta, "countries": countries}
    OUT_FULL.write_text(json.dumps(full, ensure_ascii=False, indent=1))

    slim_countries = {}
    for code, v in sorted(countries.items()):
        slim_sources = []
        for s in v["sources"][:MAX_SLIM_SOURCES]:
            entry = {k: s[k] for k in ("id", "name", "dataTypes", "status", "url")}
            if s.get("api") and s["api"]["kind"] in DIRECT_KINDS:
                entry["apiKind"] = s["api"]["kind"]
                if s["api"]["searchable"]:
                    entry["searchable"] = True
            slim_sources.append(entry)
        slim_countries[code] = {
            "name": v["name"],
            "flag": v["flag"],
            "counts": v["counts"],
            "sources": slim_sources,
        }
    slim = {"meta": meta, "countries": slim_countries}
    OUT_SLIM.write_text(json.dumps(slim, ensure_ascii=False, separators=(",", ":")))

    print(f"countries: {meta['countries']}  legislation/case-law sources: {kept}")
    print(f"direct APIs: {api_count} ({searchable_count} searchable)")
    print(f"full: {OUT_FULL} ({OUT_FULL.stat().st_size // 1024} KB)")
    print(f"slim: {OUT_SLIM} ({OUT_SLIM.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
