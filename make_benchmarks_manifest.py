#!/usr/bin/env python3
"""make_benchmarks_manifest.py — build (or extend) the machine-readable
manifest that the public /benchmarks page reads.

Number-hygiene contract: every published figure must be traceable to a run
that actually happened. So the manifest carries no free-floating numbers —
each accuracy, rate, token count and cost sits inside a `runs[]` entry that
also carries the model id, provider, run date, s3-framework sha, sampling
mode and the report path. A renderer walking `runs[]` cannot display a number
without also holding the run that produced it. There is deliberately NO
cross-run aggregate: the models share one measurement condition but they are
separate measurements, and averaging them would mint a figure with no run
behind it.

Every number below is READ from the run's own summary.json and per-pack
files. Nothing is passed in by hand except the model id, the provider, the
results directory and the sampling label.

Usage:
  python3 make_benchmarks_manifest.py \
      --merge-into ../../legalcomplex/src/data/benchmarks/manifest.json \
      --run claude-opus-4-8:anthropic:world-claude-opus-4-8-2026-07-19:full \
      --out results/benchmarks-manifest.json

`--merge-into` reads an existing manifest and keeps its `benchmark`,
`receipts` and any runs this invocation does not re-generate (matched on
run id), so re-running one model never drops another model's row. That
overwrite is exactly how the 2026 stale-number confusion started.

Each --run is  model_id:provider:results_dir[:sampling_mode]  (sampling
defaults to "full"). Use "full" ONLY for a complete sweep of every item;
a sampled run must say so (e.g. "stratified-600") because the page renders
that label next to the score.

Stdlib only.
"""

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
PACK_DIR = os.path.join(ROOT, "packs", "world")

# List price per 1M tokens (USD) in effect on the run date. Cost is derived
# from the run's MEASURED token counts, never projected from item counts.
PRICING = {
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-sonnet-5": (2.00, 10.00),   # introductory rate through 2026-08-31
    "claude-opus-4-8": (5.00, 25.00),
    "grok-4-1-fast-non-reasoning": (0.10, 0.40),
}

LABELS = {
    "claude-haiku-4-5": "Claude Haiku 4.5",
    "claude-sonnet-5": "Claude Sonnet 5",
    "claude-opus-4-8": "Claude Opus 4.8",
    "grok-4-1-fast-non-reasoning": "Grok 4.1 Fast (non-reasoning)",
}

NOTES = {
    "claude-haiku-4-5": ("Fast tier. Same no-thinking, temperature-0, "
                         "one-round condition as every other arm."),
    "claude-sonnet-5": ("Mid tier. Thinking explicitly disabled: it is on by "
                        "default on this model, and with a small output "
                        "budget the whole budget can go to thinking, "
                        "returning empty text that scores as no answer."),
    "claude-opus-4-8": ("Frontier tier, run so the finding cannot be dismissed "
                        "as a small-model result. Thinking disabled to hold "
                        "the condition identical across arms."),
}


