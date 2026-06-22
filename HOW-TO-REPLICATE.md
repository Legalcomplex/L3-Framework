# Replicating the S3 world benchmark

S3 tests whether an LLM can tell a real legal citation from a plausibly-fabricated
one — a binary True/False task, graded deterministically, across jurisdictions.
Chance is 50%. The point: models that score near chance cannot self-verify
citations from memory, so citation answers must be retrieval-grounded.

## What's here
- `packs/world/` — 227 source-grounded jurisdiction packs (the test items) + `index.json`.
- `run_world_sweep.py` — sweeps every pack on one model, writes `results/world/` + `summary.json`.
- `run_s3_claude.py` — single-pack runner.
- `make_sweep_report.py` — turns `results/world/` into `SWEEP-REPORT.md`.
- `s3-runner.html` / `serve_s3.py` — a no-build browser runner (paste a key, watch each verdict stream).
- `generate_pack.py` / `generate_world_packs.py` — regenerate packs from source.
- `SWEEP-REPORT*.md` — example reports from reference runs.

## Run a sweep (CLI)
Keys are read from the environment first, then an optional `.env` file
(`S3_ENV_FILE`, default `~/.env.local`). Pick a provider:

```bash
# xAI Grok (OpenAI-compatible)
XAI_API_KEY=...  python3 run_world_sweep.py --provider xai

# Anthropic
ANTHROPIC_API_KEY=...  python3 run_world_sweep.py --provider anthropic

# Google Gemini (Vertex service account or AI Studio key)
python3 run_world_sweep.py --provider gemini

# cheap smoke test: 6 items/pack, two jurisdictions
python3 run_world_sweep.py --provider xai --sample 6 --only nl,de
```

Then build the report:

```bash
python3 make_sweep_report.py   # writes SWEEP-REPORT.md
```

Runs are resumable (per-pack results are cached and skipped on the same model+sampling).

## Run in the browser
Open `s3-runner.html` (or `python3 serve_s3.py 8753`), paste a key, pick a model, Run.

## Reading results
`accuracy` is overall correct/total. The diagnostic is the TRUE/FALSE split: a model
that defaults to "False" scores high on FALSE items and near-zero on TRUE items
(real citations it can't confirm) — that's the citation-reliability gap S3 surfaces.
