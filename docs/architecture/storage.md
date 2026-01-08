# Storage Architecture

This document details the storage layer of `structure-it`, specifically the **Dimensional Context Model (Star Schema)** implementation.

## Overview

The storage layer is designed to:
1.  **Persist** extracted structured data.
2.  **Optimize** for LLM context retrieval (RAG).
3.  **Track** changes over time (CDC) to minimize re-extraction costs.

## Architecture: Star Schema (Dimensional Context Model)

We use a modified Star Schema approach implemented in DuckDB. This pivots from storing monolithic JSON blobs to storing "shredded" atomic facts that are easier for an LLM to query and reason about.

### Schema Design

#### 1. Dimension: `dim_documents`
Represents the source document (e.g., a PDF file, a web page).

| Column | Type | Description |
| :--- | :--- | :--- |
| `doc_id` | VARCHAR | Primary Key. Deterministic hash of source URL or content. |
| `source_type` | VARCHAR | E.g., 'policy', 'civic_meeting'. |
| `title` | VARCHAR | Document title. |
| `url` | VARCHAR | Source URL. |
| `metadata` | JSON | Original metadata blob. |
| `content_hash` | VARCHAR | SHA256 hash of the raw content (for CDC). |
| `version` | INTEGER | Version number (increments on content change). |
| `last_extracted_at`| TIMESTAMP | When it was last processed. |

#### 2. Fact: `fact_items`
Represents atomic units of information extracted from the document.

| Column | Type | Description |
| :--- | :--- | :--- |
| `item_id` | VARCHAR | Primary Key. |
| `doc_id` | VARCHAR | Foreign Key to `dim_documents`. |
| `domain` | VARCHAR | Domain context (e.g., 'financial', 'civic'). |
| `item_type` | VARCHAR | Type of atom (e.g., 'requirement', 'agenda_item', 'vote'). |
| `content_text` | VARCHAR | The core text (e.g., "The motion passed 5-0"). |
| `properties` | JSON | Structured attributes (e.g., `{"votes": {"aye": 5}}`). |
| `embedding` | FLOAT[] | Vector embedding for semantic search (optional). |

#### 3. Audit: `audit_document_changes`
Tracks the history of document ingestion.

| Column | Type | Description |
| :--- | :--- | :--- |
| `change_id` | INTEGER | Auto-increment ID. |
| `doc_id` | VARCHAR | Foreign Key to `dim_documents`. |
| `change_type` | VARCHAR | 'create', 'update'. |
| `old_content_hash` | VARCHAR | Previous hash. |
| `new_content_hash` | VARCHAR | New hash. |

## Key Features

### Change Data Capture (CDC)
To save LLM tokens and processing time, we implement CDC at the ingestion level.

1.  **Hash Check**: Before extraction, the system computes the SHA256 hash of the incoming document's text content.
2.  **Lookup**: It queries `dim_documents` to see if this `doc_id` exists and if the `content_hash` matches.
3.  **Decision**:
    *   **Match**: The document is unchanged. Extraction is skipped. `last_extracted_at` is updated.
    *   **No Match**: The document is new or changed. Extraction proceeds.
    *   **Version**: If changed, `version` is incremented, and the old `fact_items` are replaced.

### Hybrid Retrieval
The schema supports advanced RAG patterns:
*   **Semantic Search**: Using the `embedding` column in `fact_items`.
*   **Structured Filtering**: Using SQL on the `properties` JSON column.
    *   *Example:* "Find all *mandatory* (SQL) requirements about *password security* (Vector)."

## Developer Usage

### Storing Data
The `StarSchemaStorage` class handles the "shredding" logic automatically for supported schemas.

```python
storage = StarSchemaStorage()
await storage.store_entity(
    entity_id="...",
    source_type="civic_meeting",
    structured_data=my_pydantic_model.to_dict(),
    raw_content="..."
)
```

### Checking Status (CDC)
```python
is_new, has_changed = storage.check_document_status(doc_id, new_content_hash)
if not is_new and not has_changed:
    print("Skipping...")
```
