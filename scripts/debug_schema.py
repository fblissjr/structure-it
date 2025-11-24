"""Initialize DB and show schema."""
from structure_it.storage.star_schema_storage import StarSchemaStorage
import duckdb

def init_and_inspect():
    # Initialize (creates tables)
    storage = StarSchemaStorage()
    storage.close()
    
    # Inspect
    conn = duckdb.connect("data/structure_it.duckdb")
    print("--- dim_documents ---")
    print(conn.execute("DESCRIBE dim_documents").fetchall())
    print("\n--- audit_document_changes ---")
    print(conn.execute("DESCRIBE audit_document_changes").fetchall())
    conn.close()

if __name__ == "__main__":
    init_and_inspect()

