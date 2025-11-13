# Policy Requirements Extraction Guide

This guide explains how to extract structured requirements from policy and procedure documents using the `PolicyRequirementsExtractor`.

## Overview

The Policy Requirements extraction system converts unstructured policy PDFs into structured, queryable requirements data. It identifies:

- **Mandatory requirements**: "must", "shall", "will", "required to"
- **Recommended practices**: "should", "recommended", "encouraged"
- **Prohibitions**: "must not", "shall not", "prohibited", "forbidden"

Each requirement includes:
- The requirement statement
- Who/what it applies to (roles, departments, systems)
- Conditions (when it applies)
- Exceptions (when it doesn't apply)
- Regulatory basis (SOX, GDPR, PCI-DSS, HIPAA, etc.)

## Quick Start

### Installation

```bash
# Install structure-it with dev dependencies
uv pip install -e ".[dev]"

# Set your Google API key
export GOOGLE_API_KEY='your-key-here'
```

### Basic Usage

```python
import asyncio
from structure_it.extractors import PolicyRequirementsExtractor


async def extract_policy():
    extractor = PolicyRequirementsExtractor()

    requirements = await extractor.extract(
        pdf_path="path/to/policy.pdf",
        policy_metadata={
            "policy_id": "FIN-001",
            "policy_title": "Expense Reimbursement Policy",
            "policy_type": "Financial",
            "policy_version": "1.0",
            "effective_date": "2024-01-15",
        }
    )

    # Print summary
    print(f"Extracted {requirements.total_requirements} requirements")
    print(f"  Mandatory: {requirements.total_mandatory}")
    print(f"  Recommended: {requirements.total_recommended}")
    print(f"  Prohibited: {requirements.total_prohibited}")

    # Iterate through requirements
    for req in requirements.requirements:
        print(f"\n{req.requirement_id}: {req.statement}")
        if req.applies_to:
            print(f"  Applies to: {', '.join(req.applies_to)}")
        if req.conditions:
            print(f"  Conditions: {', '.join(req.conditions)}")
        if req.regulatory_basis:
            print(f"  Regulatory: {', '.join(req.regulatory_basis)}")

    # Save to JSON
    with open("requirements.json", "w") as f:
        f.write(requirements.to_json())


asyncio.run(extract_policy())
```

## Command Line Usage

The `extract_policy_requirements.py` script provides a CLI interface:

### Interactive Mode

```bash
uv run python examples/extract_policy_requirements.py policy.pdf
```

The script will prompt you for:
- Policy ID
- Policy Title
- Policy Type (Financial, IT Security, HR, Legal, Compliance)
- Version (optional)
- Effective Date (optional)

### With Command Line Arguments

```bash
uv run python examples/extract_policy_requirements.py policy.pdf \
  --policy-id FIN-001 \
  --policy-title "Expense Reimbursement Policy" \
  --policy-type Financial \
  --policy-version "1.0" \
  --effective-date "2024-01-15" \
  --output requirements.json
```

### With Metadata File

```bash
# Create metadata.json
cat > metadata.json <<EOF
{
  "policy_id": "FIN-001",
  "policy_title": "Expense Reimbursement Policy",
  "policy_type": "Financial",
  "policy_version": "1.0",
  "effective_date": "2024-01-15"
}
EOF

# Extract with metadata file
uv run python examples/extract_policy_requirements.py policy.pdf \
  --metadata metadata.json
```

## Policy Types and Domain-Specific Extraction

The extractor uses domain-specific prompts to optimize extraction quality:

### Financial Policies

Focuses on:
- Approval thresholds and authorization levels
- Spending limits and budget controls
- Financial reporting requirements
- Audit and documentation requirements

**Example policies:**
- Expense Reimbursement
- Capital Expenditure Approval
- Budget Management
- Vendor Payment Terms

### IT Security Policies

Focuses on:
- Access controls and authentication requirements
- Technical controls (encryption, logging, monitoring)
- Incident response procedures
- System configuration requirements

**Example policies:**
- Access Control Policy
- Incident Response Policy
- Data Classification Policy
- Acceptable Use Policy

### HR Policies

Focuses on:
- Employee obligations and conduct
- Performance criteria and expectations
- Leave and absence requirements
- Grievance and disciplinary procedures

**Example policies:**
- Code of Conduct
- Performance Management
- Remote Work Policy
- Leave and Absence Policy

### Legal Policies

Focuses on:
- Regulatory obligations and citations
- Disclosure requirements
- Compliance deadlines
- Risk statements and prohibitions

**Example policies:**
- Conflict of Interest
- Records Retention
- Privacy Policy
- Whistleblower Policy

### Compliance Policies

Focuses on:
- Regulatory framework references
- Monitoring and reporting requirements
- Audit and verification procedures
- Certification requirements

**Example policies:**
- Privacy and Data Protection Compliance
- Anti-Corruption Policy
- Export Compliance
- Anti-Money Laundering

## Schema Reference

### PolicyRequirement

Individual requirement extracted from a policy.

**Fields:**
- `requirement_id` (str): Unique ID (e.g., "FIN-001-REQ-001")
- `statement` (str): The requirement text
- `requirement_type` (str): "mandatory", "recommended", or "prohibited"
- `source_policy_id` (str): Parent policy ID
- `source_section` (str | None): Section reference
- `applies_to` (list[str]): Roles, departments, systems this applies to
- `conditions` (list[str]): When this requirement applies
- `exceptions` (list[str]): When this requirement does NOT apply
- `regulatory_basis` (list[str]): Referenced regulations (SOX, GDPR, etc.)
- `priority` (str | None): "high", "medium", "low"
- `enforcement_mechanism` (str | None): How compliance is verified

### PolicyRequirements

Collection of requirements from a single policy.

**Fields:**
- `policy_id` (str): Policy identifier
- `policy_title` (str): Policy name
- `policy_type` (str): Policy domain
- `policy_version` (str | None): Version string
- `effective_date` (str | None): Effective date
- `requirements` (list[PolicyRequirement]): All extracted requirements
- `total_mandatory` (int): Count of mandatory requirements
- `total_recommended` (int): Count of recommended requirements
- `total_prohibited` (int): Count of prohibited requirements
- `extraction_timestamp` (str | None): When extraction occurred
- `model_used` (str | None): Gemini model used
- `extraction_notes` (list[str]): Warnings or issues during extraction

**Methods:**
- `update_counts()`: Recalculate summary counts
- `total_requirements` (property): Total number of requirements
- `to_dict()`: Convert to dictionary
- `to_json()`: Convert to JSON string

## Advanced Usage

### Custom Model Selection

```python
# Use gemini-2.5-pro for more complex policies
extractor = PolicyRequirementsExtractor(
    model_name="gemini-2.5-pro"
)

requirements = await extractor.extract(
    pdf_path="complex_policy.pdf",
    policy_metadata=metadata,
)
```

### Batch Processing

```python
import asyncio
from pathlib import Path
from structure_it.extractors import PolicyRequirementsExtractor


async def batch_extract(policies: list[tuple[Path, dict]]):
    """Extract requirements from multiple policies."""
    extractor = PolicyRequirementsExtractor()

    results = await extractor.extract_batch(policies)

    for pdf_path, metadata in policies:
        idx = policies.index((pdf_path, metadata))
        result = results[idx]

        if isinstance(result, Exception):
            print(f"Failed to extract {metadata['policy_id']}: {result}")
        else:
            print(f"Extracted {result.total_requirements} from {metadata['policy_id']}")

    return results


# Example usage
policies = [
    (Path("fin_001.pdf"), {"policy_id": "FIN-001", "policy_title": "...", "policy_type": "Financial"}),
    (Path("it_001.pdf"), {"policy_id": "IT-001", "policy_title": "...", "policy_type": "IT Security"}),
    (Path("hr_001.pdf"), {"policy_id": "HR-001", "policy_title": "...", "policy_type": "HR"}),
]

results = asyncio.run(batch_extract(policies))
```

### Filtering and Analysis

```python
# Filter by requirement type
mandatory = [r for r in requirements.requirements if r.requirement_type == "mandatory"]
print(f"Found {len(mandatory)} mandatory requirements")

# Filter by applicability
cfo_requirements = [
    r for r in requirements.requirements
    if any("CFO" in role for role in r.applies_to)
]

# Filter by regulatory basis
sox_requirements = [
    r for r in requirements.requirements
    if any("SOX" in reg for reg in r.regulatory_basis)
]

# Group by section
from collections import defaultdict
by_section = defaultdict(list)
for req in requirements.requirements:
    section = req.source_section or "Unknown"
    by_section[section].append(req)
```

## Testing with Sample Datasets

### Generate Test Policies

```bash
# Generate 3 policies for quick testing (micro-dataset)
uv run python scripts/generate_micro_dataset.py

# Generate 13 policies across all domains (full dataset)
uv run python scripts/generate_full_dataset.py

# Generate specific number of policies
uv run python scripts/generate_full_dataset.py --count 5
```

### Test Extraction

```bash
# Test on generated policy
uv run python examples/extract_policy_requirements.py \
  sample_policies/full_dataset/FIN-001_expense_reimbursement.md \
  --metadata sample_policies/full_dataset/metadata.json
```

## Troubleshooting

### API Key Issues

```
Error: GOOGLE_API_KEY environment variable not set
```

**Solution:** Set your API key:
```bash
export GOOGLE_API_KEY='your-key-here'
```

Or create a `.env` file:
```bash
echo "GOOGLE_API_KEY=your-key-here" > .env
```

### PDF Conversion Errors

```
Error: PDF file not found
```

**Solution:** Ensure the PDF path is correct and the file exists:
```python
from pathlib import Path
pdf_path = Path("policy.pdf")
assert pdf_path.exists(), f"PDF not found: {pdf_path}"
```

### Empty or Incomplete Extraction

**Possible causes:**
- PDF is image-based (no text layer)
- Policy has unusual formatting
- Requirements use non-standard language

**Solutions:**
1. Use OCR to add text layer to image-based PDFs
2. Try `gemini-2.5-pro` for better accuracy:
   ```python
   extractor = PolicyRequirementsExtractor(model_name="gemini-2.5-pro")
   ```
3. Review extraction notes:
   ```python
   if requirements.extraction_notes:
       print("Extraction warnings:")
       for note in requirements.extraction_notes:
           print(f"  - {note}")
   ```

### Schema Validation Errors

```
ValidationError: X fields required
```

**Solution:** Ensure all required metadata fields are provided:
```python
policy_metadata = {
    "policy_id": "FIN-001",        # Required
    "policy_title": "...",          # Required
    "policy_type": "Financial",     # Required
    "policy_version": "1.0",        # Optional
    "effective_date": "2024-01-15", # Optional
}
```

## Best Practices

### 1. Use Specific Policy IDs

Use a consistent naming scheme:
- `FIN-001`, `FIN-002`, ... for Financial
- `IT-001`, `IT-002`, ... for IT Security
- `HR-001`, `HR-002`, ... for HR
- `LEG-001`, `LEG-002`, ... for Legal
- `COMP-001`, `COMP-002`, ... for Compliance

### 2. Capture Version Information

Always include version and effective date for change tracking:
```python
policy_metadata = {
    "policy_id": "FIN-001",
    "policy_title": "Expense Reimbursement Policy",
    "policy_type": "Financial",
    "policy_version": "2.1",
    "effective_date": "2024-03-01",
}
```

### 3. Review Extraction Results

Always review extracted requirements for accuracy:
```python
# Print first 5 requirements for review
for req in requirements.requirements[:5]:
    print(f"{req.requirement_type}: {req.statement}")
```

### 4. Save Raw and Structured Data

Preserve both for analysis:
```python
import json

# Save structured output
with open(f"{policy_id}_requirements.json", "w") as f:
    f.write(requirements.to_json())

# Save raw PDF path for reference
metadata = {
    "pdf_path": str(pdf_path),
    "extraction_timestamp": requirements.extraction_timestamp,
    "total_requirements": requirements.total_requirements,
}
with open(f"{policy_id}_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
```

### 5. Use Appropriate Policy Types

Choose the policy type that best matches your document:
- **Financial**: Money, budgets, approvals, audits
- **IT Security**: Security controls, access, incidents
- **HR**: Employee conduct, performance, benefits
- **Legal**: Contracts, compliance, disclosures
- **Compliance**: Regulatory requirements, certifications

## Next Steps

- **Phase 2**: Add storage and querying capabilities
- **Phase 3**: Implement validation and quality scoring
- **Phase 4**: Add requirement relationships and change detection

## References

- [Policy Project Plan](../explorations/policy/policy_project.md)
- [Policy Dataset Strategy](../explorations/policy/policy_dataset.md)
- [CLAUDE.md](../CLAUDE.md)
