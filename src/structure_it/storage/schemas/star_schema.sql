-- 1. DIMENSION: The Source Context (The Document)
CREATE TABLE IF NOT EXISTS dim_documents (
    doc_id VARCHAR PRIMARY KEY,      -- Hash of source_url/content (or deterministic ID)
    source_type VARCHAR,             -- 'policy', 'academic_paper', 'meeting'
    title VARCHAR,
    url VARCHAR,
    metadata JSON,                   -- Flexible: author, date, version
    full_text_blob VARCHAR,          -- Raw markdown for fallback
    
    -- CDC / Audit Fields
    content_hash VARCHAR,            -- SHA256 of raw file content
    version INTEGER DEFAULT 1,       -- Incremental version number
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Deprecated in favor of first_seen_at? Keep for compat.
);

-- 2. FACT: The Atomic Items (The "Embeddable" Chunks)
-- This is the most important table. It normalizes the *concept* of an item
-- regardless of whether it's a Policy Requirement, a Code Function, or an Action Item.
CREATE TABLE IF NOT EXISTS fact_items (
    item_id VARCHAR PRIMARY KEY,
    doc_id VARCHAR REFERENCES dim_documents(doc_id),
    
    -- Polymorphic Categorization
    domain VARCHAR,             -- 'financial', 'hr', 'code'
    item_type VARCHAR,          -- 'requirement', 'function', 'decision'
    
    -- The Core Content (What we embed)
    content_text VARCHAR,       -- "Employees must submit receipts..."
    
    -- The Vector (For Semantic Search)
    -- using standard array for now, can be optimized with vss later if available
    embedding FLOAT[],          
    
    -- The Structured Data (For Filtering/LLM Context)
    properties JSON,            -- { "priority": "high", "roles": ["CFO"], "args": [...] }
    
    location_pointer VARCHAR    -- Page number, line number, or JSON path
);

-- 3. BRIDGE: Relationships (The "Knowledge Graph" in SQL)
-- Instead of a Graph DB, we use a many-to-many link table.
CREATE TABLE IF NOT EXISTS rel_links (
    source_item_id VARCHAR,
    target_item_id VARCHAR,
    link_type VARCHAR,          -- 'depends_on', 'conflicts_with', 'implements'
    description VARCHAR,        -- LLM generated reasoning: "Why are they linked?"
    PRIMARY KEY (source_item_id, target_item_id, link_type)
);

-- 4. AUDIT: Extraction History (CDC Log)
CREATE TABLE IF NOT EXISTS audit_document_changes (
    change_id INTEGER PRIMARY KEY, -- Auto-increment (DuckDB uses SEQUENCE implicitly for SERIAL or explicit sequence)
    doc_id VARCHAR REFERENCES dim_documents(doc_id),
    change_type VARCHAR,           -- 'create', 'update', 'unchanged'
    old_content_hash VARCHAR,
    new_content_hash VARCHAR,
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details VARCHAR
);
CREATE SEQUENCE IF NOT EXISTS seq_audit_changes START 1;

-- Indexes for common lookups
CREATE INDEX IF NOT EXISTS idx_fact_items_doc_id ON fact_items(doc_id);
CREATE INDEX IF NOT EXISTS idx_fact_items_domain ON fact_items(domain);
CREATE INDEX IF NOT EXISTS idx_dim_documents_url ON dim_documents(url);
CREATE INDEX IF NOT EXISTS idx_audit_doc_id ON audit_document_changes(doc_id);