def short_sha():
    try:
        return subprocess.run(
            ["git", "-C", ROOT, "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def pct(x, nd=1):
    return round(x * 100, nd) if x is not None else None


def load_run(model, provider, results_dir, sampling):
    out_dir = (results_dir if os.path.isabs(results_dir)
               else os.path.join(ROOT, "results", results_dir))
    with open(os.path.join(out_dir, "summary.json"), encoding="utf-8") as f:
        summary = json.load(f)
    with open(os.path.join(PACK_DIR, "index.json"), encoding="utf-8") as f:
        index = {e["country"].upper(): e for e in json.load(f)}

    rows, per_jur = [], []
    for cc, entry in sorted(index.items()):
        path = os.path.join(out_dir, f"{cc.lower()}.json")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            res = json.load(f)
        rows.extend(res["results"])
        per_jur.append({
            "flag": entry.get("flag"),
            "cc": cc,
            "jurisdiction": entry.get("countryName"),
            "items": res["items_run"],
            "accuracyPct": pct(res["accuracy"], 0),
            "pass": res["passed"],
        })
    per_jur.sort(key=lambda r: (-(r["accuracyPct"] or 0), r["cc"]))
    for i, r in enumerate(per_jur, 1):
        r["rank"] = i
    per_jur = [{"rank": r.pop("rank"), **r} for r in per_jur]

    judged = [r for r in rows if r["verdict"] in (True, False)]
    unparsed = [r for r in rows if r["verdict"] is None]

    def acc(subset):
        return (sum(r["correct"] for r in subset) / len(subset)
                if subset else None)

    t_rows = [r for r in judged if r["expected"] is True]
    f_rows = [r for r in judged if r["expected"] is False]

    def grouped(field, key):
        out = {}
        for r in judged:
            out.setdefault(str(r.get(field)), []).append(r)
        return [{key: k, "n": len(v), "accuracyPct": pct(acc(v))}
                for k, v in out.items() if k != "None"]

    usage = summary.get("usage", {}) or {}
    tin, tout = usage.get("in", 0), usage.get("out", 0)
    pin, pout = PRICING.get(model, (None, None))
    cost = (round(tin / 1e6 * pin + tout / 1e6 * pout, 2)
            if pin is not None else None)
    run_date = summary["timestamp"][:10]

    return {
        "id": f"{model}-{run_date}",
        "modelId": model,
        "modelLabel": LABELS.get(model, model),
        "provider": provider,
        "runDate": run_date,
        "s3FrameworkSha": short_sha(),
        "packsRun": summary["packs"],
        "packsTotal": len(index),
        "itemCount": len(rows),
        "samplingMode": sampling,
        "aggregateAccuracyPct": pct(acc(judged)),
        "trueAccuracyPct": pct(acc(t_rows)),
        "falseAccuracyPct": pct(acc(f_rows)),
        "trueItemCount": len(t_rows),
        "falseItemCount": len(f_rows),
        "saidTruePct": pct(sum(1 for r in judged if r["verdict"] is True)
                           / len(judged)) if judged else None,
        # Optional, added by the analysis run: an item where the model
        # answered neither true nor false (e.g. "I cannot verify this without
        # access to the official database"). Excluded from every accuracy
        # above, so it is surfaced here rather than folded silently into a
        # score. judgedCount + unparsedCount == itemCount.
        "judgedCount": len(judged),
        "unparsedCount": len(unparsed),
        "tokensIn": tin,
        "tokensOut": tout,
        "estimatedCostUsd": cost,
        "wallTimeSeconds": (round(summary["wall_seconds"])
                            if summary.get("wall_seconds") else None),
        "notes": NOTES.get(model),
        "reportPath": (f"labs/benchmarks/s3-framework/"
                       f"SWEEP-REPORT-{model}-{run_date}.md"),
        "mutationAccuracy": grouped("mutation", "mutation"),
        "shapeAccuracy": grouped("shape", "shape"),
        "perJurisdiction": per_jur,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="append", default=[],
                    help="model:provider:results_dir[:sampling_mode]")
    ap.add_argument("--merge-into", default="",
                    help="Existing manifest to extend (keeps its benchmark "
                         "block, receipts and any runs not regenerated here).")
    ap.add_argument("--out", action="append", default=[],
                    help="Output path (repeatable).")
    args = ap.parse_args()

    base = {}
    if args.merge_into and os.path.exists(args.merge_into):
        with open(args.merge_into, encoding="utf-8") as f:
            base = json.load(f)

    new_runs = []
    for spec in args.run:
        parts = spec.split(":")
        if len(parts) == 3:
            parts.append("full")
        new_runs.append(load_run(*parts))

    new_ids = {r["id"] for r in new_runs}
    runs = [r for r in base.get("runs", []) if r["id"] not in new_ids]
    runs.extend(new_runs)
    # Best score first; a tie keeps the earlier run date first.
    runs.sort(key=lambda r: (-(r.get("aggregateAccuracyPct") or 0),
                             r.get("runDate") or ""))

    primaries = [r for r in runs if r.get("isPrimary")]
    if len(primaries) > 1:
        raise SystemExit(f"more than one isPrimary run: "
                         f"{[r['id'] for r in primaries]}")

    manifest = dict(base)
    manifest["manifestVersion"] = base.get("manifestVersion", 1)
    manifest["generatedAt"] = datetime.now(timezone.utc).isoformat()
    manifest["runs"] = runs
    manifest.setdefault("receipts", [])

    for out in args.out:
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=1, ensure_ascii=False)
            f.write("\n")
        print(f"Wrote {out} ({len(runs)} runs)")


if __name__ == "__main__":
    main()
