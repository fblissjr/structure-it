# LangExtract: Analysis and Fit Assessment

**Date**: 2025-11-07
**Status**: Analysis Complete - Integration Deferred
**Context**: Phase 1-2 Foundation - Evaluating specialized extraction tools

---

## What is LangExtract?

**LangExtract** is Google's open-source Python library for extracting structured information from text with precise source grounding. It provides entity extraction capabilities with character-level alignment back to the source document.

### Repository
- **GitHub**: https://github.com/google/langextract
- **Package**: Available via pip
- **License**: Apache 2.0
- **Maintenance**: Active Google project
- **Python**: 3.11+

### Core Purpose

LangExtract focuses on a specific problem: **extracting entities and relationships from text while maintaining provenance** - knowing exactly where in the source document each extracted piece of information came from.

**Primary Use Cases**:
- Entity extraction from long documents
- Information extraction with source citations
- Document annotation and highlighting
- Interactive extraction visualization

---

## How Does LangExtract Work?

### Architecture Overview

**Core Components**:

1. **Extraction Framework**:
   - Uses LLMs (Gemini, OpenAI, Ollama) for entity extraction
   - Provider abstraction layer for multi-LLM support
   - Prompt template system for extraction instructions
   - Few-shot example-based learning

2. **Source Grounding System**:
   - Character-level alignment to source text
   - Span annotations (start/end positions)
   - Multiple spans per entity (repeated mentions)
   - Confidence scoring per extraction

3. **Document Processing**:
   - Text chunking for long documents
   - Sliding window with overlap
   - Parallel chunk processing
   - Result aggregation and deduplication

4. **Visualization**:
   - Interactive HTML output
   - Highlights extracted entities in context
   - Shows entity relationships
   - Provenance tracking UI

### Data Model

**Key Classes**:

```python
class Extraction:
    """Extracted entity with source grounding."""
    text: str                    # Extracted entity text
    label: str                   # Entity type/label
    spans: list[tuple[int, int]] # Character positions in source
    confidence: float            # Extraction confidence
    metadata: dict               # Additional properties

class AnnotatedDocument:
    """Document with extraction results."""
    text: str                    # Original source text
    extractions: list[Extraction]
    relationships: list[Relationship]
    metadata: dict
```

### Extraction Process

1. **Template Definition**: Define extraction schema via prompt template
2. **Example Provision**: Provide few-shot examples of desired extractions
3. **Document Chunking**: Break long documents into processable chunks
4. **Parallel Extraction**: Extract entities from each chunk
5. **Grounding**: Align extracted text to source positions
6. **Aggregation**: Merge results across chunks
7. **Visualization**: Generate interactive HTML view

### Technology Stack

**Dependencies**:
- `google-genai` - Gemini API client (primary)
- `openai` - OpenAI API support (optional)
- `pydantic` - Data validation
- `jinja2` - Template rendering
- `beautifulsoup4` - HTML processing for visualization
- Provider plugins for different LLMs

---

## Relationship to Our Project

### Similarities

1. **LLM-Powered Extraction**:
   - Both use LLMs (Gemini) for structured extraction
   - Both aim to structure unstructured data
   - Both use Pydantic for data modeling

2. **Multi-Provider Support**:
   - LangExtract: Gemini, OpenAI, Ollama via providers
   - Our project: Currently Gemini, designed for multi-provider (Phase 4+)

3. **Python-First**:
   - Both are Python libraries
   - Both use modern Python (3.11+)
   - Both use async patterns

### Differences

**Extraction Approach**:
- **LangExtract**: Few-shot examples + prompt templates → entity extraction
- **Our project**: Pydantic schemas + structured output API → generic extraction

**Scope**:
- **LangExtract**: Specialized for entity extraction with source grounding
- **Our project**: Generic structured data extraction (recipes, papers, meetings, etc.)

**Output Focus**:
- **LangExtract**: Entities + character positions (provenance)
- **Our project**: Structured objects conforming to schemas (no provenance tracking)

**Document Handling**:
- **LangExtract**: Chunking strategy for long documents built-in
- **Our project**: Single-pass extraction (no chunking yet)

**Visualization**:
- **LangExtract**: Interactive HTML highlighting
- **Our project**: No visualization (focused on data pipeline)

---

## Integration Considerations

### Could LangExtract Replace Our GeminiExtractor?

**Answer**: No, different use cases.

**Why Not**:
1. **Scope mismatch**: LangExtract is entity-focused, we want generic structured output
2. **API differences**: LangExtract uses templates/examples, we use Pydantic schemas
3. **Gemini structured output**: We leverage native structured output API, LangExtract uses prompt engineering
4. **Provenance overhead**: We don't need character-level grounding for most use cases

### Could LangExtract Complement Our Project?

**Answer**: Yes, for specific use cases.

**Scenarios Where LangExtract Adds Value**:

1. **Academic Paper Extraction with Citations**:
   - Extract claims with exact source sentences
   - Track which paragraph supports which finding
   - Useful for fact-checking and attribution

