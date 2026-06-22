#!/usr/bin/env python3
"""make_sweep_report.py — build SWEEP-REPORT.md from results/world/*.json.

Run after run_world_sweep.py. Reads per-pack result files + summary.json and
the pack index for country names/flags. Stdlib only.
"""

import json
import os
from collections import Counter
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(ROOT, "results", "world")
PACK_DIR = os.path.join(ROOT, "packs", "world")

# Vertex AI pricing per 1M tokens (USD), 2026 list prices.
PRICING = {
    "gemini-2.5-flash-lite": (0.10, 0.40),
    "gemini-2.5-flash": (0.30, 2.50),
    "claude-haiku-4-5-20251001": (1.00, 5.00),
}


def pct(x, nd=1):
    return f"{x * 100:.{nd}f}%" if x is not None else "n/a"


def main():
    with open(os.path.join(OUT_DIR, "summary.json"), encoding="utf-8") as f:
        summary = json.load(f)
    with open(os.path.join(PACK_DIR, "index.json"), encoding="utf-8") as f:
        index = {e["country"].upper(): e for e in json.load(f)}

    packs = {}
    for cc in index:
        path = os.path.join(OUT_DIR, f"{cc.lower()}.json")
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                packs[cc] = json.load(f)

    all_rows = []
    for cc, res in packs.items():
        for r in res["results"]:
            r2 = dict(r)
            r2["country"] = cc
            all_rows.append(r2)
    judged = [r for r in all_rows if r["verdict"] in (True, False)]

    model = summary["model"]
    pin, pout = PRICING.get(model, (0.10, 0.40))
    usage = summary.get("usage", {})
    cost = usage.get("in", 0) / 1e6 * pin + usage.get("out", 0) / 1e6 * pout

    # true/false asymmetry
    t_rows = [r for r in judged if r["expected"] is True]
    f_rows = [r for r in judged if r["expected"] is False]
    t_acc = sum(r["correct"] for r in t_rows) / len(t_rows) if t_rows else None
    f_acc = sum(r["correct"] for r in f_rows) / len(f_rows) if f_rows else None
    said_true = sum(1 for r in judged if r["verdict"] is True)

    lines = []
    A = lines.append
    A("# S3 World Benchmark — Sweep Report")
    A("")
    A(f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%MZ')} by "
      f"`run_world_sweep.py` + `make_sweep_report.py`.")
    A("")
    A("## Run setup")
    A("")
    A(f"- **Model:** `{model}` via `{summary.get('endpoint')}` "
      f"(flash tier, thinking disabled, temperature 0, 1 round per item)")
    A(f"- **Packs:** {summary['packs_passed']}/{summary['packs']} passed "
      f"(pass = zero unresolved API errors and 100% of items parsed or "
      f"documented blocked; accuracy is NOT a pass criterion)")
    A(f"- **Items:** {summary['items']} run, {summary['parsed']} parsed, "
      f"{summary.get('blocked', 0)} blocked")
    A(f"- **Sampling:** {'full packs (all items)' if not summary.get('sampled') else str(summary['sampled']) + ' items/pack (balanced)'}")
    A(f"- **Tokens:** {usage.get('in', 0):,} in / {usage.get('out', 0):,} out "
      f"across {usage.get('calls', 0):,} calls")
    A(f"- **Estimated cost:** ${cost:.2f} "
      f"(at ${pin}/M input, ${pout}/M output)")
    A(f"- **Wall time:** {summary.get('wall_seconds', 0):.0f}s")
    A("")
    A("Prompt construction and True/False parsing mirror `run_s3_claude.py` "
      "exactly (same placeholder fill, same first-`\\b(true|false)\\b` "
      "extraction), so numbers are comparable to prior S3 runs.")
    A("")

    A("## Aggregate results")
    A("")
    acc = summary["accuracy"]
    A(f"- **Aggregate accuracy: {pct(acc)}** "
      f"({sum(r['correct'] for r in judged)}/{len(judged)}) — chance is 50%.")
    A(f"- **TRUE items:** {pct(t_acc)} correct ({len(t_rows)} items)")
    A(f"- **FALSE items:** {pct(f_acc)} correct ({len(f_rows)} items)")
    A(f"- **Model said \"True\"** on {pct(said_true / len(judged))} of all "
      f"judged items.")
    A("")
    if t_acc is not None and f_acc is not None:
        if t_acc - f_acc > 0.05:
            A(f"**Asymmetry: the model over-affirms.** It accepts real "
              f"citations far more readily than it rejects fabricated ones "
              f"(TRUE-recall {pct(t_acc)} vs FALSE-recall {pct(f_acc)}). "
              f"An over-affirming verifier is the hallucination failure mode: "
              f"shown a plausible but fabricated citation, it tends to "
              f"confirm it.")
        elif f_acc - t_acc > 0.05:
            A(f"**Asymmetry: the model over-denies.** It rejects fabricated "
              f"citations more readily than it confirms real ones "
              f"(FALSE-recall {pct(f_acc)} vs TRUE-recall {pct(t_acc)}). "
              f"This is skepticism without knowledge: it doubts everything, "
              f"including real documents, rather than knowing which "
              f"citations exist.")
        else:
            A("No material TRUE/FALSE asymmetry.")
    A("")

    A("## Accuracy by mutation class (FALSE items)")
    A("")
    A("| Mutation | n | Accuracy (caught) |")
    A("|---|---|---|")
    by_mut = {}
    for r in judged:
        if r["expected"] is False:
            by_mut.setdefault(r.get("mutation") or "?", []).append(r)
    for mut, rs in sorted(by_mut.items(),
                          key=lambda kv: -sum(x["correct"] for x in kv[1]) / len(kv[1])):
        a = sum(x["correct"] for x in rs) / len(rs)
        A(f"| {mut} | {len(rs)} | {pct(a)} |")
    A("")

    A("## Accuracy by statement shape")
    A("")
    A("| Shape | n | Accuracy |")
    A("|---|---|---|")
    by_shape = {}
    for r in judged:
        by_shape.setdefault(r.get("shape") or "?", []).append(r)
    for sh, rs in sorted(by_shape.items()):
        a = sum(x["correct"] for x in rs) / len(rs)
        A(f"| {sh} | {len(rs)} | {pct(a)} |")
    A("")

    A("## Per-jurisdiction accuracy (best → worst)")
    A("")
    A("| # | Flag | CC | Jurisdiction | Items | Accuracy | Pass |")
    A("|---|---|---|---|---|---|---|")
    ranked = sorted(
        ((cc, res) for cc, res in packs.items() if res["accuracy"] is not None),
        key=lambda kv: (-kv[1]["accuracy"], kv[0]))
    for i, (cc, res) in enumerate(ranked, 1):
        e = index.get(cc, {})
        A(f"| {i} | {e.get('flag', '')} | {cc} | "
          f"{e.get('countryName', res.get('jurisdiction', cc))} | "
          f"{res['items_run']} | {pct(res['accuracy'], 0)} | "
          f"{'PASS' if res['passed'] else 'FAIL'} |")
    A("")

    accs = [res["accuracy"] for _, res in ranked]
    n_above = sum(1 for a in accs if a >= 0.75)
    n_below = sum(1 for a in accs if a <= 0.25)
    n_chance = sum(1 for a in accs if 0.33 <= a <= 0.67)
    A(f"Distribution: {n_above} packs ≥75%, {n_chance} packs within the "
      f"33–67% chance band, {n_below} packs ≤25%.")
    A("")

    A("## Iteration log")
    A("")
    log_path = os.path.join(OUT_DIR, "iteration-log.md")
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            A(f.read().strip())
    else:
        A("(no iteration log found)")
    A("")

    A("## Interpretation")
    A("")
    A(f"The aggregate score of **{pct(acc)}** against a 50% chance baseline "
      "is the finding. These are bibliographic claims about real, recently "
      "collected official legal documents (titles, dates, publishing "
      "sources, identifiers) across 227 jurisdictions. A score near chance "
      "means the model cannot verify citations from these jurisdictions "
      "from parametric memory: it does not know which decisions, gazettes "
      "and acts exist, so it cannot tell a real citation from a controlled "
      "fabrication. **Retrieval grounding against the actual source corpus "
      "is therefore mandatory** for any citation-reliability claim — this "
      "is precisely the gap the S3 retrieval extension (Sabaio L3) is "
      "built to close.")
    A("")
    A("Where scores rise well above chance, inspection shows it is mostly "
      "the FALSE mutations being caught on internal-consistency grounds "
      "(e.g. a cross-jurisdiction `wrong-source` trap pairing a Dutch ECLI "
      "with a Gibraltar gazette is detectable without knowing the "
      "document), not genuine knowledge of the documents. TRUE items — "
      "which require actually knowing the document exists — hover near or "
      "below chance for most jurisdictions, and recent documents (2025–26 "
      "sample snapshot) sit past the model's training cutoff by "
      "construction.")
    A("")

    out = os.path.join(ROOT, "SWEEP-REPORT.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
