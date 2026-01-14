from .utils import *

def add_eval_entries(entries):
    """Add multiple evaluation entries at once."""
    ensure_eval_table_exists()

    conn, cursor = get_conn_cursor()
    to_insert = []
    for entry in entries:
        if len(entry) < 3:
            print("Skipped invalid entry:", entry)
            continue
        prompt, gold_resp, llm_resp = entry[0], entry[1], entry[2]
        category = entry[3] if len(entry) > 3 else "uncategorized"
        gold_bin, gold_text = parse_answer(gold_resp)
        llm_bin, llm_text = parse_answer(llm_resp)
        to_insert.append((prompt, gold_bin, gold_text, llm_bin, llm_text, category))

    cursor.executemany("""
        INSERT INTO eval_table (prompt, gold_binary, gold_response, llm_binary, llm_response, category)
        VALUES (?, ?, ?, ?, ?, ?)
    """, to_insert)
    conn.commit()
    conn.close()
    print(f"Added {len(to_insert)} new entries to eval_table.")