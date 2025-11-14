# Sample Policy Datasets

This directory contains metadata and (optionally) generated policy documents for testing the policy requirements extraction system.

## Directory Structure

```
data/sample_policies/
├── README.md                    # This file
├── micro_dataset/               # 3 policies for quick testing
│   ├── metadata.json           # Policy metadata (list format)
│   ├── metadata.csv            # Same metadata in CSV format
│   └── *.md                    # Generated policy documents (if generated)
└── full_dataset/                # 13 policies across all domains
    ├── metadata.json           # Policy metadata (list format)
    ├── metadata.csv            # Same metadata in CSV format
    └── *.md                    # Generated policy documents (if generated)
```

## Datasets

### Micro Dataset (3 policies)

Quick testing dataset with minimal API usage:

- **FIN-001**: Expense Reimbursement Policy (simple)
- **IT-001**: Access Control Policy (medium)
- **HR-001**: Code of Conduct (simple)

### Full Dataset (13 policies)

Comprehensive dataset covering all domains:

**Financial (3)**:
- FIN-001: Expense Reimbursement Policy (simple)
- FIN-002: Capital Expenditure Approval Policy (medium)
- FIN-003: Financial Authority Matrix and Approval Limits (complex)

**IT Security (3)**:
- IT-001: Acceptable Use Policy (simple)
- IT-002: Access Control and Identity Management Policy (medium)
- IT-003: Information Security and Data Protection Policy (complex)

**HR (3)**:
- HR-001: Code of Conduct (simple)
- HR-002: Remote Work and Flexible Work Arrangements (medium)
- HR-003: Performance Management and Employee Development (complex)

**Legal (2)**:
- LEG-001: Conflict of Interest and Disclosure Policy (medium)
- LEG-002: Records Retention and Document Management Policy (complex)

**Compliance (2)**:
- COMP-001: Privacy and Data Protection Compliance (medium)
- COMP-002: Anti-Corruption and Ethical Business Practices (complex)

## Generating Metadata

To create/update metadata files without generating policy content:

```bash
# Generate both micro and full dataset metadata
uv run python scripts/generate_metadata_only.py

# Generate only micro dataset
uv run python scripts/generate_metadata_only.py --micro

# Generate only full dataset
uv run python scripts/generate_metadata_only.py --full
```

This creates metadata files **without** calling the Gemini API, saving API credits.

## Generating Policy Content

To generate actual policy documents (uses API credits):

```bash
# Generate micro dataset (3 policies)
uv run python scripts/generate_micro_dataset.py

# Generate full dataset (13 policies)
uv run python scripts/generate_full_dataset.py

# Generate specific number of policies
uv run python scripts/generate_full_dataset.py --count 5
```

**Note**: Policy generation calls the Gemini API and uses API credits. Only run when you need actual policy content.

## Using the Datasets

### With Metadata Only

If you only have metadata files (no generated policies), you can:
1. Manually create policy markdown files matching the filenames in metadata
2. Use existing policy PDFs and convert them to markdown
3. Reference the metadata structure for planning

### With Generated Policies

If you've generated policy content:

```bash
# Extract requirements from a single policy
uv run python examples/extract_policy_requirements.py \
  data/sample_policies/full_dataset/FIN-001_expense_reimbursement.md \
  --metadata data/sample_policies/full_dataset/metadata.json

# The script will automatically find FIN-001 metadata from the list
```

### Metadata Format

The metadata files contain arrays of policy objects:

```json
[
  {
    "policy_id": "FIN-001",
    "policy_title": "Expense Reimbursement Policy",
    "policy_type": "Financial",
    "policy_version": "1.0",
    "effective_date": "2024-01-15",
    "filename": "FIN-001_expense_reimbursement.md",
    "complexity": "simple",
    "generated_at": "2024-01-15T10:00:00.000000"
  },
  ...
]
```

The extraction script automatically matches filenames to find the correct metadata entry.

## Complexity Levels

- **Simple**: 5-10 clear requirements, 2-3 pages, straightforward language
- **Medium**: 10-15 requirements with conditions, 5-7 pages, professional language
- **Complex**: 20+ requirements with nested conditions, 10-15 pages, technical/legal language

## Best Practices

1. **Start with metadata**: Generate metadata first to plan your dataset structure
2. **Generate selectively**: Only generate policy content when needed for testing
3. **Use micro dataset**: For quick iteration and testing
4. **Use full dataset**: For comprehensive testing across all domains
5. **Manual policies**: You can create your own policies and add them to the metadata

## Adding Custom Policies

To add your own policy to the dataset:

1. Create the policy markdown file (e.g., `CUSTOM-001_my_policy.md`)
2. Edit `metadata.json` to add an entry:
   ```json
   {
     "policy_id": "CUSTOM-001",
     "policy_title": "My Custom Policy",
     "policy_type": "Financial",
     "policy_version": "1.0",
     "effective_date": "2024-01-15",
     "filename": "CUSTOM-001_my_policy.md",
     "complexity": "medium",
     "generated_at": "2024-01-15T10:00:00.000000"
   }
   ```
3. Run extraction as normal

## Cleaning Up

To remove generated policies but keep metadata:

```bash
# Remove all .md files but keep metadata
rm data/sample_policies/micro_dataset/*.md
rm data/sample_policies/full_dataset/*.md
```

To start fresh:

```bash
# Remove everything and regenerate metadata
rm -rf data/sample_policies/
uv run python scripts/generate_metadata_only.py
```
