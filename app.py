# file: app.py
import os
import json
import re
import time
from datetime import datetime
from typing import List, Dict, Tuple

import streamlit as st
from openai import OpenAI

# ---------------- Parsing ----------------
def parse_true_false(text: str):
    """
    Extract a True/False decision from the model’s text.
    Returns True, False, or None if not found.
    """
    m = re.search(r"\b(True|False)\b", text, re.IGNORECASE)
    if not m:
        return None
    return m.group(1).lower() == "true"

# ---------------- Model call ----------------
def get_openai_client() -> OpenAI:
    """
    Create an OpenAI client using the API key from:
    1) st.session_state (set via UI), else
    2) environment variable OPENAI_API_KEY.
    Raises a clear error if no key is available.
    """
    # Priority: UI-provided key in session_state
    api_key = st.session_state.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Use Streamlit error surface rather than raising raw exception
        st.error("OpenAI API key is required. Please enter it in the sidebar or set the OPENAI_API_KEY environment variable.")
        st.stop()
    return OpenAI(api_key=api_key)

def ask_openai(prompt: str, model: str, temperature: float) -> str:
    """
    Send prompt to OpenAI chat completions and return text.
    """
    client = get_openai_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return resp.choices[0].message.content.strip()

# ---------------- Evaluation ----------------
def evaluate_once(tests: List[Dict], model: str, temperature: float, delay_s: float = 0.15) -> Tuple[int, List[Dict]]:
    """
    Run the provided test set once and return a score and detailed results.
    """
    results = []
    for t in tests:
        output = ask_openai(t["prompt"], model=model, temperature=temperature)
        decision = parse_true_false(output)
        correct = (decision is not None) and (decision == t["ground_truth"])
        results.append({
            "prompt": t["prompt"],
            "output": output,
            "parsed_decision": decision,
            "ground_truth": t["ground_truth"],
            "correct": correct,
            "meta": t.get("meta", {}),
        })
        time.sleep(delay_s)  # gentle pacing to avoid rate limits
    score = sum(r["correct"] for r in results)
    return score, results

def evaluate_consistency(tests: List[Dict], rounds: int, model: str, temperature: float, delay_s: float) -> List[Dict]:
    """
    Run multiple rounds to check consistency (same prompts, temp=0 recommended).
    """
    history = []
    for i in range(rounds):
        score, results = evaluate_once(tests, model=model, temperature=temperature, delay_s=delay_s)
        history.append({
            "round": i + 1,
            "score": score,
            "ratio": f"{score}/{len(tests)}",
            "results": results
        })
    return history

# ---------------- Streamlit App ----------------
st.set_page_config(page_title="S3 Legal LLM Evaluation", page_icon="⚖️", layout="wide")

st.title("S3 Legal LLM Evaluation GUI")
st.caption("Evaluate Accuracy, Recency, and Consistency of instruct LLMs on objective legal citation prompts.")

# Initialize session state for API key (optional, stored only in memory)
if "OPENAI_API_KEY" not in st.session_state:
    # Prefill from environment if available; otherwise empty
    st.session_state.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")

    # Secure API Key input (not shown in logs; stored in session for this run)
    api_key_input = st.text_input(
        "OpenAI API Key",
        value="••••••••••" if st.session_state.OPENAI_API_KEY else "",
        type="password",
        help="Enter your OpenAI API key. It will be stored in memory for this session only."
    )
    # Update the session state only if user provided a non-empty value that's not the placeholder mask
    if api_key_input and api_key_input != "••••••••••":
        st.session_state.OPENAI_API_KEY = api_key_input

    # Show status badge
    if st.session_state.OPENAI_API_KEY:
        st.success("API key set for this session.")
    else:
        st.warning("API key not set. Enter it above or set OPENAI_API_KEY in the environment.")

    model = st.text_input("Model name", value="gpt-4o-mini", help="Use an instruct-capable model name.")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.1, help="Keep at 0.0 for consistency.")
    rounds = int(st.number_input("Consistency rounds", min_value=1, max_value=10, value=3, step=1))
    delay_s = st.slider("Inter-prompt delay (seconds)", min_value=0.0, max_value=2.0, value=0.15, step=0.05)
    st.divider()
    st.caption("Tip: Store ground truth with sources and effective dates for recency checks.")

st.subheader("Benchmark Test Items")

# Initialize tests state
if "tests" not in st.session_state:
    st.session_state.tests = [
        {
            "prompt": "In Dutch Law, is ‘Burgerlijk Wetboek Boek 7 artikel 675’ the correct reference for ‘Wanprestatie’? Answer True/False with a 20-word explanation as to why.",
            "ground_truth": False,
            "meta": {"jurisdiction": "Dutch Law", "topic": "Wanprestatie", "notes": "Example item"}
        }
    ]

