# S3 World Packs: source-grounded citation-reliability tests for every catalog jurisdiction

Auto-generated True/False packs, one per jurisdiction, grounded in **real documents
collected from live official sources** (the `worldwidelaw/legal-sources` sample
snapshot, indexed by `labs/world-law-catalog/world-law-catalog.json`).

Generated: 227 jurisdictions, 2,716 items (1,358 True / 1,358 False), by
`../../generate_world_packs.py`. The `generated` stamp in every pack and in
`index.json` is the catalog's `meta.generated` date (not wall clock), so a
regeneration against the same snapshot is byte-identical.

## Methodology: source-grounded generation

Every country in the catalog with at least one `status="complete"` legislation or
case_law source that has readable sample documents on disk
(`labs/legal-sources/sources/{CC}/{SourceName}/sample/*.json`) gets a pack of up
to 12 items (fewer where samples are thin; countries with fewer than 4 viable
items are skipped).

**True items (up to 6)** quote title, date, publishing source, and identifier
VERBATIM from a real collected record, in one of three surface shapes:

- S1 (legislation/other): `'{title}' was published via {source name} ({date}).`
- S2 (case law): `Decision '{title}' ({date}) is published by {source name}.`
- S3 (identifier): `In the collection of {source name}, identifier '{id}' corresponds to '{title}' ({date}).`

Long titles are truncated at a word boundary (marker: `…`) but kept long enough
to stay uniquely identifying; the full title is preserved in the item's
`doc_title` field. Original-language titles stay verbatim inside the quotes.

**False items (same count, 50/50 balance)** are controlled mutations of those
SAME real documents. Each item's `mutation` field names the class and its
`rationale` states both the mutation and the true fact:

1. `date-shift`: the recorded date, shifted by 1 to 3 years (never into the
   future). Docs whose title embeds the year are steered away from this class
   so the contradiction is not visible inside the statement itself.
2. `wrong-source`: the document attributed to a REAL official source of a
   different country in the same region (the cross-jurisdiction trap, the
   world-scale sibling of `../cross-jurisdiction.json`). Claimed sources are
   preferentially same-data-type, catalog-priority-1 national sources, so the
   trap is plausible.
3. `id-mutation`: the last digit group of the real identifier incremented
   (`ECLI:NL:RBOBR:2026:1087` becomes `:1088`). The claim binds the mutated
   identifier to the real title, so it stays false even if the mutated
   identifier happens to exist for some other document.

All three FALSE shapes mirror TRUE shapes, so surface form never gives the
answer away (no "statements with identifiers are always False" shortcut).

## Anti-hallucination guarantee

These packs make **no legal doctrine claims**. There is nothing of the form
"Article X says Y" or "case Z held W". Statements only bind bibliographic facts
that were read from a collected document: its title, its recorded date, the
official source that published it, and its identifier. Every True fact exists in
the repo snapshot; every False item is false by construction relative to that
snapshot, and its rationale records the truth. `verify_status` is `high`
throughout for exactly that reason: True items are repo-grounded, False items
are false-by-construction.

Safety guards in the generator:

- Duplicate ("generic") titles within a country pool (standard Japanese
  case-type names, one decision collected by two sources) and short undated
  boilerplate titles ("THE REPUBLIC OF KENYA") are only used with an identifier
  binding, never for date-shift or wrong-source traps, because the live source
  may hold many documents under the same heading.
- Wrong-source claims are always cross-country, never same-country (official
  gazettes sometimes do publish court decision formulas, so same-country
  cross-type attribution is not reliably false). Known multi-jurisdiction
  aggregators (BAILII, CourtListener, OpenJur, Juricaf, the LII family, ...)
  are excluded from the claimed side, and the claimed source never shares a
  root domain with the true source.
- Identifiers are only taken from official-looking fields (ecli,
  neutral_citation, case_number, doc_id, ...; 4+ chars with digits); bare row
  indexes are rejected. Mutated identifiers avoid colliding with any
  identifier seen in the country pool (best effort; a collision would still be
  false, see above).

## Ground truth caveat

Truth is defined **relative to the collected sample snapshot**. Live sources
move: a consolidated-legislation portal can re-version a law under a new date.
Each item carries `doc_url`, `doc_date`, `doc_identifier` and `source_id` so any
item can be re-verified against the live source; the date-shift class prefers
court decisions (single-valued dates) over legislation effective dates where
the pack's source mix allows it.

## Schema notes

Same item schema as the hand-curated packs (`id`, `jurisdiction`, `code`,
`reference`, `number`, `topic`, `expected`, `verify_status`, `rationale`, plus
additive metadata). The full claim sentence lives in `topic` and the pack-level
`prompt_template` only uses the `[Jurisdiction]` and `[Subject - Topic]`
placeholders, so both runners work unmodified.

**Tier convention:** existing packs use date-based tiers (`T1-established` /
`T2-uncertain` / `T3-post-cutoff`) as a recency probe. Here, dates are claim
CONTENT, not recency probes, so every item carries the single tier value
`source`. The runner's per-tier chart will show one bar for these packs; slice
by the `mutation` and `shape` fields instead when analyzing failures.

## How to regenerate

```bash
cd labs/benchmarks/s3-framework
python3 generate_world_packs.py              # all packs + index.json
python3 generate_world_packs.py --only NL,DE # subset (index.json untouched)
python3 generate_world_packs.py --dry-run    # stats only
```

Python 3 stdlib only (config.yaml files are not read, so pyyaml is not needed).
Output is deterministic: per-country `random.Random("s3-world-v1:{CC}")` seeds,
sorted iteration everywhere. Existing pack files are overwritten in place;
`index.json` is only rewritten on a full run so an `--only` run cannot clobber
the manifest.

## How to run them

- **Browser:** `python3 serve_s3.py` then open `s3-runner.html`. The pack picker
  loads `packs/world/index.json` at startup and lists every jurisdiction under
  "World — source-grounded" (silently absent if the manifest is missing).
  Deep-link: `s3-runner.html?pack=packs/world/nl-source-grounded.json`.
- **CLI:** `python3 run_s3_claude.py packs/world/nl-source-grounded.json --rounds 3`
  (add `--dry-run` to inspect prompts without API calls).

## Limitation (read before citing results)

These packs test **citation reliability about sources and documents**: can the
model tell real bibliographic facts from near-miss fabrications about official
legal publications? They do NOT test doctrinal knowledge (what the law says).
Doctrinal packs such as `../nl-adjacent-article.json` and
`../nl-direction-asymmetry.json` remain hand-curated, verified by a human
against the primary source. Use the world packs as the wide cheap smoke test,
and the curated packs as the deep probe.
