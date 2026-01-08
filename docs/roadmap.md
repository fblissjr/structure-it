# structure-it Roadmap

This document captures the long-term vision, research questions, and planned directions for structure-it based on design discussions and explorations. This is not a timeline or ordered plan—it's a collection of the nuanced ideas, approaches, and possibilities we're exploring.

## Core Philosophy

**structure-it is a research sandbox, not a production library.** The goal is to explore different approaches to structured data extraction and modeling for LLM-driven data pipelines. We experiment, discover patterns, document findings, and iterate based on real data rather than theoretical designs.

### Key Principles

1. **Let Structure Emerge**: Start with flexible JSON storage and discover patterns from real data before enforcing rigid schemas
2. **Modular & Extensible**: Components should be loosely coupled and easy to swap or extend
3. **LLM-First Design**: Optimize for LLM context window efficiency and consumption patterns
4. **Research Over Production**: Try different approaches, compare results, document findings
5. **Optional Complexity**: Keep core simple; add sophisticated patterns only when justified by data

## Completed Foundation

### Phase 1: Foundation ✅
- Base extractor interface with async support
- GeminiExtractor with structured output API
- Centralized configuration (no hardcoded models)
- 6 domain-specific Pydantic schemas
- BaseGenerator framework with 3 domain implementations
- Sample datasets across 3 domains (policies, ArXiv, civic)
- markitdown integration for PDFs and web content
- Development tooling and testing infrastructure

### Phase 2: Storage ✅
- Flexible storage abstraction (BaseStorage)
- JSON file storage (human-readable, schema-free)
- DuckDB storage (queryable, JSON columns)
- SHA256-based deterministic IDs (inspired by star-schema-llm-context)
- Full CRUD operations
- Parallel storage for comparison

### Active Exploration: Phase 3 - Modeling

**Goal**: Extract real data across domains, analyze patterns, iterate on schemas and storage approaches.

### Current Status: IN PROGRESS

We have the infrastructure. Now we need to:

1. **Extract Real Data** (5-10 examples per domain)
   - ✅ **Civic Documents**: Implemented robust Scrapy spider for CivicPlus (Generic) with CDC.
   - Web articles from different sources (tech blogs, news, tutorials)
   - Academic papers from different fields (ML, systems, theory)

2. **Analyze Stored Data**
   - Query DuckDB to find patterns in JSON structures
   - Which fields are consistently populated?
   - Which are sparse or domain-specific?
   - How does structure vary within domains?
   - What cross-domain patterns emerge?

3. **Document Findings**
   - Create `explorations/json-patterns-analysis.md`
   - Create `explorations/schema-evolution.md`
   - Compare JSON vs DuckDB trade-offs in practice
   - Identify candidates for normalization

4. **Iterate on Schemas**
   - Evolve schemas based on real data patterns
   - Add fields that consistently appear
   - Make sparse fields optional
   - Consider domain-specific vs shared fields

### Research Questions

**Storage & Modeling**:
- What's the right balance between structure and flexibility?
- When should we normalize JSON into typed columns?
- Do we need star schema, or is DuckDB with JSON columns sufficient?
- What query patterns emerge from real usage?
- How do different storage approaches affect LLM context assembly?

**Schema Design**:
- What patterns are common across all domains?
- What fields are domain-specific?
- How do schemas evolve as we encounter edge cases?
- Should we have a universal base schema beyond BaseSchema?
- What metadata is essential vs nice-to-have?

**LLM Context Optimization**:
- How should we structure data for efficient LLM consumption?
- What's the optimal balance between structured and unstructured context?
- Do we need different serialization formats for different LLM use cases?
- How do we handle large documents that exceed context windows?

**Cross-Domain Patterns**:
- Are there universal extraction patterns?
- How do relationships between entities work across domains?
- What metadata is universal (source, timestamps, authors)?
- Can we identify common entity types across domains?

## Future Modeling Approaches

