# Sample Dataset Strategy for Policy Requirements System

## Recommended Approach: Hybrid Dataset

### Phase 1: Public Policy Sources (10-15 documents)

These are real, publicly available policies that closely match your use case:

#### **1. University Policies (Excellent Match)**
Universities publish comprehensive P&P libraries covering all your domains:

**Sources:**
- **MIT Policies**: https://policies.mit.edu/
  - Download: Information Security, Financial, HR, Research policies
  - Why: Well-structured, covers technical + administrative domains

- **Stanford Administrative Guide**: https://adminguide.stanford.edu/
  - Procurement, IT security, records management
  - Why: Clear requirements, proper versioning

- **UC Berkeley Policies**: https://policy.ucop.edu/
  - Financial controls, data security, HR
  - Why: Includes regulatory references (good for compliance mapping)

**Action Items:**
```python
# Add to instructions for Claude Code:

"""
Task 1.5: Download Sample Public Policies

Create script: scripts/download_sample_policies.py

Download 10-15 policies from:
1. MIT Policies (https://policies.mit.edu/):
   - Information Security Policy
   - Procurement and Payment Policy
   - Conflict of Interest Policy
   - Records Retention Policy

2. Stanford (https://adminguide.stanford.edu/):
   - IT Security Policy
   - Financial Authority Matrix
   - Vendor Management Policy

3. UC Berkeley (https://policy.ucop.edu/):
   - Data Classification Policy
   - Travel and Entertainment Policy
   - Whistleblower Policy

Save to: sample_policies/public/
With metadata CSV: sample_policies/public/metadata.csv

Metadata should include:
- filename
- policy_id (assign: MIT-IS-001, STAN-IT-001, etc.)
- policy_type (Financial, IT Security, HR, Legal)
- source_url
- download_date
- notes
"""
```

#### **2. Open Source Project Governance (5-10 documents)**

**Sources:**
- **Apache Software Foundation**: https://www.apache.org/foundation/policies/
  - Brand policy, license policy, conduct policy
  - Why: Clear requirements, well-maintained

- **Python Software Foundation**: https://www.python.org/psf/policies/
  - Code of conduct, trademark policy
  - Why: Short, focused policies good for testing

- **Linux Foundation**: https://www.linuxfoundation.org/policies
  - Antitrust policy, IP policy
  - Why: Legal/compliance heavy

#### **3. Government Policies (5-10 documents)**

**Sources:**
- **NIST SP 800 Series**: https://csrc.nist.gov/publications/sp800
  - Not policies per se, but structured like them
  - Excellent for IT security requirements

- **GSA Federal Acquisition Regulation**: https://www.acquisition.gov/
  - Procurement policies with clear requirements

---

### Phase 2: Generate Synthetic Policies (20-30 documents)

Create realistic synthetic policies to fill domain gaps and add variety.

**Add to Claude Code instructions:**

```python
"""
Task 1.6: Generate Synthetic Policy Documents

Create: scripts/generate_synthetic_policies.py

Generate 20-30 realistic policy PDFs across domains using Gemini.

For each domain, create 3-5 policies with varying complexity:

FINANCIAL:
- Capital Expenditure Approval Policy (complex, multi-level approvals)
- Expense Reimbursement Policy (simple, clear requirements)
- Budget Management Policy (medium complexity)
- Vendor Payment Terms Policy
- Financial Reporting Policy

IT SECURITY:
- Access Control Policy (technical requirements)
- Incident Response Policy (procedures + requirements)
- Data Classification Policy (categorization + rules)
- Acceptable Use Policy (employee obligations)
- Cloud Services Policy

HR:
- Code of Conduct (behavior requirements)
- Performance Management Policy (process + expectations)
- Remote Work Policy (eligibility + requirements)
- Leave and Absence Policy
- Workplace Safety Policy

LEGAL/COMPLIANCE:
- Conflict of Interest Policy (disclosure requirements)
- Records Retention Policy (timeframes + rules)
- Privacy Policy (data handling requirements)
- Anti-Corruption Policy (prohibitions)
- Whistleblower Policy

For each policy, generate:
1. PDF document with:
   - Header with metadata (policy ID, version, effective date, owner)
   - Purpose section
   - Scope section
   - Definitions (5-10 terms)
   - Policy statements (5-15 requirements)
   - Procedures (2-5 procedures)
   - Related documents references
   - Version history table

2. Use realistic language patterns:
   - "Employees must..."
   - "The CFO shall approve..."
   - "It is prohibited to..."
   - "Managers should..."
   - "All requests require..."

3. Include variety:
   - Some requirements with conditions ("when amount exceeds $50k")
   - Some with exceptions ("except for emergency situations")
   - Some with regulatory references ("in compliance with SOX 404")
   - Some with role specifications ("the CISO must review")

4. Make them realistic length:
   - Simple policies: 2-3 pages
   - Medium policies: 5-8 pages
   - Complex policies: 10-15 pages

Save to: sample_policies/synthetic/
With metadata: sample_policies/synthetic/metadata.csv

Generation prompt template:
```
Generate a realistic {policy_type} policy document for a mid-sized technology company.

