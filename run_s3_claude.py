#!/usr/bin/env python3
"""
run_s3_claude.py — S3-Framework runner for Claude models (default: Fable 5).

The upstream S3 Streamlit app (app.py) is OpenAI-only (ask_openai()). This is a
standalone, Anthropic-SDK equivalent so the same True/False legal-citation packs
can be run against Claude models — primarily claude-fable-5.

What it does (mirrors app.py's evaluate_once + evaluate_consistency):
  1. Loads an S3 JSON pack (sample-tests-dutch-law.json or packs/*.json)
  2. Fills the pack's prompt_template from each item's fields
  3. Calls the model N rounds per item
  4. Parses True/False, scores accuracy, and measures cross-round consistency
  5. Slices accuracy by `tier` when present (the recency pillar)
  6. Writes per-round results to JSON + CSV and prints a summary

FABLE 5 NOTE — temperature is removed on Fable 5 (and Opus 4.7+): sending it
returns 400. S3's classic "temperature 0" cannot be honored. Consistency is still
measured across rounds; it just reflects the model's natural behavior rather than
a forced-deterministic setting. `thinking` is omitted (zero-shot knowledge probe;
an explicit `disabled` also 400s on Fable 5).

Usage:
  export ANTHROPIC_API_KEY=sk-ant-...
  python run_s3_claude.py sample-tests-dutch-law.json
  python run_s3_claude.py packs/nl-ecli-tiered.json --rounds 3 --model claude-fable-5
  python run_s3_claude.py sample-tests-dutch-law.json --dry-run   # print prompts, no API calls
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone

MODEL_DEFAULT = "claude-fable-5"

# Map template placeholders -> item field names. Both the statutory template
# ("[Code name] [Reference type] [Number]") and the ECLI template
# ("[Code][Reference][Number]") draw from the same fields.
PLACEHOLDERS = {
    "[Jurisdiction]": "jurisdiction",
    "[Code name]": "code",
    "[Code]": "code",
    "[Reference type]": "reference",
    "[Reference]": "reference",
    "[Number]": "number",
    "[Subject - Topic]": "topic",
    "[Topic]": "topic",
}

_TF = re.compile(r"\b(true|false)\b", re.IGNORECASE)


def build_prompt(template, item, pack_jurisdiction):
    out = template
    for ph, field in PLACEHOLDERS.items():
        if ph not in out:
            continue
        val = item.get(field)
        if field == "jurisdiction" and not val:
            val = pack_jurisdiction
        val = "" if val is None else str(val)
        # When a value is empty (e.g. statutory items have no [Number]), also
        # drop one leading space so we don't leave "artikel 74 '".
        if val == "":
            out = out.replace(" " + ph, ph)
        out = out.replace(ph, val)
    return re.sub(r"\s+", " ", out).strip()


def parse_true_false(text):
    """Return True / False / None (unparseable). The template asks the model to
    lead with True/False, so the first word-boundary match is reliable."""
    if not text:
        return None
    m = _TF.search(text)
    if not m:
        return None
    return m.group(1).lower() == "true"


def call_model(client, model, prompt, max_tokens):
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
        # No temperature / top_p / top_k — removed on Fable 5 (400 if sent).
        # No thinking param — omitted on purpose (disabled also 400s on Fable 5).
    )
    parts = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    return "".join(parts).strip()


def call_with_retry(client, model, prompt, max_tokens, retries=3):
    import anthropic
    delay = 2.0
    for attempt in range(retries):
        try:
            return call_model(client, model, prompt, max_tokens)
        except anthropic.RateLimitError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay *= 2
        except anthropic.APIStatusError as e:
            if getattr(e, "status_code", 0) >= 500 and attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                raise


def run(args):
    with open(args.pack, encoding="utf-8") as f:
        pack = json.load(f)

    template = pack.get("prompt_template")
    if not template:
        sys.exit(f"Pack {args.pack} has no prompt_template.")
    pack_jur = pack.get("jurisdiction", "")
    tests = pack.get("tests", [])
    if not tests:
        sys.exit(f"Pack {args.pack} has no tests.")

    print(f"Pack:   {pack.get('name', args.pack)}  ({len(tests)} items)")
    print(f"Model:  {args.model}")
    print(f"Rounds: {args.rounds}   max_tokens: {args.max_tokens}   "
          f"dry_run: {args.dry_run}\n")

    client = None
    if not args.dry_run:
        import anthropic
        if not os.environ.get("ANTHROPIC_API_KEY"):
            sys.exit("ANTHROPIC_API_KEY not set. Export it, or use --dry-run.")
        client = anthropic.Anthropic()

    rows = []          # one row per (item, round)
    per_item = {}      # id -> list of parsed answers across rounds

    for item in tests:
        item_id = item.get("id")
        # Per-item prompt_template overrides the pack default (used by the
        # direction-asymmetry pack: F2 items carry their own template).
        prompt = build_prompt(item.get("prompt_template") or template, item, pack_jur)
        expected = item.get("expected")
        answers = []

        if args.dry_run:
            print(f"[{item_id}] {prompt}")
            continue

        for rnd in range(1, args.rounds + 1):
            raw = call_with_retry(client, args.model, prompt, args.max_tokens)
            parsed = parse_true_false(raw)
            answers.append(parsed)
            rows.append({
                "id": item_id,
                "tier": item.get("tier", ""),
                "round": rnd,
                "expected": expected,
                "parsed": parsed,
                "correct": (parsed == expected) if parsed is not None else False,
                "raw": raw.replace("\n", " ").strip(),
            })
            time.sleep(args.delay)

        per_item[item_id] = answers
        modal = Counter(a for a in answers if a is not None).most_common(1)
        modal_ans = modal[0][0] if modal else None
        agree = sum(1 for a in answers if a == modal_ans)
        consistency = agree / len(answers) if answers else 0.0
        correct_rounds = sum(1 for a in answers if a == expected)
        print(f"[{item_id}] expected={expected!s:<5} "
              f"answers={answers} "
              f"acc={correct_rounds}/{args.rounds} "
              f"consistency={consistency:.0%}")

    if args.dry_run:
        print(f"\n{len(tests)} prompts built. No API calls made.")
        return

    summarize(pack, args, rows, per_item, tests)
    write_outputs(pack, args, rows)


def summarize(pack, args, rows, per_item, tests):
    n_items = len(tests)
    total_rounds = len(rows)
    correct = sum(1 for r in rows if r["correct"])
    unparsed = sum(1 for r in rows if r["parsed"] is None)

    # Per-item consistency (% of rounds matching the modal answer).
    consistencies = []
    for answers in per_item.values():
        modal = Counter(a for a in answers if a is not None).most_common(1)
        modal_ans = modal[0][0] if modal else None
        agree = sum(1 for a in answers if a == modal_ans)
        consistencies.append(agree / len(answers) if answers else 0.0)
    mean_consistency = sum(consistencies) / len(consistencies) if consistencies else 0.0
    perfect = sum(1 for c in consistencies if c == 1.0)

    print("\n" + "=" * 56)
    print("SUMMARY")
    print("=" * 56)
    print(f"Accuracy (round-level):   {correct}/{total_rounds} "
          f"({correct / total_rounds:.1%})")
    print(f"Mean consistency:         {mean_consistency:.1%} "
          f"({perfect}/{n_items} items unanimous)")
    if unparsed:
        print(f"Unparseable answers:      {unparsed}/{total_rounds}")

    # Recency pillar: accuracy by tier, when the pack carries tiers.
    tiers = sorted({r["tier"] for r in rows if r["tier"]})
    if tiers:
        print("\nAccuracy by tier (recency pillar):")
        for t in tiers:
            tr = [r for r in rows if r["tier"] == t]
            tc = sum(1 for r in tr if r["correct"])
            print(f"  {t:<18} {tc}/{len(tr)} ({tc / len(tr):.0%})")

    print("\nNote: Fable 5 ignores temperature (removed) — consistency above")
    print("reflects the model's natural behavior, not a forced temp=0 setting.")


def write_outputs(pack, args, rows):
    os.makedirs(args.out, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = os.path.splitext(os.path.basename(args.pack))[0]
    tag = f"{base}__{args.model}__{stamp}"

    json_path = os.path.join(args.out, f"{tag}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "pack": pack.get("name", args.pack),
            "pack_file": args.pack,
            "model": args.model,
            "rounds": args.rounds,
            "run_at": stamp,
            "results": rows,
        }, f, indent=2, ensure_ascii=False)

    csv_path = os.path.join(args.out, f"{tag}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f, fieldnames=["id", "tier", "round", "expected", "parsed", "correct", "raw"])
        w.writeheader()
        w.writerows(rows)

    print(f"\nWrote {json_path}")
    print(f"Wrote {csv_path}")


def main():
    p = argparse.ArgumentParser(description="Run an S3 pack against a Claude model (default Fable 5).")
    p.add_argument("pack", help="Path to an S3 JSON test pack.")
    p.add_argument("--model", default=MODEL_DEFAULT, help=f"Model id (default {MODEL_DEFAULT}).")
    p.add_argument("--rounds", type=int, default=3, help="Consistency rounds per item (default 3).")
    p.add_argument("--max-tokens", type=int, default=150, help="Max output tokens per call (default 150).")
    p.add_argument("--delay", type=float, default=0.15, help="Inter-call delay seconds (default 0.15).")
    p.add_argument("--out", default="results", help="Output directory (default ./results).")
    p.add_argument("--dry-run", action="store_true", help="Build and print prompts; make no API calls.")
    run(p.parse_args())


if __name__ == "__main__":
    main()
