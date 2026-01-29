import streamlit as st
import pandas as pd
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eval.database import calc_scores as cs
from eval.database import db
from eval.database.sentence_similarity import legal_similarity, extract_citations

st.set_page_config(
    page_title="L3-Framework - Legal LLM Evaluation",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ L3-Framework")
st.subheader("Legal LLM Evaluation Framework")

st.markdown("""
This framework evaluates Large Language Models on legal tasks by measuring three core deficiency areas:
- **Accuracy**: Correct citation of legal codes and case law
- **Recency**: Knowledge of up-to-date legal information
- **Consistency**: Reliability on repeated objective tasks
""")

# Sidebar for navigation
page = st.sidebar.selectbox(
    "Choose an action",
    ["Single Evaluation", "Batch Evaluation (CSV)", "View Database", "Manage Database"]
)

if page == "Single Evaluation":
    st.header("Single Response Evaluation")
    st.markdown("Compare a gold standard response with an LLM response for a legal prompt.")

    col1, col2 = st.columns(2)

    with col1:
        prompt = st.text_area(
            "Legal Prompt/Question",
            height=100,
            placeholder="Enter the legal question or prompt..."
        )

        gold_response = st.text_area(
            "Gold Standard Response",
            height=150,
            placeholder="True/False. [Explanation with citations like 42 U.S.C. § 1983]"
        )

    with col2:
        llm_response = st.text_area(
            "LLM Response",
            height=150,
            placeholder="True/False. [LLM's response with citations]"
        )

        # Parse binary values from responses
        def parse_binary(text):
            if not text:
                return None
            text_lower = text.strip().lower()
            if text_lower.startswith("true"):
                return 1
            elif text_lower.startswith("false"):
                return 0
            return None

    if st.button("Evaluate", type="primary"):
        if not prompt or not gold_response or not llm_response:
            st.warning("Please fill in all fields.")
        else:
            with st.spinner("Computing similarity scores..."):
                gold_bin = parse_binary(gold_response)
                llm_bin = parse_binary(llm_response)

                result = legal_similarity(
                    gold_response,
                    llm_response,
                    gold_bin,
                    llm_bin,
                    question=prompt
                )

                # Compute adjusted score
                final_adjusted = cs.adjust_final_score_from_q_terms(
                    result,
                    gold_bin=gold_bin,
                    llm_bin=llm_bin
                )

            st.success("Evaluation complete!")

            # Display results
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Final Score (Adjusted)", f"{final_adjusted:.2f}")
            with col2:
                st.metric("Final Score (Raw)", f"{result.get('final_score', 0):.2f}")
            with col3:
                threshold = 0.85
                status = "✅ PASS" if final_adjusted >= threshold else "❌ FAIL"
                st.metric("Status", status)

            st.divider()

            # Detailed metrics
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Similarity Metrics")
                metrics_data = {
                    "Metric": ["Semantic Similarity", "Citation Similarity", "Truth Alignment"],
                    "Score": [
                        f"{result.get('semantic_similarity', 'N/A'):.2f}" if result.get('semantic_similarity') is not None else "N/A",
                        f"{result.get('citation_similarity', 'N/A'):.2f}" if result.get('citation_similarity') is not None else "N/A",
                        f"{result.get('truth_alignment', 'N/A'):.2f}" if result.get('truth_alignment') is not None else "N/A"
                    ]
                }
                st.table(pd.DataFrame(metrics_data))

            with col2:
                st.subheader("Question-Answer Scores")
                qa_data = {
                    "Metric": ["Q→Gold Score", "Q→LLM Score", "Q Ratio"],
                    "Value": [
                        f"{result.get('q_gold_score', 'N/A'):.2f}" if result.get('q_gold_score') is not None else "N/A",
                        f"{result.get('q_llm_score', 'N/A'):.2f}" if result.get('q_llm_score') is not None else "N/A",
                        f"{result.get('q_ratio', 'N/A'):.2f}" if result.get('q_ratio') is not None else "N/A"
                    ]
                }
                st.table(pd.DataFrame(qa_data))

            # Citations
            st.subheader("Extracted Citations")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("**Question Citations:**")
                q_cits = result.get('question_citations', [])
                st.write(q_cits if q_cits else "None found")

            with col2:
                st.write("**Gold Citations:**")
                gold_cits = result.get('gold_citations', [])
                st.write(gold_cits if gold_cits else "None found")

            with col3:
                st.write("**LLM Citations:**")
                llm_cits = result.get('llm_citations', [])
                st.write(llm_cits if llm_cits else "None found")

            # Additional info
            with st.expander("Additional Details"):
                st.json({
                    "penalty": result.get('penalty', 0),
                    "bonus": result.get('bonus', 0),
                    "exact_gold_overlap": result.get('exact_gold_overlap'),
                    "exact_q_overlap": result.get('exact_q_overlap'),
                    "title_conflict": result.get('title_conflict'),
                    "truth_gate": result.get('truth_gate', 'N/A')
                })

elif page == "Batch Evaluation (CSV)":
    st.header("Batch Evaluation from CSV")
    st.markdown("""
    Upload a CSV file with the following columns:
    - `prompt` - The legal question
    - `gold_answer` or `gold_response` - The gold standard response
    - `llm_answer` or `llm_response` - The LLM's response

    Responses should start with `True.` or `False.` followed by the explanation.
    """)

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        # Save uploaded file temporarily
        temp_path = "/tmp/uploaded_eval.csv"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        # Preview the data
        df = pd.read_csv(temp_path)
        st.write("**Preview of uploaded data:**")
        st.dataframe(df.head())

        if st.button("Run Batch Evaluation", type="primary"):
            with st.spinner("Processing... This may take a while for large datasets."):
                try:
                    # Clear existing data and load new
                    db.ensure_eval_table_exists()
                    db.delete_eval_entries()
                    db.create_eval_table_from_csv(temp_path)

                    # Capture the output
                    import io
                    from contextlib import redirect_stdout

                    f = io.StringIO()
                    with redirect_stdout(f):
                        summary = cs.get_eval_scores(db)

                    output = f.getvalue()

                    st.success("Batch evaluation complete!")

                    # Display summary metrics
                    if summary:
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Overall Accuracy", f"{summary['overall_accuracy']*100:.1f}%")
                        with col2:
                            st.metric("Deficiency Score", f"{summary['deficiency_score']:.2f}")
                        with col3:
                            st.metric("Failed Questions", len(summary['fail_positions']))

                        if summary['fail_positions']:
                            st.write(f"**Failed at questions:** {summary['fail_positions']}")

                        if summary.get('pattern'):
                            st.subheader("Failure Pattern Analysis")
                            pattern = summary['pattern']
                            pattern_data = {
                                "Metric": [
                                    "Failures Region",
                                    "Longest Fail Streak",
                                    "Longest Success Streak",
                                    "Average Fail Score"
                                ],
                                "Value": [
                                    pattern.get('region', 'N/A'),
                                    pattern.get('longest_fail_streak', 'N/A'),
                                    pattern.get('longest_success_streak', 'N/A'),
                                    f"{pattern.get('avg_fail_score', 0):.2f}" if pattern.get('avg_fail_score') else "N/A"
                                ]
                            }
                            st.table(pd.DataFrame(pattern_data))

                    # Show detailed output
                    with st.expander("Detailed Output"):
                        st.text(output)

                except Exception as e:
                    st.error(f"Error during evaluation: {str(e)}")

elif page == "View Database":
    st.header("View Evaluation Database")

    try:
        from eval.database.utils import get_conn_cursor
        conn, cursor = get_conn_cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eval_table';")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM eval_table")
            count = cursor.fetchone()[0]
            st.info(f"Database contains {count} entries.")

            if count > 0:
                limit = st.slider("Number of entries to display", 5, min(100, count), 10)
                cursor.execute(f"SELECT * FROM eval_table LIMIT {limit}")
                rows = cursor.fetchall()

                df = pd.DataFrame(rows, columns=[
                    "ID", "Prompt", "Gold Binary", "Gold Response",
                    "LLM Binary", "LLM Response", "Category"
                ])
                st.dataframe(df, use_container_width=True)
        else:
            st.warning("No eval_table found in the database. Upload a CSV to create one.")

        conn.close()
    except Exception as e:
        st.error(f"Error accessing database: {str(e)}")

elif page == "Manage Database":
    st.header("Database Management")

    st.warning("⚠️ These actions are destructive and cannot be undone!")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Clear All Entries"):
            try:
                db.delete_eval_entries()
                st.success("All entries deleted from eval_table.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    with col2:
        if st.button("Drop Entire Table"):
            try:
                db.drop_eval_table()
                st.success("eval_table dropped from database.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    st.divider()

    st.subheader("Add Single Entry")

    with st.form("add_entry_form"):
        new_prompt = st.text_area("Prompt")
        new_gold = st.text_area("Gold Response")
        new_llm = st.text_area("LLM Response")

        submitted = st.form_submit_button("Add Entry")
        if submitted:
            if new_prompt and new_gold and new_llm:
                try:
                    db.add_eval_entry(new_prompt, new_gold, new_llm)
                    st.success("Entry added successfully!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please fill in all fields.")

# Footer
st.divider()
st.markdown("""
---
**L3-Framework** | Legal LLM Evaluation Framework
[GitHub Repository](https://github.com/Legalcomplex/L3-Framework)
""")
