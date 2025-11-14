# Data Directory

This directory contains sample datasets for testing and exploring structure-it's extraction capabilities across different domains.

## Datasets

### Policy Documents (`sample_policies/`)
Policy and compliance documents for requirement extraction:
- 13 policies across 5 domains (Financial, IT Security, HR, Legal, Compliance)
- Micro dataset (3 policies) for quick testing
- Full dataset (13 policies) for comprehensive testing

**Generators:**
- `scripts/generate_micro_dataset.py` - Generate 3 test policies
- `scripts/generate_full_dataset.py` - Generate 13 comprehensive policies
- `scripts/generate_metadata_only.py` - Create metadata without API calls

**Example Usage:**
```bash
uv run python examples/extract_policy_requirements.py \
  data/sample_policies/full_dataset/FIN-001_expense_reimbursement.md \
  --metadata data/sample_policies/full_dataset/metadata.json
```

### ArXiv Papers (`sample_arxiv/`)
AI/ML research papers from ArXiv for academic paper extraction:
- 8 papers across 6 AI focus areas
- Machine Learning, Computer Vision, NLP, Robotics, Neural Networks
- Various complexity levels (simple, medium, complex)

**Generator:**
- `scripts/generate_arxiv_dataset.py` - Generate 8 AI/ML papers

**Example Usage:**
```bash
uv run python examples/extract_academic_paper.py \
  data/sample_arxiv/2401.12345_efficient_llm_training.md
```

### Civic Documents (`sample_civic/`)
Local government meeting documents for civic data extraction:
- 8 documents across 4 types (agendas, minutes, proposals, resolutions)
- Township, village, county, and city documents
- Meeting schedules, decisions, proposals

**Generator:**
- `scripts/generate_civic_dataset.py` - Generate 8 civic documents

**Example Usage:**
```bash
# Extract meeting information using meeting schema
# (Custom extraction script needed - use base GeminiExtractor)
```

## Generating Datasets

All datasets support optional generation with the Gemini API:

```bash
# Generate sample datasets
uv run python scripts/generate_micro_dataset.py       # Policies (3 docs)
uv run python scripts/generate_full_dataset.py        # Policies (13 docs)
uv run python scripts/generate_arxiv_dataset.py       # ArXiv (8 papers)
uv run python scripts/generate_civic_dataset.py       # Civic (8 docs)

# Limit generation count
uv run python scripts/generate_full_dataset.py --count 5
uv run python scripts/generate_arxiv_dataset.py --count 3
```

**Note:** Dataset generation uses the Gemini API and consumes credits. Only generate when you need actual content for testing.

## Data Structure

Each dataset directory contains:
- **`metadata.json`** - Structured metadata for all documents (list format)
- **`metadata.csv`** - Same metadata in CSV format
- **`*.md`** - Generated document content (if generated)

All generators support:
- Configurable complexity levels
- Temperature variation for diversity
- Metadata-only mode (no API calls)
- Incremental generation

## Adding Custom Data

You can add your own documents to any dataset:

1. Place your document file in the appropriate directory
2. Add an entry to `metadata.json`
3. Run extraction as normal

## Storage

Extracted data can be stored in:
- **JSON Storage**: `./data/entities/{hash[:2]}/{hash}.json`
- **DuckDB**: `./data/structure_it.duckdb`

Configure paths via environment variables (see main README.md).