### Star Schema (POC Implemented)

Inspired by [star-schema-llm-context](https://github.com/fblissjr/star-schema-llm-context/), we have implemented a Dimensional Context Model POC:

**Implemented Structure**:
```
Fact Tables:
- fact_items (atomic "shredded" items: requirements, sections, etc.)
- rel_links (relationships between items)

Dimension Tables:
- dim_documents (source metadata)
```

**Status**:
- `StarSchemaStorage` implemented
- Logic to "shred" Policy requirements and generic sections added
- Hybrid retrieval (SQL + Vector placeholder) API designed

**Challenges to Explore**:
- How to handle domain-specific dimensions?
- Trade-off: query efficiency vs schema flexibility
- How does it impact LLM context assembly?

### Graph Models (Future Exploration)

For relationship-heavy domains, graph structures might be more natural:

**Potential Use Cases**:
- Code documentation (function calls, dependencies)
- Academic papers (citations, influence networks)
- Meeting notes (action items → people → projects)
- Policy documents (requirements → regulations → compliance)

**Questions to Answer**:
- Which domains benefit most from graph representation?
- Do we need a graph database or can DuckDB handle it?
- How do we query graphs for LLM context?
- What's the learning curve vs benefit trade-off?

**Exploration Path**:
1. Identify relationship-heavy domains in our data
2. Model a subset as graph (nodes + edges)
3. Compare query patterns vs relational approach
4. Assess LLM context assembly complexity
5. Document trade-offs

### Hybrid Approaches

We're not limited to one approach. Consider:

**JSON + Star Schema Hybrid**:
- Star schema for queryable dimensions
- JSON columns for domain-specific nested data
- Best of both: structure where needed, flexibility where useful

**Document + Graph Hybrid**:
- Document storage for full content
- Graph overlay for relationships
- Query relationships, retrieve full documents

**Multi-Model Storage**:
- DuckDB for structured queries
- JSON files for human inspection
- Future: Graph database for specific use cases
- Each optimized for different access patterns

## Domain Expansion

### Implemented Domains (3)
1. **Policy Documents**: Requirements extraction, compliance
2. **ArXiv Papers**: Academic research, structured findings
3. **Civic Documents**: Government meetings, decisions

### Planned Domain Generators

**High Priority** (extend BaseGenerator):
- **ArticleGenerator**: Blog posts, news articles, tutorials
- **CodeDocGenerator**: API docs, README files, inline docs
- **MeetingGenerator**: Various meeting types, action items
- **MediaGenerator**: Podcast transcripts, video content

**Medium Priority**:
- **EmailGenerator**: Thread extraction, key decisions
- **ChatGenerator**: Slack/Discord conversations
- **ContractGenerator**: Legal agreements, terms
- **ReportGenerator**: Business reports, analytics

**Exploratory**:
- **CodeGenerator**: Source code with inline context
- **IssueGenerator**: GitHub issues, bug reports
- **PRGenerator**: Pull request descriptions, reviews

### Schema Evolution Strategy

**Current Approach**: 6 domain-specific schemas

**Future Considerations**:
- Universal metadata schema (all domains share)
- Domain-specific extensions (inherit from universal)
- Cross-domain entity recognition (people, orgs, locations)
- Relationship schemas (connects entities across domains)
- Temporal schemas (versioning, history)

**Questions**:
- Is inheritance the right pattern or composition?
- How do we handle fields that appear in multiple domains?
- Should we have a registry of entity types?
- How do we version schemas as they evolve?

## Extraction Evolution

### Current: Single-Pass Extraction
- One Gemini API call per document
- Structured output with Pydantic schema
- Works well for straightforward cases

### Future: Multi-Stage Extraction

**Chunked Extraction** (for long documents):
1. Split document into chunks
2. Extract from each chunk
3. Merge/reconcile results
4. Handle cross-chunk references

**Hierarchical Extraction**:
1. First pass: Extract high-level structure
2. Second pass: Detailed extraction per section
3. Third pass: Relationship extraction
4. Combine into unified structure

**Iterative Refinement**:
1. Initial extraction
2. Validation/quality check
3. Re-extract with refinements
4. Merge improvements

### Multimodal Extraction

**Current**: Text and PDF (via markitdown)

**Future**:
- **Images**: Diagrams, charts, infographics
- **Tables**: Structured data extraction
- **Mixed**: Text + images in context
- **Video**: Frames + transcript analysis
- **Audio**: Speech + acoustic features

**Challenges**:
- How to represent multimodal data in schemas?
- What metadata is needed for different modalities?
- How to handle modality-specific features?
- LLM context assembly with multiple modalities

## Storage Evolution

### Current Storage

**JSON Storage**:
- File-based: `./data/entities/{hash[:2]}/{hash}.json`
- Human-readable
- No schema enforcement
- Good for prototyping

**DuckDB Storage**:
- Database: `./data/structure_it.duckdb`
- JSON columns for flexibility
- Indexed queries
- Analytical capabilities

### Future Storage Considerations

**Partitioning Strategies**:
- By domain (separate tables per domain)
- By date (time-series partitions)
- By source type (URL vs file vs API)
- Hybrid (domain + date partitioning)

**Indexing Strategies**:
- Full-text search on content
- Embedding-based similarity search
- Temporal indexes
- Cross-domain indexes

**Compression & Archival**:
- Hot vs cold data separation
- Compressed archives for old data
- Tiered storage strategies
- Export formats for long-term preservation

**Versioning**:
- Document versioning (track changes over time)
- Schema versioning (handle evolution)
- Extraction versioning (re-extract with improved prompts)

## LLM Context Assembly

### Current: Direct Serialization
- `to_dict()` and `to_json()` methods
- Simple, direct representation
- No optimization for LLM consumption

### Future: Context Assembly Strategies

**Optimized Serialization**:
- Markdown format for better LLM comprehension
- Hierarchical structure with clear headings
- Selective field inclusion based on use case
- Token-optimized representations

**Context Window Management**:
- Truncation strategies (most important first)
- Summarization for long documents
- Reference by ID with lazy loading
- Chunked retrieval with ranking

**Cross-Document Context**:
- Assemble related documents
- Build knowledge graphs on-the-fly
- Temporal ordering (chronological context)
- Topic-based grouping

**Use-Case Specific Assembly**:
- Question answering (focused context)
- Summarization (comprehensive context)
- Analysis (comparative context)
- Generation (example-based context)

### Retrieval Strategies

**Current**: Direct queries by ID or source type

**Future RAG Patterns**:
- Embedding-based similarity search
- Hybrid search (keyword + semantic)
- Re-ranking strategies
- Contextual retrieval (consider conversation history)

**Cache Strategies**:
- Frequently accessed documents
- Pre-assembled context for common queries
- Embedding cache
- Query result cache

## Relationship Modeling

### Current: Minimal Relationships
- Source URLs
- Citation references (in academic schema)
- No explicit relationship modeling

### Future: Rich Relationship Modeling

**Entity Relationships**:
- Author → Document (created)
- Document → Document (cites, references)
- Person → Organization (employed by)
- Requirement → Regulation (mandated by)
- Meeting → Decision → Action Item

**Temporal Relationships**:
- Version history (Document A → Document A v2)
- Event sequences (Meeting 1 → Decision → Meeting 2)
- Evolution tracking (Requirement changes over time)

**Cross-Domain Relationships**:
- Policy → Academic Paper (implements research)
- Meeting → Policy (resulted in)
- Person appears in multiple domains
- Topics span domains

**Representation Options**:
1. Foreign keys in relational tables
2. Graph database (nodes + edges)
3. JSON references with IDs
4. Hybrid (structured + graph overlay)

## Framework Integration (Revisited)

### Previously Evaluated & Deferred

**genai-processors**:
- Evaluated: Complex modular processor framework
- Decision: Too complex for current needs
- Revisit when: We need sophisticated multi-stage pipelines
- Documentation: `explorations/genai-processors-analysis.md`

**langextract**:
- Evaluated: Entity extraction with source grounding
- Decision: Scope mismatch (entities vs generic schemas)
- Revisit when: We focus on entity-centric extraction
- Documentation: `explorations/langextract-analysis.md`

### Future Framework Considerations

**LangChain**:
- When: Building complex LLM chains
- Use case: Multi-step reasoning, agent-based extraction
- Trade-off: Added complexity vs powerful patterns

**LlamaIndex**:
- When: Need advanced RAG capabilities
- Use case: Document indexing, retrieval optimization
- Trade-off: Framework lock-in vs features

**DSPy**:
- When: Want to optimize prompts systematically
- Use case: Prompt engineering at scale
- Trade-off: Learning curve vs optimization benefits

**Custom Lightweight Approach** (current preference):
- Keep core simple
- Add patterns as needed
- Document what we learn
- Avoid framework lock-in until clearly beneficial

## Quality & Validation

### Current: Pydantic Validation
- Schema validation on extraction
- Type checking
- Required vs optional fields

### Future: Enhanced Quality

**Extraction Quality**:
- Confidence scores per field
- Missing data tracking
- Validation against source (citations exist)
- Consistency checks (dates, references)

**Data Quality Metrics**:
- Completeness (% fields populated)
- Accuracy (ground truth comparison)
- Consistency (cross-document)
- Freshness (age of data)

**Active Learning**:
- Flag low-confidence extractions
- Re-extract with refined prompts
- Build quality dataset for evaluation
- Iterative improvement loop

## Research Methodology

### Current Workflow
1. Design schema
2. Extract data
3. Store results
4. Inspect JSON

### Enhanced Research Workflow

**Data Collection**:
1. Extract diverse real-world examples
2. Store in both JSON and DuckDB
3. Tag with quality metadata
4. Version extractions

**Analysis**:
1. Query patterns in DuckDB
2. Visualize field population rates
3. Identify common structures
4. Compare across domains

**Schema Evolution**:
1. Document observed patterns
2. Propose schema changes
3. Test on existing data
4. Migrate with versioning

**Findings Documentation**:
1. Create exploration documents
2. Compare approaches with data
3. Document trade-offs discovered
4. Share learnings

### Exploration Documents to Create

**Planned**:
- `json-patterns-analysis.md` - Patterns from real data
- `schema-evolution.md` - How schemas changed with data
- `storage-comparison.md` - JSON vs DuckDB vs others
- `context-assembly-patterns.md` - LLM context strategies
- `cross-domain-patterns.md` - Universal patterns found
- `multimodal-learnings.md` - Insights from mixed media
- `relationship-modeling.md` - Graph vs relational findings

## Open Research Questions

### Architectural Questions
1. When is normalization worth the loss of flexibility?
2. How do we balance schema evolution with backward compatibility?
3. What's the optimal storage strategy for different query patterns?
4. Should we separate metadata from content storage?
5. How do we handle schema conflicts across domains?

### Extraction Questions
1. What prompts produce the most reliable extractions?
2. How do we handle ambiguous or missing information?
3. When should we use multi-stage extraction?
4. How do we validate extraction quality automatically?
5. What's the right granularity for structured data?

### LLM Context Questions
1. How should we format data for different LLM use cases?
2. What context assembly strategies work best?
3. How do we optimize for token efficiency?
4. Should we summarize or truncate long documents?
5. How do we handle temporal context (document history)?

### Performance Questions
1. At what scale do we need optimization?
2. When should we introduce caching?
3. Is DuckDB sufficient or do we need specialized stores?
4. How do we handle incremental updates efficiently?
5. What indexing strategies are most valuable?

### Research Process Questions
1. How do we systematically compare approaches?
2. What metrics indicate success?
3. How do we avoid premature optimization?
4. When do we know a pattern is worth generalizing?
5. How do we document learnings for future reference?

## Success Metrics (Qualitative)

This is a research project, not a product. Success means:

1. **Learning**: We understand trade-offs between approaches
2. **Documentation**: Findings are well-documented for others
3. **Flexibility**: Easy to try new approaches
4. **Patterns**: We've identified reusable patterns
5. **Data**: Real-world data validates or invalidates assumptions

**Not** success metrics:
- Performance benchmarks (unless blocking research)
- Feature completeness (intentionally incomplete)
- Production readiness (not the goal)
- User adoption (research sandbox, not library)

## Philosophical Notes

### Why This Approach?

**Start Flexible, Add Structure**:
Rather than designing the "perfect" schema upfront, we start with flexible JSON storage and discover what structure is actually needed through real data. This is more scientific—we let data reveal patterns rather than imposing them.

**Multiple Storage Backends**:
By supporting both JSON and DuckDB simultaneously, we can directly compare approaches with the same data. This makes trade-offs concrete rather than theoretical.

**Generators for Testing**:
Creating synthetic data generators (policies, ArXiv, civic) lets us quickly test extraction at scale before finding real data sources. The generators themselves are valuable outputs—they demonstrate domain knowledge.

**Domain Diversity**:
By exploring multiple domains (not just policies), we can find universal patterns vs domain-specific patterns. This prevents over-fitting to one domain.

**Research First**:
Treating this as research rather than product development gives us permission to try approaches that might "fail." Failure teaches us just as much as success.

### Inspiration Sources

**star-schema-llm-context**:
- SHA256-based deterministic IDs
- DuckDB for analytical queries
- Dimensional modeling concepts
- LLM context optimization focus

**Gemini Structured Outputs**:
- Pydantic schema integration
- Structured generation capabilities
- JSON schema generation

**Our Own Needs**:
- Policy requirements extraction (real use case)
- Academic paper analysis (real use case)
- Civic document understanding (real use case)
- Multi-domain extraction patterns

### What This Is Not

This is **not**:
- A production-ready library
- A one-size-fits-all solution
- Optimized for performance
- Feature-complete
- Stable API (we evolve based on learnings)

This **is**:
- A research sandbox
- An exploration of approaches
- Documentation of learnings
- Reusable patterns
- Foundation for future production systems

## Next Steps (Unordered)

These are possible next steps, not a roadmap:

- [ ] Extract 5-10 real examples per domain
- [ ] Create json-patterns-analysis.md from real data
- [x] Experiment with star schema for one domain (POC Implemented)
- [ ] Try graph modeling for citation networks
- [ ] Build context assembly utilities
- [ ] Add embedding-based retrieval
- [ ] Create more domain generators
- [ ] Explore multimodal extraction
- [ ] Implement chunked extraction for long docs
- [ ] Add quality metrics and validation
- [ ] Compare storage approaches with benchmarks
- [ ] Document schema evolution patterns
- [ ] Build cross-domain analysis tools
- [ ] Create visualization of extracted data
- [ ] Experiment with different serialization formats
- [ ] Add relationship extraction capabilities
- [ ] Build RAG patterns for specific use cases
- [ ] Create comprehensive comparison documents

## Contributing to This Vision

This roadmap is a living document. As we learn from data, discover new patterns, or identify better approaches, we update it. The goal is to maintain the "why" and "what if" alongside the "what" we've built.

**When adding to this roadmap**:
1. Focus on research questions, not implementation details
2. Document the reasoning, not just the idea
3. Reference real use cases or data that motivated it
4. Note trade-offs and open questions
5. Link to explorations or analyses

**When something moves from roadmap to reality**:
1. Create an exploration document
2. Document what we learned
3. Update this roadmap with findings
4. Add new questions that emerged
