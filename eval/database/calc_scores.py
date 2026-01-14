import sqlite3
from collections import defaultdict
from .sentence_similarity import *
import pprint


def _fmt_float(x, nd=2, na="N/A"):
    """Format float-like values safely (handles None)."""
    if x is None:
        return na
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return na

ALLOWED_USER_REQUESTS = {
    "final_score",
    "final_score_adjusted",
    "semantic_similarity",
    "citation_similarity",
    "truth_alignment",
    "q_gold_score",
    "q_llm_score",
    "q_ratio",
    "penalty",
    "bonus",
}


def normalise_user_requests(user_request):
    """
    Accept None, a single string, or an iterable of strings.
    Returns:
      - None if user_request is None (meaning: print full default output)
      - otherwise a non-empty list of allowed metric keys
    Raises:
      - ValueError if any requested metric is not allowed
    """
    if user_request is None:
        return None

    # single metric
    if isinstance(user_request, str):
        reqs = [user_request]
    else:
        reqs = list(user_request)

    # clean + validate
    reqs = [r.strip() for r in reqs if isinstance(r, str) and r.strip()]
    bad = [r for r in reqs if r not in ALLOWED_USER_REQUESTS]
    if bad:
        raise ValueError(
            f"Invalid user_request(s): {bad}. Only allowed: {sorted(ALLOWED_USER_REQUESTS)}"
        )

    return reqs if reqs else None


def adjust_final_score_from_q_terms(result, gold_bin, llm_bin, alpha=0.25, beta=0.15, clamp=True):
    """
    Deflate final_score using Q-term penalties.
    Only applies when either gold_bin == 0 OR llm_bin == 0.

    alpha: penalty weight for (Q→LLM − Q→Gold)
    beta : penalty weight for (q_ratio − 1)
    """
    base = float(result.get("final_score", 0.0) or 0.0)

    # Q-based penalty applies if at least one answer is FALSE
    if not ((gold_bin == 0) or (llm_bin == 0)):
        return max(0.0, min(1.0, base)) if clamp else base

    q_llm = float(result.get("q_llm_score", 0.0) or 0.0)
    q_gold = float(result.get("q_gold_score", 0.0) or 0.0)
    q_ratio = result.get("q_ratio", None)

    penalty = 0.0

    # Penalise if LLM parrots prompt more than gold
    prompt_overlap_excess = max(0.0, q_llm - q_gold)
    penalty += alpha * prompt_overlap_excess

    # Additional penalty if Q->LLM / Q→Gold ratio > 1
    if q_ratio is not None:
        ratio_excess = max(0.0, float(q_ratio) - 1.0)
        penalty += beta * ratio_excess

    adjusted = base - penalty

    # Clamp score to [0,1]
    if clamp:
        adjusted = max(0.0, min(1.0, adjusted))

    return adjusted


