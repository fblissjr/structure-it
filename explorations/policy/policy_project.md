# Instructions for Claude Code: Policy Requirements Extraction System

## Project Goal
Build a system to extract structured requirements from policy and procedure documents (scope: <1000 documents). Start with a basic POC, then evolve to a production-ready system that extracts, validates, stores, and queries policy requirements.

## Context
- Working in the `structure-it` repository
- Tech stack: Python 3.11+, Google Gemini, Pydantic, DuckDB
- Use `uv` for all Python operations
- Follow existing code patterns in `src/structure_it/`
- Documents are PDFs with existing metadata (policy_id, type, version, etc.)

---

## Phase 1: Basic POC (Day 1-2)

### Objective
Extract requirements from 3-5 sample policies and demonstrate immediate value.

### Tasks

#### 1.1 Create Requirements Schema
**File**: `src/structure_it/schemas/policy_requirements.py`

Create schemas for:
- `PolicyRequirement` - A single requirement with:
  - `requirement_id` (auto-generated)
  - `statement` (the actual requirement text)
  - `requirement_type` ("mandatory", "recommended", "prohibited")
  - `source_policy_id`, `source_section`
  - `applies_to` (roles/departments as list)
  - `conditions` (when this applies)
  - `exceptions` (when this doesn't apply)
  - `regulatory_basis` (e.g., "SOX 404", "GDPR Article 32")

- `PolicyRequirements` - Collection wrapper with:
  - `policy_id`, `policy_title`, `policy_type`
  - `requirements` (list of PolicyRequirement)
  - Summary counts: `total_mandatory`, `total_recommended`, `total_prohibited`

**Success criteria**: Schema compiles, has proper type hints, inherits from BaseSchema

#### 1.2 Create Requirements Extractor
**File**: `src/structure_it/extractors/policy_extractor.py`

Create `PolicyRequirementsExtractor` class that:
- Accepts PDF path and policy metadata dict
- Uses `markitdown` to convert PDF to text
- Uses `GeminiExtractor` with `PolicyRequirements` schema
- Has a focused extraction prompt that:
  - Identifies requirement patterns ("must", "shall", "will", "required to", "prohibited")
  - Extracts who/what it applies to
  - Captures conditions and exceptions
  - Notes regulatory basis if mentioned
  - Includes section references

**Key prompt guidance**:
```
Extract ALL requirements from this {policy_type} policy.

A requirement is any statement that:
- Uses obligation language: "must", "shall", "will", "required to", "should", "prohibited"
- Specifies an action, restriction, or recommendation
- Has a clear subject (who/what it applies to)

For each requirement:
1. Extract the exact statement
2. Classify as mandatory, recommended, or prohibited
3. Identify who/what it applies to (roles, departments, systems)
4. Note any conditions ("when X happens") or exceptions ("except for Y")
5. If mentioned, note the regulatory basis (SOX, GDPR, etc.)

Be thorough - include all requirements, even minor ones.
```

**Success criteria**: Can extract requirements from one sample policy PDF

#### 1.3 Create Simple Demo Script
**File**: `examples/extract_policy_requirements.py`

Create a demo that:
- Takes a PDF path as command line argument
- Accepts optional metadata via JSON or dict
- Extracts requirements
- Prints results in readable format:
  - Total requirements found
  - Breakdown by type (mandatory/recommended/prohibited)
  - First 3-5 requirements as examples
  - Outputs full JSON to a file

**Success criteria**:
- Run: `uv run python examples/extract_policy_requirements.py sample_policy.pdf`
- Outputs readable summary and JSON file

#### 1.4 Test with Sample Policies
Create test with 3 sample policies from different domains:
- One Financial policy
- One IT Security policy
- One HR/Legal policy

**Success criteria**:
- Extracts requirements from all 3
- Requirements make sense to a human reviewer
- Captures different requirement patterns across domains

---

## Phase 2: Enhanced POC (Day 3-5)

### Objective
Add storage, querying, validation, and domain-specific improvements.

### Tasks

#### 2.1 Extend Storage for Requirements
**File**: `src/structure_it/storage/requirements_storage.py`

Create `RequirementsStorage(DuckDBStorage)` that:
- Extends your existing DuckDB storage
- Creates a dedicated `policy_requirements` table with columns:
  - requirement_id (PK)
  - policy_id, policy_type
  - statement (text)
  - requirement_type
  - source_section
  - applies_to (array)
  - conditions (array)
  - exceptions (array)
  - regulatory_basis (array)
  - created_at

- Creates indexes on:
  - policy_type
  - requirement_type
  - policy_id

- Implements methods:
  - `store_requirements(requirements: PolicyRequirements)` - bulk insert
  - `query_requirements(**filters)` - flexible filtering by:
    - policy_type
    - applies_to (array contains)
    - regulatory_basis (array contains)
    - requirement_type
  - `get_requirements_by_policy(policy_id)` - all requirements for a policy
  - `count_requirements(**filters)` - count with same filters

**Success criteria**: Can store extracted requirements and query them efficiently

#### 2.2 Add Domain-Specific Extraction Prompts
**File**: `src/structure_it/extractors/policy_extractor.py`

Enhance `PolicyRequirementsExtractor` with:
- Domain-specific prompt templates for:
  - **Financial**: Focus on approval thresholds, authorization levels, spending limits
  - **IT Security**: Focus on access controls, technical controls, incident procedures
  - **Legal/Compliance**: Focus on regulatory references, obligations, risk statements
  - **HR**: Focus on employee obligations, performance criteria, grievance procedures

- Method `_build_domain_prompt(policy_type: str) -> str` that customizes the prompt
- Method `_post_process_requirements(requirements, policy_type)` for domain-specific tagging

**Success criteria**: Extraction quality improves for domain-specific policies

#### 2.3 Add Validation Layer
**File**: `src/structure_it/validation/requirements_validator.py`

Create `RequirementsValidator` that checks:
- All requirements have non-empty statements
- requirement_type is one of: mandatory, recommended, prohibited
- applies_to is populated (warn if empty)
- Detect potential duplicates (similar statements)
- Flag requirements without clear subjects
- Flag ambiguous requirements (contains "as needed", "when appropriate", etc.)

Returns validation report with:
- `is_valid: bool`
- `warnings: list[str]`
- `errors: list[str]`
- `quality_score: float` (0-1)

**Success criteria**: Can validate extracted requirements and surface quality issues

#### 2.4 Create Batch Processing Script
**File**: `examples/batch_extract_requirements.py`

Create script that:
- Takes a directory of PDFs and a metadata CSV/JSON file
- Processes all policies in parallel (with rate limiting)
- Stores results in RequirementsStorage
- Generates a summary report:
  - Total policies processed
  - Total requirements extracted
  - Breakdown by policy type
  - Validation quality scores
  - Any errors encountered
- Outputs detailed log file

**Success criteria**: Can process 20+ policies in batch and store in database

#### 2.5 Create Query Interface
**File**: `examples/query_requirements.py`

Create interactive query script with commands:
- `by-role <role>` - All requirements applying to a role
- `by-regulation <regulation>` - All requirements for a regulation
- `by-policy-type <type>` - All requirements for a policy type
- `mandatory-only` - Only mandatory requirements
- `export <query> <format>` - Export query results to CSV/JSON

**Success criteria**: Can answer common compliance questions via CLI

---

## Phase 3: Production-Ready System (Day 6-10)

### Objective
Add monitoring, refinement loops, relationship extraction, and analytics.

### Tasks

#### 3.1 Add Extraction Confidence Scoring
**File**: `src/structure_it/extractors/policy_extractor.py`

Enhance extraction to:
- Track extraction confidence per requirement
- Use multiple passes for low-confidence extractions:
  - Pass 1: Quick extraction (gemini-2.0-flash-exp)
  - Pass 2: Re-extract low-confidence items (gemini-2.5-pro)
- Store confidence scores in database
- Flag requirements needing human review (confidence < 0.7)

**Success criteria**: Can identify and reflag uncertain extractions

#### 3.2 Add Requirement Relationships
**File**: `src/structure_it/schemas/policy_requirements.py` (extend)

Add `RequirementRelationship` schema:
- `source_requirement_id`
- `target_requirement_id`
- `relationship_type` ("conflicts_with", "depends_on", "implements", "related_to")
- `description` (why they're related)

Create extractor to identify relationships:
- Within a policy (requirement A depends on requirement B)
- Cross-policy (requirement in Policy X implements requirement in Policy Y)

Add to storage:
- New table `requirement_relationships`
- Query method `get_related_requirements(requirement_id, relationship_type=None)`

**Success criteria**: Can find requirement dependencies and conflicts

#### 3.3 Add Change Detection
**File**: `src/structure_it/utils/change_detection.py`

Create system to:
- Compare requirements between policy versions
- Detect:
  - New requirements
  - Removed requirements
  - Modified requirements (statement changed)
  - Changed classifications (mandatory → recommended)
- Generate change report for a policy version

Store version history:
- Table `requirement_versions` with:
  - requirement_id, version, statement, effective_date

**Success criteria**: Can show what changed between policy versions

#### 3.4 Add Analytics Dashboard Data
**File**: `examples/generate_analytics.py`

Create script that generates analytics:
- **Compliance Matrix**: Requirements by regulation (pivot table)
- **Role Responsibility Matrix**: Requirements by role
- **Policy Coverage**: Which policy types have most/fewest requirements
- **Requirement Complexity**: Average conditions/exceptions per type
- **Gap Analysis**: Regulations mentioned but no implementing requirements
- **Risk Heatmap**: Mandatory requirements without clear ownership

Output as:
- JSON data files for dashboarding
- CSV exports
- Markdown report

**Success criteria**: Generates actionable compliance insights

#### 3.5 Add Iterative Refinement Loop
**File**: `src/structure_it/refinement/requirements_refiner.py`

Create `RequirementsRefiner` that:
- Takes extracted requirements and original policy text
- Uses LLM to:
  - Check for missed requirements (validation pass)
  - Verify applies_to is accurate
  - Enhance regulatory_basis with more detail
  - Split compound requirements into atomic requirements
- Generates refined version with change log

**Success criteria**: Second-pass refinement improves extraction quality

#### 3.6 Create Full Pipeline Script
**File**: `examples/full_pipeline.py`

Create end-to-end pipeline:
```python
async def process_policy_document(
    pdf_path: str,
    metadata: dict,
    storage: RequirementsStorage
) -> ProcessingResult:
    """Full pipeline from PDF to stored, validated, refined requirements."""

    # 1. Extract requirements
    # 2. Validate
    # 3. If validation passes, refine
    # 4. Extract relationships
    # 5. Store everything
    # 6. Return processing report
```

Include:
- Progress reporting
- Error handling and retry logic
- Logging to file
- Metrics collection (time, cost, tokens used)

**Success criteria**: Can process entire policy library with one command

---

## Phase 4: Polish & Documentation (Day 11-12)

### Tasks

#### 4.1 Add Comprehensive Tests
**File**: `tests/test_policy_requirements.py`

Add tests for:
- Schema validation
- Extraction from sample policies
- Storage operations (CRUD)
- Query filtering
- Validation logic
- Relationship detection

**Success criteria**: >80% test coverage on core functionality

#### 4.2 Create User Documentation
**File**: `docs/policy_requirements_guide.md`

Document:
- Overview and use cases
- Getting started (installation, setup)
- Extracting requirements (basic usage)
- Querying requirements (examples)
- Batch processing
- Interpreting validation reports
- Common troubleshooting

**Success criteria**: Non-technical user can follow guide

#### 4.3 Create Operator Guide
**File**: `docs/operations_guide.md`

Document:
- System architecture
- Database schema
- Configuration options
- Monitoring and logs
- Performance tuning
- Backup and recovery
- Scaling considerations (for future growth beyond 1000 docs)

**Success criteria**: Technical operator can maintain system

#### 4.4 Add Example Policy Templates
**Directory**: `examples/sample_policies/`

Create:
- 3-5 synthetic policy PDFs covering different domains
- Corresponding metadata JSON
- Expected extraction results (for testing)
- README explaining each sample

**Success criteria**: New users can test system immediately

---

## Implementation Guidelines

### Code Quality Standards
- Follow existing patterns in `src/structure_it/`
- Use type hints everywhere
- Add docstrings to all public functions/classes
- Keep functions focused (single responsibility)
- Handle errors gracefully with informative messages
- Log important events (extraction start/end, errors, warnings)

### Performance Considerations
- Use async/await for IO operations
- Batch database operations where possible
- Consider rate limiting for Gemini API (under 1000 docs, not critical but good practice)
- Cache PDF→text conversion results to avoid re-processing

### Testing Strategy
- Unit tests for schemas and utilities
- Integration tests for extraction pipeline
- Sample policy fixtures for consistent testing
- Validation that queries return expected results

### Error Handling
- Graceful degradation (continue processing other policies if one fails)
- Detailed error logs with context
- User-friendly error messages
- Retry logic for transient failures

---

## Success Metrics

### Phase 1 Complete When:
- ✅ Can extract requirements from 3 sample policies
- ✅ Results are readable and make sense
- ✅ JSON output is well-structured

### Phase 2 Complete When:
- ✅ Can process 20+ policies in batch
- ✅ All requirements stored in queryable database
- ✅ Can answer "show me all CFO approval requirements" in <1 second
- ✅ Validation catches obvious quality issues

### Phase 3 Complete When:
- ✅ Can process entire 1000-doc library
- ✅ Relationships between requirements are identified
- ✅ Can detect changes between policy versions
- ✅ Analytics reveal compliance insights

### Phase 4 Complete When:
- ✅ Documentation allows new user to get started in <30 minutes
- ✅ Tests provide confidence in system reliability
- ✅ Sample policies demonstrate capabilities

---

## Prioritization Notes

**Must Have (Phase 1-2)**:
- Basic extraction working
- Storage and querying
- Batch processing

**Should Have (Phase 3)**:
- Confidence scoring
- Relationships
- Change detection

**Nice to Have (Phase 4)**:
- Advanced analytics
- Iterative refinement
- Comprehensive docs

**Scale linearly**: With <1000 docs, don't over-engineer. Focus on extraction quality over scale optimizations.

---

## Getting Started

1. Review existing codebase structure
2. Start with Phase 1, Task 1.1
3. Test each component as you build it
4. Use the sample policies to validate
5. Commit frequently with clear messages
6. Document decisions and trade-offs in code comments

**First command to run**:
```bash
# Create the schemas file
touch src/structure_it/schemas/policy_requirements.py
```

**When complete, I should be able to run**:
```bash
# Process entire policy library
uv run python examples/full_pipeline.py ./policies/ --output ./results/

# Query requirements
uv run python examples/query_requirements.py by-regulation "SOX 404"

# Generate analytics
uv run python examples/generate_analytics.py --format markdown
```

---

Begin with Phase 1, Task 1.1. Let me know when each phase is complete and ready for review.