# Editor UI
with st.expander("Edit test items", expanded=True):
    for idx, item in enumerate(st.session_state.tests):
        st.markdown(f"Test #{idx+1}")
        item["prompt"] = st.text_area(f"Prompt {idx+1}", value=item["prompt"], height=100, key=f"prompt_{idx}")
        col1, col2 = st.columns([1, 3])
        with col1:
            item["ground_truth"] = st.selectbox(
                f"Ground Truth {idx+1}", options=[True, False],
                index=0 if item["ground_truth"] else 1, key=f"gt_{idx}"
            )
        with col2:
            jurisdiction = st.text_input(f"Jurisdiction {idx+1}", value=item.get("meta", {}).get("jurisdiction", ""), key=f"jur_{idx}")
            topic = st.text_input(f"Topic {idx+1}", value=item.get("meta", {}).get("topic", ""), key=f"topic_{idx}")
            notes = st.text_input(f"Notes {idx+1}", value=item.get("meta", {}).get("notes", ""), key=f"notes_{idx}")
            item["meta"] = {"jurisdiction": jurisdiction, "topic": topic, "notes": notes}
        st.divider()

    add_col, reset_col, load_col = st.columns([1, 1, 1])
    with add_col:
        if st.button("Add test item"):
            st.session_state.tests.append({
                "prompt": "In [Jurisdiction], is ‘[Code name Reference type Number]’ the correct reference for ‘[Subject - Topic]’? Answer True/False with a 20-word explanation as to why.",
                "ground_truth": False,
                "meta": {"jurisdiction": "", "topic": "", "notes": ""}
            })
    with reset_col:
        if st.button("Reset to example"):
            st.session_state.tests = [
                {
                    "prompt": "In Dutch Law, is ‘Burgerlijk Wetboek Boek 7 artikel 675’ the correct reference for ‘Wanprestatie’? Answer True/False with a 20-word explanation as to why.",
                    "ground_truth": False,
                    "meta": {"jurisdiction": "Dutch Law", "topic": "Wanprestatie", "notes": "Example item"}
                }
            ]
    with load_col:
        uploaded = st.file_uploader("Load tests JSON", type=["json"], help="JSON with a list of items: prompt, ground_truth, meta")
        if uploaded is not None:
            try:
                data = json.load(uploaded)
                if isinstance(data, list) and all("prompt" in d and "ground_truth" in d for d in data):
                    st.session_state.tests = data
                    st.success("Loaded tests from JSON.")
                else:
                    st.error("Invalid JSON format. Expect a list of items with 'prompt' and 'ground_truth'.")
            except Exception as e:
                st.error(f"Failed to load JSON: {e}")

# Run evaluation
st.subheader("Run Evaluation")
run_btn = st.button("Run S3 Evaluation")

if run_btn:
    with st.spinner("Running evaluation..."):
        try:
            history = evaluate_consistency(
                tests=st.session_state.tests,
                rounds=rounds,
                model=model,
                temperature=temperature,
                delay_s=delay_s
            )
            summary = {
                "timestamp": datetime.utcnow().isoformat(),
                "model": model,
                "temperature": temperature,
                "total_items": len(st.session_state.tests),
                "rounds": [{"round": r["round"], "ratio": r["ratio"], "score": r["score"]} for r in history],
            }
            st.session_state.history = history
            st.session_state.summary = summary
            st.success("Completed evaluation.")
        except Exception as e:
            st.error(f"Error during evaluation: {e}")

# Show results
if "summary" in st.session_state:
    st.subheader("Summary")
    st.json(st.session_state.summary)

    st.subheader("Per-round Results")
    for r in st.session_state.history:
        st.markdown(f"Round {r['round']} — Score: {r['score']} ({r['ratio']})")
        rows = []
        for item in r["results"]:
            rows.append({
                "Correct": item["correct"],
                "Decision": item["parsed_decision"],
                "Ground Truth": item["ground_truth"],
                "Jurisdiction": item.get("meta", {}).get("jurisdiction", ""),
                "Topic": item.get("meta", {}).get("topic", ""),
                "Prompt": item["prompt"],
                "Output": item["output"],
            })
        st.dataframe(rows, use_container_width=True)
        st.divider()

    # Export buttons
    st.subheader("Export")
    json_data = json.dumps({"runs": st.session_state.history, "summary": st.session_state.summary}, indent=2)
    st.download_button("Download JSON", data=json_data, file_name="s3_results.json", mime="application/json")

    # Flat CSV export
    import csv
    import io
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["round", "correct", "parsed_decision", "ground_truth", "jurisdiction", "topic", "prompt", "output"])
    for r in st.session_state.history:
        for item in r["results"]:
            writer.writerow([
                r["round"],
                item["correct"],
                item["parsed_decision"],
                item["ground_truth"],
                item.get("meta", {}).get("jurisdiction", ""),
                item.get("meta", {}).get("topic", ""),
                item["prompt"],
                item["output"]
            ])
    st.download_button("Download CSV", data=csv_buffer.getvalue(), file_name="s3_results.csv", mime="text/csv")

st.caption("Keep temperature at 0.0 for consistency. Use instruct-capable models. Store ground truth sources and dates for recency checks.")