def analyse_pattern(fail_positions, total_count, scores=None, all_scores=None, threshold=0.8):
    """
    Analyse failure and success patterns using score intensity.
    Includes longest fail streak and longest success streak.
    """
    if not fail_positions:
        return {
            "avg_gap": None,
            "gaps": [],
            "region": None,
            "longest_fail_streak": 0,
            "longest_success_streak": None,
            "avg_fail_score": None,
            "worst_streak_avg": None,
        }

    fail_positions = sorted(set(fail_positions))
    gaps = [j - i for i, j in zip(fail_positions, fail_positions[1:])]
    avg_gap = sum(gaps) / len(gaps) if gaps else None

    third = total_count / 3.0
    counts = {
        "beginning": sum(p <= third for p in fail_positions),
        "middle": sum(third < p <= 2 * third for p in fail_positions),
        "end": sum(p > 2 * third for p in fail_positions),
    }
    dominant_region, dominant_count = max(counts.items(), key=lambda kv: kv[1])
    total_f = len(fail_positions)
    region = dominant_region if total_f and dominant_count / total_f >= 0.6 else "spread"

    longest_fail_streak = 1
    current_streak = 1
    streak_scores = []
    current_scores = [scores[0]] if scores else []

    for i in range(1, len(fail_positions)):
        if fail_positions[i] == fail_positions[i - 1] + 1:
            current_streak += 1
            if scores:
                current_scores.append(scores[i])
        else:
            if scores and current_scores:
                streak_scores.append(sum(current_scores) / len(current_scores))
            current_streak = 1
            current_scores = [scores[i]] if scores else []
        longest_fail_streak = max(longest_fail_streak, current_streak)

    if scores and current_scores:
        streak_scores.append(sum(current_scores) / len(current_scores))

    avg_fail_score = sum(scores) / len(scores) if scores else None
    worst_streak_avg = min(streak_scores) if streak_scores else None

    longest_success_streak = 0
    if all_scores:
        success_mask = [s >= threshold for s in all_scores]
        current_s = 0
        for val in success_mask:
            if val:
                current_s += 1
                longest_success_streak = max(longest_success_streak, current_s)
            else:
                current_s = 0

    return {
        "avg_gap": avg_gap,
        "gaps": gaps,
        "region": region,
        "longest_fail_streak": longest_fail_streak,
        "longest_success_streak": longest_success_streak,
        "avg_fail_score": avg_fail_score,
        "worst_streak_avg": worst_streak_avg,
    }


def normalise_binary(value):
    """Normalise any binary-like input to 0/1 or None."""
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("1", "true", "t", "yes"):
            return 1
        if v in ("0", "false", "f", "no"):
            return 0
    return None

def get_metric_value(result, req, gold_bin, llm_bin):
    """
    Returns a numeric value for a requested metric.
    Special-cases final_score_adjusted so it is computed on demand.
    """
    if req == "final_score_adjusted":
        return adjust_final_score_from_q_terms(
            result,
            gold_bin=gold_bin,
            llm_bin=llm_bin,
            alpha=0.25,
            beta=0.15,
            clamp=True,
        )
    return result.get(req, None)


def truth_gate_score(user_score, gold_bin, llm_bin, clamp=True):
    """
    Apply truth-alignment rules to ONE score (the user-input score).

    Rules:
      - both true  -> 1
      - one true/one false -> 0
      - both false -> keep user_score (logic calculate)
    """
    gb = normalise_binary(gold_bin)
    lb = normalise_binary(llm_bin)

    # If unknown truth labels, don't gate.
    if gb is None or lb is None:
        return user_score

    if gb == 1 and lb == 1:
        return 1.0
    if (gb == 1 and lb == 0) or (gb == 0 and lb == 1):
        return 0.0

    # both false => keep computed score (optionally clamp)
    if user_score is None:
        return None
    try:
        s = float(user_score)
    except Exception:
        return user_score

    if clamp:
        s = max(0.0, min(1.0, s))
    return s