Title: {policy_title}
Policy ID: {policy_id}
Version: 1.2
Effective Date: 2024-01-15

The policy should include:
- Clear purpose and scope
- 5-10 defined terms
- 10-20 specific requirements using obligation language
- 2-3 procedures with step-by-step instructions
- References to regulations where appropriate
- Role responsibilities clearly stated
- Version history showing 2-3 revisions

Make it professionally written and realistic. Include specific thresholds,
timeframes, and approval levels. Vary the complexity of requirements.

Format as a professional policy document with proper sections and numbering.
```

Use different models/temperatures for variety:
- Some with gemini-2.0-flash-exp (faster, lighter)
- Some with gemini-2.5-pro (more detailed)
- Vary temperature (0.7-1.0) for stylistic variety
"""
```

---

### Phase 3: Create Test Scenarios (10 documents)

**Add to Claude Code instructions:**

```python
"""
Task 1.7: Create Test Scenario Policies

Create: sample_policies/test_cases/

Generate 10 policies designed to test specific extraction challenges:

1. high_complexity_financial.pdf
   - Multiple nested conditions
   - Complex approval matrices
   - Cross-references to other policies
   - Tests: conditional extraction, approval workflow mapping

2. ambiguous_requirements_hr.pdf
   - Vague language ("as appropriate", "when needed")
   - Tests: ambiguity detection, validation warnings

3. technical_jargon_it.pdf
   - Heavy technical terminology
   - Acronyms and specialized vocabulary
   - Tests: domain-specific extraction

4. multi_regulation_compliance.pdf
   - References SOX, GDPR, HIPAA, PCI-DSS
   - Tests: regulatory mapping, compliance matrix

5. short_simple_policy.pdf
   - 1 page, 5 clear requirements
   - Tests: basic extraction, baseline quality

6. long_complex_policy.pdf
   - 20+ pages, 50+ requirements
   - Multiple sections and subsections
   - Tests: chunking, context preservation

7. conflicting_requirements.pdf
   - Internal contradictions (intentional)
   - Tests: conflict detection, validation logic

8. no_clear_structure.pdf
   - Poor formatting, unclear sections
   - Tests: extraction robustness

9. version_comparison_v1.pdf and version_comparison_v2.pdf
   - Two versions of same policy with changes
   - Tests: change detection

10. cross_policy_references.pdf
    - Heavy references to other policies
    - Tests: relationship extraction

Each includes metadata documenting:
- What it tests
- Expected extraction challenges
- Known issues (for validation)
"""
```

---

### Phase 4: Create Metadata Files

**Add to Claude Code instructions:**

```python
"""
Task 1.8: Create Comprehensive Metadata

Create: sample_policies/metadata_master.csv

Columns:
- policy_id: Unique identifier (FIN-001, IT-005, HR-010)
- filename: PDF filename
- policy_title: Full policy name
- policy_type: Financial, IT Security, HR, Legal, Compliance
- version: Version number
- version_date: Effective date
- policy_owner: Department/role
- approver: Who approved
- source: public/synthetic/test_case
- source_url: If public policy
- regulatory_frameworks: Comma-separated (SOX, GDPR, etc.)
- complexity: simple/medium/complex
- page_count: Number of pages
- estimated_requirements: Approximate count
- notes: Special considerations

Also create domain-specific metadata files:
- sample_policies/financial_policies.csv
- sample_policies/it_policies.csv
- sample_policies/hr_policies.csv
- sample_policies/legal_policies.csv

This enables filtered batch processing by domain.
"""
```

---

## Complete Dataset Structure

