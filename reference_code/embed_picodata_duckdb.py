import datetime

import duckdb
import pandas as pd
from pylate import models

# --- Configuration ---
DB_FILE = "image_edits.duckdb"
MODEL_NAME = "mixedbread-ai/mxbai-edge-colbert-v0-17m"
EMBEDDING_COLUMN = "prompt_embedding"


def get_or_create_model_entry(con, model):
    """
    Checks if the model exists in the metadata table. If not, it creates it.
    Returns the model's ID.
    """
    print("--- Registering embedding model in the database ---")
    model_name = model.model_card_data.base_model or MODEL_NAME
    embedding_dim = model.get_sentence_embedding_dimension()
    pooling_strategy = "mean"  # Standard for ColBERT-style models

    # **FIX:** Use "ON CONFLICT DO NOTHING" for DuckDB instead of "INSERT OR IGNORE".
    # This safely inserts the model only if its name isn't already in the table.
    con.execute(
        """
        INSERT INTO embedding_models (model_name, embedding_dimension, pooling_strategy)
        VALUES (?, ?, ?)
        ON CONFLICT (model_name) DO NOTHING;
        """,
        [model_name, embedding_dim, pooling_strategy],
    )

    # Retrieve the model_id for the given model name
    result = con.execute(
        "SELECT model_id FROM embedding_models WHERE model_name = ?;", [model_name]
    ).fetchone()
    if result is None:
        raise RuntimeError(f"Failed to insert or retrieve model_id for {model_name}")

    model_id = result[0]
    print(
        f"✅ Using Model ID: {model_id} for '{model_name}' (Dimension: {embedding_dim})"
    )
    return model_id


def add_embeddings_to_table(con, model, model_id, table_name, text_column):
    """
    Fetches text, generates embeddings, and updates the table.
    """
    print(f"\n--- Processing table: '{table_name}' ---")

    try:
        df = con.execute(f'SELECT rowid, "{text_column}" FROM {table_name}').fetchdf()
        print(f"Found {len(df)} rows to process.")
    except duckdb.CatalogException:
        print(
            f"⚠️ Warning: Table '{table_name}' or column '{text_column}' not found. Skipping."
        )
        return

    if df.empty or df[text_column].isnull().all():
        print("No text data to embed. Skipping.")
        return

    print(f"Generating embeddings for '{text_column}'...")
    texts = df[text_column].tolist()
    embeddings = model.encode(
        texts,
        batch_size=32,
        is_query=False,
        show_progress_bar=True,  # This will display a progress bar
        convert_to_numpy=False,
    )

    temp_df = pd.DataFrame(
        {"rowid": df["rowid"], "embedding": [emb.tolist() for emb in embeddings]}
    )

    print("Staging embeddings for database update...")
    con.register("temp_embeddings_df", temp_df)

    print(f"Executing UPDATE on '{table_name}'...")
    con.execute(
        f"""
        UPDATE {table_name}
        SET
            {EMBEDDING_COLUMN} = temp.embedding,
            embedding_model_id = ?,
            updated_at = ?
        FROM temp_embeddings_df AS temp
        WHERE {table_name}.rowid = temp.rowid;
    """,
        [model_id, datetime.datetime.now()],
    )

    con.unregister("temp_embeddings_df")
    print(f"✅ Successfully updated '{table_name}' with embeddings.")


def main():
    print("--- Starting Embedding Generation with PyLate ---")

    print(f"Loading local model via PyLate: '{MODEL_NAME}'...")
    model = models.ColBERT(model_name_or_path=MODEL_NAME)

    print(f"Connecting to database: '{DB_FILE}'...")
    con = duckdb.connect(database=DB_FILE, read_only=False)

    model_id = get_or_create_model_entry(con, model)

    tables_to_process = [
        {"table": "single_turn_edits", "text_col": "full_edit_prompt"},
        {"table": "multi_turn_steps", "text_col": "prompt"},
        {"table": "edit_preferences", "text_col": "full_edit_prompt"},
    ]

    for item in tables_to_process:
        add_embeddings_to_table(con, model, model_id, item["table"], item["text_col"])

    print("\n--- Verification ---")
    print("Final schemas after embedding process:")

    for item in tables_to_process:
        print(f"\nDESCRIBE {item['table']};")
        print(con.execute(f"DESCRIBE {item['table']};").fetchdf())

    con.close()
    print("\nDatabase connection closed.")
    print(f"--- Process Complete ---")


if __name__ == "__main__":
    main()