2. **Legal Document Analysis**:
   - Extract clauses with precise positions
   - Reference specific contract sections
   - Generate annotated agreements

3. **Long Document Processing**:
   - Built-in chunking strategy
   - Parallel processing of chunks
   - Could handle documents our single-pass approach can't

4. **Interactive Exploration**:
   - HTML visualization for debugging
   - Useful during schema development
   - Shows what LLM "sees"

### Integration Architecture (If We Wanted To)

**Option 1: Separate Extractor**:
```python
class LangExtractExtractor(BaseExtractor[TSchema]):
    """Adapter for LangExtract."""
    def __init__(self, schema: type[TSchema]):
        self.langextract_engine = ...
        super().__init__(schema)

    async def extract(self, content: str) -> TSchema:
        # Convert Pydantic schema to LangExtract template
        template = self._schema_to_template(self.schema)
        # Extract with grounding
        annotated_doc = await self.langextract_engine.extract(content, template)
        # Convert to Pydantic model
        return self._annotations_to_schema(annotated_doc, self.schema)
```

**Option 2: Hybrid Approach**:
```python
# Use LangExtract for entity-heavy tasks
from langextract import LangExtractor

# Use our GeminiExtractor for structured schemas
from structure_it import GeminiExtractor

# Choose based on use case
if use_case == "entity_extraction_with_provenance":
    extractor = LangExtractExtractor(...)
else:
    extractor = GeminiExtractor(...)
```

**Option 3: Chunking Strategy Adoption**:
```python
# Borrow LangExtract's chunking approach
from langextract.chunking import chunk_document

# Apply to our extractor
class ChunkedGeminiExtractor(GeminiExtractor):
    async def extract(self, content: str) -> TSchema:
        chunks = chunk_document(content, max_size=4000, overlap=200)
        results = await asyncio.gather(*[
            super().extract(chunk) for chunk in chunks
        ])
        return self._merge_results(results)
```

---

## Comparison with Our Approach

### LangExtract vs. Direct Gemini API (Our Approach)

| Aspect | LangExtract | Our GeminiExtractor |
|--------|-------------|---------------------|
| **Extraction Method** | Few-shot + templates | Pydantic schema + structured output API |
| **Output Type** | Entities with spans | Generic structured objects |
| **Provenance** | ✅ Character-level | ❌ Not tracked |
| **Long Documents** | ✅ Built-in chunking | ❌ Single-pass (may hit limits) |
| **Schema Definition** | Template strings | Pydantic classes |
| **LLM Support** | Gemini, OpenAI, Ollama | Gemini (extensible) |
| **Complexity** | Higher (templates, examples, chunking) | Lower (direct API) |
| **Flexibility** | Entity extraction focus | Any structured output |
| **Visualization** | ✅ HTML highlighting | ❌ None |
| **Use Case Fit** | Entity-heavy documents | Generic data structuring |

### LangExtract vs. GenAI Processors

| Aspect | LangExtract | GenAI Processors |
|--------|-------------|------------------|
| **Scope** | Entity extraction library | Full pipeline framework |
| **Abstraction** | High-level (extract entities) | Low-level (processor composition) |
| **Composability** | Limited | Extensive (chain/parallel) |
| **Learning Curve** | Medium | High |
| **Use Case** | Specific (entities) | General (any pipeline) |

### Unique Value of LangExtract

**What LangExtract Does That We Don't**:
1. **Source Grounding**: Character positions for every extraction
2. **Chunking Strategy**: Production-ready long document handling
3. **Interactive Viz**: HTML highlighting for debugging/exploration
4. **Few-Shot Learning**: Template-based extraction (alternative to schemas)

**What We Do That LangExtract Doesn't**:
1. **Generic Schemas**: Any Pydantic model, not just entities
2. **Structured Output API**: Native Gemini feature for guaranteed format
3. **Data Modeling Focus**: Storage, retrieval, modeling (Phase 2-3)
4. **Research-Oriented**: Comparing modeling approaches, not production extraction

---

## Recommendation

### Decision: Document but Defer Integration

**Rationale**:

1. **Scope Mismatch**: LangExtract is entity-extraction-focused, we're building generic structured extraction
2. **API Incompatibility**: Different extraction paradigms (templates vs. schemas)
3. **Complexity Not Justified**: We can achieve our goals with simpler direct API approach
4. **Phase 1-3 Don't Need It**: Current phases focus on extraction + modeling, not provenance

### When to Revisit

**Consider LangExtract if**:
1. **Provenance becomes critical**: Need to cite exact source positions
2. **Long documents**: Hitting token limits on single-pass extraction
3. **Entity-heavy use cases**: Academic papers with many citations, legal docs
4. **Interactive debugging**: Want visualization during schema development

**Trigger points**:
- User explicitly requests source grounding
- Documents exceed 10k tokens regularly
- Entity extraction becomes primary use case
- Need chunking strategy for production

### Current Status

**Implementation**: None - analysis only