```
sample_policies/
├── README.md                      # Overview of dataset
├── metadata_master.csv            # All policies
├── financial_policies.csv         # Filtered metadata
├── it_policies.csv
├── hr_policies.csv
├── legal_policies.csv
│
├── public/                        # Real public policies (10-15)
│   ├── mit_infosec_policy.pdf
│   ├── stanford_procurement.pdf
│   ├── ucb_data_classification.pdf
│   └── ...
│
├── synthetic/                     # Generated policies (20-30)
│   ├── FIN-001_capital_expenditure.pdf
│   ├── FIN-002_expense_reimbursement.pdf
│   ├── IT-001_access_control.pdf
│   ├── HR-001_code_of_conduct.pdf
│   └── ...
│
├── test_cases/                    # Edge cases (10)
│   ├── high_complexity_financial.pdf
│   ├── ambiguous_requirements_hr.pdf
│   ├── technical_jargon_it.pdf
│   └── ...
│
└── expected_results/              # For validation
    ├── FIN-001_expected.json      # Expected extraction results
    ├── IT-001_expected.json
    └── ...
```

---

## Usage in Development

**Add to Phase 1 instructions:**

```python
"""
After creating dataset, update examples/extract_policy_requirements.py to:

1. Include --sample flag that uses sample_policies/ dataset:
   uv run python examples/extract_policy_requirements.py --sample

2. Include --domain filter:
   uv run python examples/extract_policy_requirements.py --sample --domain Financial

3. Include --test-case mode that validates against expected_results/:
   uv run python examples/extract_policy_requirements.py --test-case FIN-001

This allows testing before using real data.
"""
```

---

## Quality Metrics for Sample Dataset

The dataset should enable testing:
- **Coverage**: All major policy domains represented
- **Complexity range**: Simple (2 pages) to complex (20+ pages)
- **Requirement variety**:
  - Mandatory vs recommended vs prohibited
  - Conditional requirements
  - Role-specific requirements
  - Regulatory-linked requirements
- **Edge cases**: Ambiguity, conflicts, poor structure
- **Relationships**: Cross-policy references, version changes

---

## Quick Start Script

**Add to instructions:**

```python
"""
Task 1.9: Create Dataset Setup Script

Create: scripts/setup_sample_dataset.py

This script should:
1. Create directory structure
2. Download public policies (with rate limiting)
3. Generate synthetic policies (in batches)
4. Create all metadata files
5. Generate expected results for test cases
6. Validate dataset completeness
7. Print summary statistics

Run with:
uv run python scripts/setup_sample_dataset.py

Should complete in 30-60 minutes and produce:
- 50-60 total policy PDFs
- Complete metadata
- Test cases with expected results
- README documenting the dataset

Output summary:
  Public policies: 12
  Synthetic policies: 28
  Test cases: 10
  Total: 50 policies

  By domain:
    Financial: 12
    IT Security: 15
    HR: 10
    Legal: 8
    Compliance: 5

  By complexity:
    Simple: 15
    Medium: 25
    Complex: 10
"""
```

---

## Advantages of This Approach

1. **Realistic**: Mix of real public policies and synthetic ones
2. **Comprehensive**: Covers all domains you'll encounter
3. **Testable**: Known edge cases with expected results
4. **Safe**: No proprietary data, can share with Claude Code
5. **Reproducible**: Script can regenerate synthetic policies
6. **Scalable**: Can generate more policies as needed

---

## Alternative: Faster Minimal Dataset

If you need something immediately (< 1 hour setup):

```python
"""
MINIMAL DATASET (10 policies)

Create: scripts/quick_dataset.py

Generate just 10 synthetic policies:
- 2 Financial (simple + complex)
- 2 IT Security (simple + complex)
- 2 HR (simple + complex)
- 2 Legal (simple + complex)
- 2 Test cases (edge cases)

Should complete in 10-15 minutes.
Good enough for Phase 1-2, expand for Phase 3-4.
"""
```

---

## Recommended Action

**Add this as Task 1.4 in the Claude Code instructions** (before Task 1.5 which was testing):

```
Task 1.4: Setup Sample Dataset

Run: uv run python scripts/setup_sample_dataset.py

This creates a realistic test dataset of 50+ policy documents before working with real data.

Once complete, update Task 1.5 (testing) to use this dataset instead of requiring manual sample policies.
```

This gives Claude Code everything it needs to create a realistic test environment before touching your actual policy documents.
