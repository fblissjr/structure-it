# Star Schema Implementation (Dimensional Context Model)

This document describes the "Dimensional Context Model" approach for storing extracted data in a queryable format optimized for LLM context retrieval.

**Implementation**: `src/structure_it/storage/star_schema_storage.py`
**Schema**: `src/structure_it/storage/schemas/star_schema.sql`

## Overview

We use a "shredded" approach where structured documents are exploded into atomic items (facts) and context (dimensions). This enables:

1. **Hybrid Retrieval**: SQL filters + vector similarity
2. **Analytical Queries**: Aggregations across documents
3. **LLM Context Assembly**: Retrieve relevant atomic facts

## Database Schema Design

### Dimension Table: `dim_documents`

Represents source documents (PDFs, web pages, etc.)

```sql
CREATE TABLE dim_documents (
    doc_id VARCHAR PRIMARY KEY,      -- Hash of source_url/content
    source_type VARCHAR,             -- 'policy', 'academic_paper', 'meeting'
    title VARCHAR,
    url VARCHAR,
    metadata JSON,                   -- Flexible: author, date, version
    full_text_blob VARCHAR,          -- Raw markdown for fallback
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Fact Table: `fact_items`

Atomic units of information extracted from documents.

```sql
CREATE TABLE fact_items (
    item_id VARCHAR PRIMARY KEY,
    doc_id VARCHAR REFERENCES dim_documents(doc_id),

    -- Polymorphic Categorization
    domain VARCHAR,             -- 'financial', 'hr', 'code'
    item_type VARCHAR,          -- 'requirement', 'function', 'decision'

    -- The Core Content (What we embed)
    content_text VARCHAR,       -- "Employees must submit receipts..."

    -- The Vector (For Semantic Search)
    embedding FLOAT[],

    -- The Structured Data (For Filtering/LLM Context)
    properties JSON,            -- { "priority": "high", "roles": ["CFO"] }

    location_pointer VARCHAR    -- Page number, line number, or JSON path
);
```

## Implementation Pattern

### Shredding

A `PolicyRequirements` object with 50 requirements becomes:
- 1 row in `dim_documents`
- 50 rows in `fact_items`

Each fact is independently queryable and embeddable.

### Hybrid Retrieval

Combine SQL filters with vector similarity search:

```python
async def retrieve_context(self, query_vector, filters):
    sql = """
        SELECT content_text, properties
        FROM fact_items
        WHERE json_extract_string(properties, '$.type') = ?
        ORDER BY array_cosine_similarity(embedding, ?) DESC
    """
    # Execute with filter value and query vector
```

## Analytical Queries

Example analytics enabled by the star schema:

```python
class StarSchemaAnalytics:
    """Analytics queries leveraging star schema."""

    def papers_by_organization(self, limit: int = 20):
        """Top organizations by paper count."""
        return self.conn.execute("""
            SELECT
                o.name as organization,
                COUNT(DISTINCT e.extraction_id) as paper_count,
                array_agg(DISTINCT e.title) as papers
            FROM fact_extractions e
            JOIN dim_authors a ON e.author_id = a.author_id
            JOIN dim_organizations o ON a.organization_id = o.org_id
            WHERE e.entity_type = 'academic_paper'
            GROUP BY o.name
            ORDER BY paper_count DESC
            LIMIT ?
        """, [limit]).fetchall()

    def cross_domain_topics(self):
        """Topics that appear across multiple domains."""
        return self.conn.execute("""
            SELECT
                t.topic_name,
                array_agg(DISTINCT e.entity_type) as domains,
                COUNT(DISTINCT e.entity_type) as domain_count,
                COUNT(*) as total_mentions
            FROM fact_extraction_topics et
            JOIN dim_topics t ON et.topic_id = t.topic_id
            JOIN fact_extractions e ON et.extraction_id = e.extraction_id
            GROUP BY t.topic_name
            HAVING COUNT(DISTINCT e.entity_type) > 1
            ORDER BY domain_count DESC, total_mentions DESC
        """).fetchall()
```

## Migration from JSON/DuckDB

```python
async def migrate_to_star_schema():
    """Migrate existing data to star schema."""

    duckdb_storage = DuckDBStorage()
    star_storage = StarSchemaStorage()

    entities = await duckdb_storage.query_entities(limit=10000)

    for entity in entities:
        await star_storage.store_entity(
            entity_id=entity['entity_id'],
            source_type=entity['source_type'],
            source_url=entity['source_url'],
            raw_content=entity.get('raw_content', ''),
            structured_data=entity['structured_data'],
            metadata=entity.get('metadata')
        )
```

## Trade-offs

### Advantages
- Fast analytical queries across documents
- Efficient LLM context retrieval
- Natural fit for RAG patterns
- SQL-based filtering + vector search

### Challenges
- Schema more rigid than pure JSON
- Shredding logic per domain type
- Query complexity for cross-domain patterns

## Related

- [Storage Architecture](storage.md) - CDC and overall storage design
- [Graph Modeling](graph-modeling.md) - Alternative for relationship-heavy data
- [RAG Patterns](../implementation/rag-patterns.md) - Retrieval strategies
