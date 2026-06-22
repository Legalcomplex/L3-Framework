# Sabaio S3 — Friday demo runbook

A ~7-minute live walkthrough of the S3 legal-LLM eval. The story: **S3 catches where a
model breaks on legal citations — cheaply, deterministically, and across jurisdictions.**

---

## Pre-flight (do this 5 min before)

- [ ] **Start the server:** `python serve_s3.py` (from the `s3-framework/` folder) → leave it running on `http://localhost:8753`.
- [ ] **Open** `http://localhost:8753/s3-runner.html` in a browser.
- [ ] **Paste your Anthropic API key** into the key field (stored in localStorage; do this off-screen).
- [ ] **Pick the pack:** Test pack → **Case Law — Tiered by date (30)**. Confirm the line under the dropdown reads *"S3 — NL Case Law (ECLI) — Tiered by Date · 30 items."*
- [ ] **Pick speed:** for a snappy live run set **Rounds = 1** (30 calls, ~30–60s). Keep model `claude-fable-5` (the headline) — or `claude-haiku-4-5` if the room's bandwidth is slow.
- [ ] **Warm-up run (optional but recommended):** do one full run *before* the audience arrives so it's also sitting in **Run history** as a fallback if live networking flakes.
- [ ] Have the **Background** and **Pack generator** tabs ready (header links).

---

## The flow (with talking points)

**1. Frame it (30s).** "Most legal benchmarks measure what a model does *well*. S3 measures where it *breaks* — can it reliably tell whether a real Dutch Supreme Court case is about the topic claimed? Binary True/False, deterministic, no LLM judge."

**2. Show one question (30s).** Point at a row: *"is ECLI:NL:HR:1965:AB7079 a case about gevaarzetting?"* "These are real ECLI case numbers, verified against rechtspraak.nl. Some are **false twins** — a real case paired with the wrong topic — and the post-cutoff tier even has **fabricated** ECLIs to catch hallucination."

**3. Run it live (90s).** Hit **▶ Run evaluation**. Talk over the **Live model trace** as it streams — each question, the model's answer, the ✓/✗ verdict. "You're watching it decide in real time."

**4. Read the scoreboard (60s).** When it finishes: **Accuracy**, **Mean consistency**, **Unparseable**, and **Est. cost** (point out it's well under a dollar). Then the **Accuracy-by-tier** chart: "This is the payoff — the curve from T1 landmarks → T2 recent → T3 post-cutoff is the model's effective legal-knowledge frontier. A flat curve means it's guessing."

**5. Explain the failures (60s).** Click **✦ Explain fails (Sonnet)**. "For just the items it got wrong, a second model — Sonnet — explains why, grounded in our verified rationale so it can't hallucinate. Watch it skip everything that passed." Expand a failed row's drawer.

**6. Generate a pack live (60s).** Open the **Pack generator** page. Set Popular 3 / Obscure 5, click Generate. "This pulls *real* rulings live from rechtspraak.nl — popular landmarks vs. obscure cases — and every ECLI is fetched at build time, so it physically can't invent one. That discipline already caught a transposed digit in a famous case's number." → click **Open in the S3 runner**.

**7. Close on credibility (30s).** Open **Background**. "S3 is the cheap smoke-test you run *first* — if a model fails foundational citation reliability in your jurisdiction, no RAG or fine-tuning saves it downstream. The expensive benches come after."

---

## The credibility highlight (use if asked "how do you know the answers are right?")

> Every ECLI was confirmed on rechtspraak.nl. The process caught two real errors in our
> own data: **Quint/Te Poel** had a non-existent number (`BG9445` → corrected to the real
> `AI1600`), and **Lindenbaum/Cohen** had a transposed digit (`AG1786` → `AG1776`). The
> generator's "fetch-or-skip" rule surfaced the second one automatically. We never cite an
> ECLI we haven't verified — `verify_status: needs_check` means *unverified*.

Bonus domain nugget: *"wanprestatie"* doesn't appear in the Dutch Civil Code at all (the
statute says *tekortkoming*) — it's a doctrinal term. S3's packs are written to know the
difference.

---

## Fallbacks (if something breaks)

| Problem | Fallback |
|---|---|
| API key / network fails live | Show the pre-run result from **Run history** (download its JSON live). |
| Server won't start | Double-click `s3-runner.html` — the **embedded Sample pack** runs offline (statutory, no ECLIs, but proves the flow). |
| Run too slow for the room | Drop **Rounds to 1**, or switch model to `claude-haiku-4-5`. |
| Don't want to spend live | `python run_s3_claude.py packs/nl-ecli-tiered.json --dry-run` prints the 30 questions with no API calls. |

---

## One-line takeaways to land

- **Deterministic & cheap** — string-match grading, a full run is well under $0.50.
- **Multi-jurisdictional** — same template works for any codified law; NL shipped.
- **Hallucination-aware** — fabricated-ECLI traps + post-cutoff tier + fails-only explanations.
- **Honest by construction** — unverified citations are flagged, not guessed.