**Documentation**: This document serves as reference

**Dependencies**: Not added to pyproject.toml (can add to optional extras if needed later)

**Next Steps**: Proceed with our schema-driven approach, revisit if requirements change

---

## Potential Future Integration

### If We Integrate (Future Phase)

**Scenario 1: Hybrid Extractors**
```python
# In pyproject.toml
[project.optional-dependencies]
langextract = ["langextract>=1.0.0"]

# In code
try:
    from langextract import LangExtractor
    HAS_LANGEXTRACT = True
except ImportError:
    HAS_LANGEXTRACT = False

# Provide LangExtract-based extractor only if available
if HAS_LANGEXTRACT:
    class GroundedExtractor(BaseExtractor):
        """Entity extraction with source grounding."""
        ...
```

**Scenario 2: Chunking Strategy Adoption**
```python
# Borrow just the chunking logic, not the full framework
from structure_it.utils.chunking import chunk_text  # Inspired by LangExtract

class LongDocumentExtractor(GeminiExtractor):
    async def extract(self, content: str) -> TSchema:
        if len(content) > self.max_tokens:
            return await self._chunked_extract(content)
        return await super().extract(content)
```

**Scenario 3: Visualization for Debugging**
```python
# Use LangExtract viz for schema development
from langextract.viz import highlight_extractions

def debug_extraction(content: str, extracted: TSchema):
    """Visualize what was extracted."""
    # Convert Pydantic result to LangExtract format
    annotations = schema_to_annotations(extracted)
    # Generate HTML
    html = highlight_extractions(content, annotations)
    # Open in browser
    webbrowser.open(html)
```

---

## Key Insights

### Core Difference

**LangExtract**: "What entities are in this text, and where exactly?"

**Our Project**: "What structured data can I extract from this content?"

**Analogy**:
- **LangExtract**: Like Named Entity Recognition (NER) with source highlighting
- **Our Project**: Like form filling from unstructured data

### Mental Model

Think of LangExtract as:
- **spaCy/Stanza**: For LLM-powered entity extraction
- **Hypothesis.is**: For annotating documents
- **Information extraction**: From NLP research

We're building:
- **Pydantic validation**: For LLM outputs
- **Data pipeline**: From unstructured to structured
- **Data modeling**: For LLM context management

### The Bottom Line

**LangExtract is excellent at what it does (entity extraction with provenance), but it's not what we're building.**

We're focused on:
1. Generic structured extraction (any schema)
2. Data modeling approaches for LLM context
3. Storage and retrieval optimization
4. Research into modeling patterns

LangExtract could be a tool in our toolkit for specific use cases, but it's not core to our research questions.

---

## Usage in Our Project

### Current Role: None

We are **not using** LangExtract in structure-it at this time.

### Why Not?

1. **Different goals**: We want generic schema-driven extraction, not entity extraction
2. **Gemini structured output**: Our approach uses native API feature that guarantees format compliance
3. **Simpler is better**: Direct API calls are clearer for research and iteration
4. **Flexibility**: Pydantic schemas give us more control over output structure

### Potential Future Use

**Chunking inspiration**: If we hit long document limits, we could adapt LangExtract's chunking strategy without adopting the full framework.

**Example scenario**:
```python
# If we implement chunking later
class LongDocumentExtractor(GeminiExtractor):
    """Extractor that handles long documents via chunking."""

    # Inspired by LangExtract's approach but adapted for our schemas
    async def extract(self, content: str) -> TSchema:
        if self._estimate_tokens(content) > 30000:
            # Chunk the document
            chunks = self._chunk_document(content)
            # Extract from each chunk
            results = await asyncio.gather(*[
                super().extract(chunk) for chunk in chunks
            ])
            # Merge results
            return self._merge_extractions(results)
        else:
            # Normal single-pass extraction
            return await super().extract(content)
```

### Decision Framework

**Use LangExtract if**:
- Need exact character positions for provenance
- Working with very long documents (>50k tokens)
- Primary use case is entity extraction
- Want interactive HTML visualization

**Use our GeminiExtractor if**:
- Want generic structured data (not just entities)
- Documents fit in context window
- Need flexibility in output schema
- Prefer simpler, more direct approach

**For most of our use cases**: Our approach is better suited.

---

## References

- **LangExtract GitHub**: https://github.com/google/langextract
- **Documentation**: See `coderef/langextract/` for local reference
- **Related**: See `explorations/genai-processors-analysis.md` for comparison with another Google tool

---

## Conclusion

**Status**: Documented, integration deferred

**Decision**: Continue with our schema-driven Gemini structured output approach

**Rationale**: LangExtract solves a different problem (entity extraction + provenance) than our core goals (generic structured extraction + data modeling research)

**Revisit if**: Provenance tracking or long document chunking becomes critical

**Key Takeaway**: Excellent specialized tool for entity extraction with source grounding, but our project needs generic schema-driven extraction for diverse domains (papers, articles, meetings, media, code docs). Different tools for different jobs.
