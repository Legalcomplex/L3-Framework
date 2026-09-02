# S3-Framework

**Legal LLM evaluation that tests deficiency, not proficiency.**

S3 asks a language model one narrow, objectively gradeable question: can it tell a
real legal citation from a plausibly fabricated one, from memory, with no retrieval?

Half the items are true bibliographic statements about real, recently collected
official legal documents (title, publishing source, date, identifier). The other
half are the same statements with exactly one controlled mutation: a wrong source,
a mutated identifier, or a shifted date. The model answers true or false in a
single call. Grading is exact match on the first `true`/`false` token, so there is
no judge model and no scoring discretion.

**Chance is 50%.**

## The finding

Four models, two providers, full 2,716-item sweeps across 227 jurisdiction packs,
no retrieval and no web access, temperature 0, one round, thinking disabled:

| Model | Provider | Run date | Aggregate | TRUE items | FALSE items | Said "true" |
|---|---|---|---|---|---|---|
| Claude Opus 4.8 | Anthropic | 2026-07-19 | **52.6%** | 7.4% | 97.6% | 4.9% |
| Claude Haiku 4.5 | Anthropic | 2026-07-19 | **52.3%** | 6.6% | 98.0% | 4.3% |
| Grok 4.1 Fast (non-reasoning) | xAI | 2026-06-20 | **51.9%** | 5.8% | 98.1% | 3.9% |
| Claude Sonnet 5 | Anthropic | 2026-07-19 | **50.5%** | 1.5% | 99.5% | 1.0% |

Every arm lands within roughly two points of chance, and the aggregate is the least
interesting number in the table. The TRUE/FALSE split is the result:

**These models reject fabricated citations almost perfectly and confirm almost no
real ones.** A model that answered "false" to every item would score about 50%.
Three of these four sit within two points of that strategy, and Sonnet 5 is within
half a point of it, because it says "true" only 1.0% of the time.

Two things follow. Scale does not fix it: the frontier arm and the fast arm are
0.3pp apart, and the mid-tier arm is the *worst* here precisely because it is the
most sceptical. And a low score is a score for unaided model memory, not for a
legal AI product. It is the argument for grounding citation answers in retrieval,
which is what this benchmark exists to justify.

### Which mutation gets caught

Accuracy on the FALSE half, broken out by how each item was corrupted:

| Mutation | Opus 4.8 | Haiku 4.5 | Grok 4.1 Fast | Sonnet 5 |
|---|---|---|---|---|
| `wrong-source` | 100% | 100% | 100% | 100% |
| `id-mutation` | 99.1% | 98.7% | 97.9% | 99.6% |
| `date-shift` | 92.5% | 94.1% | 94.8% | 98.5% |

Attributing a document to the wrong publishing body is caught every time by every
model. A shifted date is the one that gets through. This near-perfect rejection is
also what *produces* the near-chance aggregate, given how rarely any of them will
confirm a citation that is genuinely real.

## Why measure deficiency

Legal proficiency benchmarks are hard to make honest. Law varies by jurisdiction,
language and culture; many legal tasks are subjective enough that competent lawyers
disagree; and any proficiency test can eventually be trained against. S3 sidesteps
that by testing three foundational properties that are objectively measurable and
harder to game: citation accuracy, recency, and consistency on repeated objective
prompts.

Scope is deliberately narrow. It tests instruct-tuned raw models, not vendor
products or RAG applications, and it does not test summarisation, drafting or legal
reasoning. See [`Introduction.md`](Introduction.md) for the full rationale and FAQ.

## Repository layout

```
packs/world/              227 source-grounded jurisdiction packs (the test items) + index.json
results/                  per-run outputs and summary.json
data/                     source material the packs are generated from
manifest.json             machine-readable contract: every published run, with model and date
run_world_sweep.py        sweep every pack on one model
run_s3_claude.py          single-pack runner
generate_pack.py          regenerate one pack from source
generate_world_packs.py   regenerate all world packs
make_sweep_report.py      turn results/world/ into a SWEEP-REPORT
s3-runner.html            no-build browser runner
serve_s3.py               local server for the browser runner
```

## Quickstart

Requires Python 3.8+ and `pip install -r requirements.txt`. Keys are read from the
environment first, then an optional `.env` file (`S3_ENV_FILE`, default `~/.env.local`).

```bash
# cheap smoke test: 6 items per pack, two jurisdictions
python3 run_world_sweep.py --provider xai --sample 6 --only nl,de

# full sweep
XAI_API_KEY=...        python3 run_world_sweep.py --provider xai
ANTHROPIC_API_KEY=...  python3 run_world_sweep.py --provider anthropic
python3 run_world_sweep.py --provider gemini   # Vertex service account or AI Studio key

# build the report
python3 make_sweep_report.py
```

Runs are resumable: per-pack results are cached and skipped for the same model and
sampling mode. Or open `s3-runner.html` (or run `python3 serve_s3.py 8753`), paste a
key, pick a model, and watch each verdict stream.

Full instructions, including how to read a result, are in
[`HOW-TO-REPLICATE.md`](HOW-TO-REPLICATE.md).

## Reproducibility

`manifest.json` is the single source of truth for every published figure. Each run
records its model id, provider, run date, item count, the framework commit it ran
at, token usage and cost. Quote numbers from the manifest with the model and date
attached, never from a report file in isolation: the reports are per-model
snapshots, and one model's numbers say nothing about another's.

Per-run reports are `SWEEP-REPORT-<model>-<date>.md`. Benchmark design notes are in
[`WORLD-CITATION-BENCHMARK.md`](WORLD-CITATION-BENCHMARK.md), and a worked
walkthrough is in [`DEMO.md`](DEMO.md).

## Contributing

New jurisdiction packs are the most useful contribution, especially outside the
Anglophone common-law world, which is where this kind of benchmarking is thinnest.
Packs are generated from official sources rather than written by hand; start from
`generate_pack.py`. Issues and pull requests welcome.

## Background

S3 came out of building retrieval-grounded legal research at
[Legalcomplex](https://legalcomplex.com), where the practical question was whether a
newer model was actually more reliable than an older one on the task that matters
for legal citation. It is published as a counterpoint to benchmarks that measure
human-style cognition: foundational reliability is simpler than that, and easier to
check.

## Licence

MIT. See [`LICENSE`](LICENSE).
