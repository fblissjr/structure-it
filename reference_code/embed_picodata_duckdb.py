import argparse
import datetime

import duckdb
import pandas as pd
import torch
from pylate import models

# --- Configuration ---
# Sensible default batch size for a machine with high RAM.
DEFAULT_BATCH_SIZE = 512


def get_or_create_model_entry(con, model, model_name_arg: str) -> int:
    """
    Checks if the model exists in the metadata table. If not, it creates it.
    Returns the model's ID.
    """
    print("--- Registering embedding model in the database ---")
    model_name = model.model_card_data.base_model or model_name_arg
    embedding_dim = model.get_sentence_embedding_dimension()
    pooling_strategy = "mean"  # Standard for ColBERT-style models

    # Use "ON CONFLICT (unique_column) DO NOTHING" for idempotent inserts in DuckDB.
    con.execute(
        """
        INSERT INTO embedding_models (model_name, embedding_dimension, pooling_strategy)
        VALUES (?, ?, ?)
        ON CONFLICT (model_name) DO NOTHING;
        """,
        [model_name, embedding_dim, pooling_strategy],
    )

    # Retrieve the model_id, whether it was just inserted or already existed.
    result = con.execute(
        "SELECT model_id FROM embedding_models WHERE model_name = ?;", [model_name]
    ).fetchone()
    if result is None:
        raise RuntimeError(f"Failed to insert or retrieve model_id for {model_name}")

    model_id = result[0]
    print(f"Using Model ID: {model_id} for '{model_name}' (Dimension: {embedding_dim})")
    return model_id


def add_embeddings_to_table(
    con, model, model_id: int, table_name: str, text_column: str, batch_size: int
):
    """
    Fetches text, generates embeddings, and updates the table.
    """
    print(f"\n--- Processing table: '{table_name}' ---")

    try:
        # Only select rows that haven't been embedded yet.
        df = con.execute(
            f'SELECT rowid, "{text_column}" FROM {table_name} WHERE embedding_model_id IS NULL'
        ).fetchdf()
        print(f"Found {len(df)} rows to process.")
    except duckdb.CatalogException:
        print(f"⚠️ Warning: Table '{table_name}' or column '{text_column}' not found. Skipping.")
        return

    if df.empty or df[text_column].isnull().all():
        print("No new text data to embed. Skipping.")
        return

    print(f"Generating embeddings for '{text_column}' using batch size {batch_size}...")
    texts = df[text_column].tolist()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        is_query=False,
        show_progress_bar=True,
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
            prompt_embedding = temp.embedding,
            embedding_model_id = ?,
            updated_at = ?
        FROM temp_embeddings_df AS temp
        WHERE {table_name}.rowid = temp.rowid;
    """,
        [model_id, datetime.datetime.now()],
    )

    con.unregister("temp_embeddings_df")
    print(f"Successfully updated '{table_name}' with embeddings.")


def main():
    """Main function to parse arguments and run the embedding process."""
    parser = argparse.ArgumentParser(
        description="Generate and store text embeddings in a DuckDB database using PyLate.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--db-file",
        default="image_edits.duckdb",
        help="Path to the DuckDB database file.",
    )
    parser.add_argument(
        "-m",
        "--model-name",
        default="mixedbread-ai/mxbai-edge-colbert-v0-17m",
        help="Hugging Face model name or local path for the embedding model.",
    )
    parser.add_argument(
        "-b",
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Batch size for the encoding process. Increase for systems with high RAM/VRAM.",
    )
    args = parser.parse_args()

    print("--- Starting Embedding Generation with PyLate ---")
    print("\n--- Configuration ---")
    print(f"Database File:  {args.db_file}")
    print(f"Model Name:     {args.model_name}")
    print(f"Batch Size:     {args.batch_size}")
    print("---------------------\n")

    if torch.backends.mps.is_available():
        device = "mps"
        print("MPS (Apple Silicon GPU) is available. Using for acceleration.")
    else:
        device = "cpu"
        print("MPS not available. Running on CPU (this will be slower).")

    print(f"Loading local model via PyLate: '{args.model_name}'...")
    model = models.ColBERT(model_name_or_path=args.model_name, device=device)

    print(f"Connecting to database: '{args.db_file}'...")
    con = duckdb.connect(database=args.db_file, read_only=False)

    model_id = get_or_create_model_entry(con, model, args.model_name)

    tables_to_process = [
        {"table": "single_turn_edits", "text_col": "full_edit_prompt"},
        {"table": "multi_turn_steps", "text_col": "prompt"},
        {"table": "edit_preferences", "text_col": "full_edit_prompt"},
    ]

    for item in tables_to_process:
        add_embeddings_to_table(
            con, model, model_id, item["table"], item["text_col"], args.batch_size
        )

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
