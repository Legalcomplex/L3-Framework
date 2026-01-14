import sqlite3
from collections import defaultdict
from .sentence_similarity import *
import pprint


def adjust_final_score_from_q_terms(result, gold_bin, llm_bin, alpha=0.25, beta=0.15, clamp=True):
    """
    Deflate final_score using Q-term penalties.
    Only applies when either gold_bin == 0 OR llm_bin == 0.

    alpha: penalty weight for (Q→LLM − Q→Gold)
    beta : penalty weight for (q_ratio − 1)
    """
    base = float(result.get("final_score", 0.0))

    # Q-based penalty applies ONLY when at least one answer is FALSE
    if not ((gold_bin == 0) or (llm_bin == 0)):
        return max(0.0, min(1.0, base)) if clamp else base

    q_llm = float(result.get("q_llm_score", 0.0) or 0.0)
    q_gold = float(result.get("q_gold_score", 0.0) or 0.0)
    q_ratio = result.get("q_ratio", None)

    penalty = 0.0

    # Penalize if LLM parrots prompt more than gold
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
    Analyze failure and success patterns using score intensity.
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



# normalise_binary but for list of strings

# normalise for table values


def normalize_binary(value):
    """Normalize any binary-like input to 0/1 or None."""
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


def get_eval_scores(db):
    """
    Read eval_table, compute semantic/citation similarity per row,
    and print aggregate metrics.
    """
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

    # trigger error for notes
    score_threshold = 0.80 # shouldbe 0.85

    records = []
    for row in cursor.execute(
        "SELECT id, prompt, gold_response, llm_response, gold_binary, llm_binary FROM eval_table ORDER BY id"):
        rid, prompt, gold_resp, llm_resp, gold_bin, llm_bin = row
        gold_bin = normalize_binary(gold_bin)
        llm_bin = normalize_binary(llm_bin)

        result = legal_similarity(
            gold_resp,
            llm_resp,
            gold_bin,
            llm_bin,
            question=prompt 
        )

        final_score = adjust_final_score_from_q_terms(
            result,
            gold_bin=gold_bin,
            llm_bin=llm_bin,
            alpha=0.25,
            beta=0.15,
            clamp=True
        )
        result["final_score_adjusted"] = final_score

        print(f"\nID {rid}:")
        print(f"  Adjusted Final Score : {final_score:.2f}")
        print(f"  Semantic Similarity  : {result['semantic_similarity']:.2f}")
        print(f"  Citation Similarity  : {result['citation_similarity']:.2f}")
        print(f"  Truth Alignment      : {result['truth_alignment']:.2f}")
        print(f"  Penalty Applied      : {result['penalty']}")
        if 'bonus' in result and result['bonus']:
            print(f"  Bonus Applied        : {result['bonus']:.2f}")
        else:
            print(f"  Bonus Applied        : 0.00")

        if 'question_citations' in result:
            print(f"  Question Citations   : {result['question_citations']}")
        else:
            print("  Question Citations   : None")

        print(f"  Gold Citations       : {result['gold_citations']}")
        print(f"  LLM Citations        : {result['llm_citations']}")

        print(f"  Q→Gold Semantic Score : {result['q_gold_score']:.2f}")
        print(f"  Q→LLM Semantic Score  : {result['q_llm_score']:.2f}")
        if result['q_ratio'] is not None:
            print(f"  Q→LLM/Q→Gold Ratio    : {result['q_ratio']:.2f}")
        else:
            print("  Q→LLM/Q→Gold Ratio    : N/A")

        match = final_score >= score_threshold
        records.append((rid, match, final_score))

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
        pattern = analyse_pattern(fail_positions, total_count, scores=fail_scores)
        if pattern["avg_gap"] is not None:
            print(f"  - Average gap between failures: {pattern['avg_gap']:.2f} questions")
        else:
            print("  - Not enough data to calculate gap.")
        print(f"  - Gaps sequence: {pattern['gaps']}")
        print(f"  - Failures are mostly at the {pattern['region']} of the dataset")
        print(f"  - Longest consecutive-failure streak: {pattern['longest_fail_streak']}")
        print(f"  - Longest consecutive-success streak: {pattern['longest_success_streak']}")
        print(f"  - Average fail score: {pattern['avg_fail_score']:.2f}")
        print(f"  - Worst streak average score: {pattern['worst_streak_avg']:.2f}")

    summary = {
        "overall_accuracy": overall_accuracy,
        "deficiency_score": deficiency_score,
        "fail_positions": fail_positions,
        "pattern": pattern,
    }

    return summary
