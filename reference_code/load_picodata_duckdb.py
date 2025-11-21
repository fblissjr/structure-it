import json
import uuid

import duckdb
import pandas as pd

# --- Configuration ---
DB_FILE = "image_edits.duckdb"
SFT_FILE = "sft.jsonl"
MULTI_TURN_FILE = "multi-turn.jsonl"
PREFERENCE_FILE = "preference.jsonl"


def initialize_database(con):
    """Drops old tables and creates the new, robust schema with a sequence for model_id."""
    print("--- Initializing new database schema ---")
    con.execute("DROP TABLE IF EXISTS single_turn_edits;")
    con.execute("DROP TABLE IF EXISTS multi_turn_sessions;")
    con.execute("DROP TABLE IF EXISTS multi_turn_steps;")
    con.execute("DROP TABLE IF EXISTS edit_preferences;")
    con.execute("DROP TABLE IF EXISTS embedding_models;")
    con.execute("DROP SEQUENCE IF EXISTS model_id_seq;")

    con.execute("CREATE SEQUENCE model_id_seq START 1;")

    con.execute("""
        CREATE TABLE embedding_models (
            model_id INTEGER PRIMARY KEY DEFAULT nextval('model_id_seq'),
            model_name VARCHAR UNIQUE NOT NULL,
            embedding_dimension INTEGER,
            pooling_strategy VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("✅ Table 'embedding_models' created with auto-incrementing ID.")


def load_single_turn_edits(con):
    print(f"Loading '{SFT_FILE}'...")
    df = pd.read_json(SFT_FILE, lines=True)
    df.rename(
        columns={
            "open_image_input_url": "input_image_url",
            "text": "full_edit_prompt",
            "output_image": "output_image_path",
            "edit_type": "edit_category",
            "summarized_text": "prompt_summary",
        },
        inplace=True,
    )

    df["uuid"] = [uuid.uuid4() for _ in range(len(df))]
    df["source_file"] = SFT_FILE

    con.execute("""
        CREATE TABLE single_turn_edits (
            uuid UUID PRIMARY KEY,
            input_image_url VARCHAR,
            full_edit_prompt VARCHAR,
            output_image_path VARCHAR,
            edit_category VARCHAR,
            prompt_summary VARCHAR,
            source_file VARCHAR,
            prompt_embedding DOUBLE[], -- **FIX: Changed FLOAT[] to DOUBLE[]**
            embedding_model_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        );
    """)
    con.execute("INSERT INTO single_turn_edits BY NAME FROM df;")
    print(f"✅ Loaded {len(df)} records into 'single_turn_edits'.")


def load_multi_turn_conversations(con):
    print(f"Loading and normalizing '{MULTI_TURN_FILE}'...")
    sessions_data = []
    steps_data = []
    with open(MULTI_TURN_FILE, "r") as f:
        # ... (rest of data processing is unchanged)
        for session_id, line in enumerate(f, 1):
            data = json.loads(line)
            original_url = next(
                (
                    item["url"]
                    for item in data["files"]
                    if item["id"] == "original_input_image"
                ),
                None,
            )
            final_url = next(
                (item["url"] for item in data["files"] if item["id"] == "final_image"),
                None,
            )
            sessions_data.append(
                {
                    "session_id": session_id,
                    "original_input_image_url": original_url,
                    "final_image_path": final_url,
                    "total_turns": len(data["metadata_edit_turn_prompts"]),
                    "source_file": MULTI_TURN_FILE,
                }
            )
            for turn_number, prompt in enumerate(data["metadata_edit_turn_prompts"], 1):
                turn_image_path = next(
                    (
                        item["url"]
                        for item in data["files"]
                        if item["id"] == f"edit_turn{turn_number}"
                    ),
                    None,
                )
                steps_data.append(
                    {
                        "session_id": session_id,
                        "turn_number": turn_number,
                        "prompt": prompt,
                        "output_image_path": turn_image_path,
                    }
                )
    sessions_df = pd.DataFrame(sessions_data)
    steps_df = pd.DataFrame(steps_data)

    con.execute("""
        CREATE TABLE multi_turn_sessions (
            session_id INTEGER PRIMARY KEY,
            original_input_image_url VARCHAR,
            final_image_path VARCHAR,
            total_turns INTEGER,
            source_file VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    con.execute("INSERT INTO multi_turn_sessions BY NAME FROM sessions_df;")
    print(f"✅ Loaded {len(sessions_df)} records into 'multi_turn_sessions'.")

    con.execute("""
        CREATE TABLE multi_turn_steps (
            session_id INTEGER,
            turn_number INTEGER,
            prompt VARCHAR,
            output_image_path VARCHAR,
            prompt_embedding DOUBLE[], -- **FIX: Changed FLOAT[] to DOUBLE[]**
            embedding_model_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            PRIMARY KEY (session_id, turn_number)
        );
    """)
    con.execute("INSERT INTO multi_turn_steps BY NAME FROM steps_df;")
    print(f"✅ Loaded {len(steps_df)} records into 'multi_turn_steps'.")


def load_edit_preferences(con):
    print(f"Loading '{PREFERENCE_FILE}'...")
    df = pd.read_json(PREFERENCE_FILE, lines=True)
    df.rename(
        columns={
            "output_image": "chosen_image_path",
            "rejected_images": "rejected_image_paths",
            "text": "full_edit_prompt",
            "edit_type": "edit_category",
            "open_image_input_url": "input_image_url",
            "summarized_text": "prompt_summary",
        },
        inplace=True,
    )

    df["uuid"] = [uuid.uuid4() for _ in range(len(df))]
    df["source_file"] = PREFERENCE_FILE

    con.execute("""
        CREATE TABLE edit_preferences (
            uuid UUID PRIMARY KEY,
            chosen_image_path VARCHAR,
            rejected_image_paths VARCHAR[],
            full_edit_prompt VARCHAR,
            edit_category VARCHAR,
            input_image_url VARCHAR,
            prompt_summary VARCHAR,
            source_file VARCHAR,
            prompt_embedding DOUBLE[], -- **FIX: Changed FLOAT[] to DOUBLE[]**
            embedding_model_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        );
    """)
    con.execute("INSERT INTO edit_preferences BY NAME FROM df;")
    print(f"✅ Loaded {len(df)} records into 'edit_preferences'.")


def main():
    con = duckdb.connect(database=DB_FILE, read_only=False)
    initialize_database(con)
    load_single_turn_edits(con)
    load_multi_turn_conversations(con)
    load_edit_preferences(con)

    print("\n--- Verification ---")
    print("Database schema created. Tables and schemas:\n")
    all_tables = con.execute("SHOW ALL TABLES;").fetchdf()
    print(all_tables)
    con.close()

    print(f"\nDatabase '{DB_FILE}' is ready for embedding.")


if __name__ == "__main__":
    main()