def get_eval_scores(db, user_request=None, always_show_adjusted=False):
    """
    Read eval_table, compute semantic/citation similarity per row,
    and print aggregate metrics.

    Updated to support:
      - user_request as a single metric key string, OR
      - user_request as an iterable of metric keys (list/tuple/set)

    Aggregation for multiple metrics (for pass/fail + summary score):
      - uses MIN score across requested metrics (row passes only if all are strong)

    Behaviour:
      - If user_request includes 'final_score_adjusted', it is computed on-demand.
      - If user_request has MORE THAN ONE metric AND includes truth_alignment:
          * aggregate score is computed ONLY from non-truth metrics
          * if all non-truth metrics are missing/NaN, fallback to final_score_adjusted
          * then truth gate is applied to that single aggregate score:
              - both true => 1
              - one true/one false => 0
              - both false => keep aggregate score

    Display behaviour:
      - In USER_INPUT mode:
          * If always_show_adjusted=True, always prints "Adjusted Final Score".
          * Otherwise, prints "Adjusted Final Score" only when the aggregate score
            actually depends on final_score_adjusted (explicitly requested as sole metric,
            or used as fallback in truth-alignment aggregation path).
    """
    user_requests = normalise_user_requests(user_request)

    if isinstance(db, str):
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        close_after = True
    else:
        conn, cursor = db.get_conn_cursor()
        close_after = True

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eval_table';")
    if not cursor.fetchone():
        if close_after:
            conn.close()
        raise RuntimeError("Table 'eval_table' not found in database.")

    score_threshold = 0.85

    records = []
    all_adjusted_scores = []

    for row in cursor.execute(
        "SELECT id, prompt, gold_response, llm_response, gold_binary, llm_binary FROM eval_table ORDER BY id"
    ):
        rid, prompt, gold_resp, llm_resp, gold_bin, llm_bin = row
        gold_bin = normalise_binary(gold_bin)
        llm_bin = normalise_binary(llm_bin)

        result = legal_similarity(
            gold_resp,
            llm_resp,
            gold_bin,
            llm_bin,
            question=prompt,
        )

        # Always compute adjusted (used for default printing + possible fallback + optional display)
        final_score_adjusted = adjust_final_score_from_q_terms(
            result,
            gold_bin=gold_bin,
            llm_bin=llm_bin,
            alpha=0.25,
            beta=0.15,
            clamp=True,
        )

        # If user asked for specific metric(s)
        if user_requests is not None:
            print(f"\nID {rid}:")

            row_scores = []  # list of (req, score_float_or_nan)
            has_truth_alignment = ("truth_alignment" in user_requests)

            for req in user_requests:
                val = get_metric_value(result, req, gold_bin, llm_bin)

                if val is None:
                    print(f"  {req:>22} : None (missing)")
                    row_scores.append((req, float("nan")))
                    continue

                print(f"  {req:>22} : {_fmt_float(val)}")

                try:
                    score = float(val)
                except (TypeError, ValueError):
                    print(f"  {req} is not numeric: {val!r}")
                    score = float("nan")

                row_scores.append((req, score))

            agg_source = "user_input"

            if has_truth_alignment and len(user_requests) > 1:
                # Aggregate ONLY non-truth metrics
                non_truth_scores = [
                    s for (req, s) in row_scores
                    if req != "truth_alignment" and (s == s)  # not NaN
                ]

                if non_truth_scores:
                    base_agg = min(non_truth_scores)
                    agg_source = "user_input(non_truth_min)"
                else:
                    # Fallback when non-truth metrics are missing
                    base_agg = final_score_adjusted
                    agg_source = "final_score_adjusted(fallback)"

                # Apply truth rules to the single aggregate
                agg_score = truth_gate_score(base_agg, gold_bin, llm_bin, clamp=True)
                agg_source += "+truth_gate"

            else:
                # Default: MIN across requested metrics
                numeric_scores = [(req, s) for (req, s) in row_scores if s == s]  # NaN filter
                if numeric_scores:
                    agg_score = min(s for (_, s) in numeric_scores)

                    # If the user's chosen input is solely final_score_adjusted,
                    # then the aggregate is based on adjusted_final_score.
                    if len(user_requests) == 1 and user_requests[0] == "final_score_adjusted":
                        agg_source = "final_score_adjusted(user_input)"
                    else:
                        agg_source = "user_input(min)"
                else:
                    agg_score = float("nan")
                    agg_source = "no_numeric_user_input"
                    
            show_adjusted = (
                always_show_adjusted
                or (len(user_requests) == 1 and user_requests[0] == "final_score_adjusted")
                or ("final_score_adjusted" in agg_source)
            )

            if show_adjusted:
                print(f"  {'Adjusted Final Score':>22} : {_fmt_float(final_score_adjusted)}")

            match = (agg_score == agg_score) and (agg_score >= score_threshold)

            records.append((rid, match, agg_score))
            all_adjusted_scores.append(agg_score)

        # Default behaviour (no user_request): print full output using adjusted final score
        else:
            result["final_score_adjusted"] = final_score_adjusted

            print(f"\nID {rid}:")
            print(f"  Adjusted Final Score : {_fmt_float(final_score_adjusted)}")
            print(f"  Final Score (raw)    : {_fmt_float(result.get('final_score'))}")

            # These may be None under truth-gated early returns
            print(f"  Semantic Similarity  : {_fmt_float(result.get('semantic_similarity'))}")
            print(f"  Citation Similarity  : {_fmt_float(result.get('citation_similarity'))}")
            print(f"  Truth Alignment      : {_fmt_float(result.get('truth_alignment'))}")

            print(f"  Penalty Applied      : {result.get('penalty', 0.0)}")
            bonus_val = result.get("bonus", 0.0)
            try:
                bonus_val = float(bonus_val or 0.0)
            except Exception:
                bonus_val = 0.0
            print(f"  Bonus Applied        : {_fmt_float(bonus_val)}")

            # Optional debug marker from truth gate
            if "truth_gate" in result:
                print(f"  Truth Gate           : {result['truth_gate']}")

            # Citations (should exist even in truth-gated early returns)
            q_cits = result.get("question_citations", None)
            print(f"  Question Citations   : {q_cits if q_cits is not None else 'None'}")
            print(f"  Gold Citations       : {result.get('gold_citations', [])}")
            print(f"  LLM Citations        : {result.get('llm_citations', [])}")

            # Q-scores may be None under truth-gated early returns
            print(f"  Q→Gold Semantic Score : {_fmt_float(result.get('q_gold_score'))}")
            print(f"  Q→LLM Semantic Score  : {_fmt_float(result.get('q_llm_score'))}")
            if result.get("q_ratio", None) is not None:
                print(f"  Q→LLM/Q→Gold Ratio    : {_fmt_float(result.get('q_ratio'))}")
            else:
                print("  Q→LLM/Q→Gold Ratio    : N/A")

            match = final_score_adjusted >= score_threshold
            records.append((rid, match, final_score_adjusted))
            all_adjusted_scores.append(final_score_adjusted)

    if close_after:
        conn.close()

    if not records:
        print("No data found in eval_table.")
        return

    total_count = len(records)
    total_correct = sum(1 for _, match, _ in records if match)

    fails = [(i + 1, s) for i, (_, _, s) in enumerate(records) if s < score_threshold]
    fail_positions = [i for i, _ in fails]
    fail_scores = [s for _, s in fails]

    overall_accuracy = total_correct / total_count if total_count else 0.0
    deficiency_score = 1 - overall_accuracy

    print(f"\nOverall deficiency Similarity Score: {deficiency_score:.2f}")
    print(f"Overall accuracy: {overall_accuracy*100:.2f}%")
    print(f"Total correct: {total_correct}/{total_count}")
    print(f"Failures at question #: {fail_positions if fail_positions else 'None'}")

    print("\nFailure Pattern Analysis:")
    if not fail_positions:
        print("  - No failures in dataset.")
        pattern = None
    else:
        pattern = analyse_pattern(
            fail_positions,
            total_count,
            scores=fail_scores,
            all_scores=all_adjusted_scores,
            threshold=score_threshold,
        )
        if pattern["avg_gap"] is not None:
            print(f"  - Average gap between failures: {pattern['avg_gap']:.2f} questions")
        else:
            print("  - Not enough data to calculate gap.")
        print(f"  - Gaps sequence: {pattern['gaps']}")
        print(f"  - Failures are mostly at the {pattern['region']} of the dataset")
        print(f"  - Longest consecutive-failure streak: {pattern['longest_fail_streak']}")
        print(f"  - Longest consecutive-success streak: {pattern['longest_success_streak']}")
        if pattern["avg_fail_score"] is not None:
            print(f"  - Average fail score: {pattern['avg_fail_score']:.2f}")
        else:
            print("  - Average fail score: N/A")
        if pattern["worst_streak_avg"] is not None:
            print(f"  - Worst streak average score: {pattern['worst_streak_avg']:.2f}")
        else:
            print("  - Worst streak average score: N/A")

    summary = {
        "overall_accuracy": overall_accuracy,
        "deficiency_score": deficiency_score,
        "fail_positions": fail_positions,
        "pattern": pattern,
    }

    return summary
