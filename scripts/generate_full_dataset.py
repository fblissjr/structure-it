"""Generate comprehensive sample dataset for policy requirements extraction.

Creates 12-15 realistic policy documents across all domains:
- Financial: 3 policies (simple, medium, complex)
- IT Security: 3 policies (simple, medium, complex)
- HR: 3 policies (simple, medium, complex)
- Legal: 2 policies (medium, complex)
- Compliance: 2 policies (medium, complex)

Usage:
    uv run python scripts/generate_full_dataset.py [--count N]
"""

import argparse
import asyncio
import csv
import json
import os
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types


class FullDatasetGenerator:
    """Generate comprehensive policy dataset."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize the dataset generator.

        Args:
            api_key: Google API key (if not set via environment).
        """
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = genai.Client()

    async def generate_policy_text(
        self,
        policy_id: str,
        policy_title: str,
        policy_type: str,
        complexity: str = "medium",
        temperature: float = 0.8,
    ) -> str:
        """Generate policy document text using Gemini.

        Args:
            policy_id: Policy identifier.
            policy_title: Policy name.
            policy_type: Type (Financial, IT Security, HR, Legal, Compliance).
            complexity: simple/medium/complex.
            temperature: Sampling temperature for variety.

        Returns:
            Generated policy text in markdown format.
        """
        complexity_specs = {
            "simple": {
                "requirements": "5-10 clear, straightforward requirements",
                "pages": "2-3 pages",
                "language": "Simple, accessible language",
                "conditions": "Minimal conditions or exceptions",
            },
            "medium": {
                "requirements": "10-15 requirements with some conditions",
                "pages": "5-7 pages",
                "language": "Professional business language",
                "conditions": "Some conditional requirements and exceptions",
            },
            "complex": {
                "requirements": "20-30 requirements with nested conditions",
                "pages": "10-15 pages",
                "language": "Technical and legal language",
                "conditions": "Multiple conditions, exceptions, and cross-references",
            },
        }

        spec = complexity_specs.get(complexity, complexity_specs["medium"])

        prompt = f"""Generate a realistic {policy_type} policy document for a mid-sized technology company (500-1000 employees, $100M-500M revenue).

POLICY METADATA:
- Title: {policy_title}
- Policy ID: {policy_id}
- Version: 1.2
- Effective Date: 2024-01-15
- Policy Owner: {self._get_policy_owner(policy_type)}
- Approver: {self._get_approver(policy_type)}

COMPLEXITY: {complexity.upper()}
- Requirements: {spec["requirements"]}
- Length: {spec["pages"]}
- Language: {spec["language"]}
- Conditions: {spec["conditions"]}

REQUIRED SECTIONS:

1. DOCUMENT HEADER
   - Policy ID, Version, Effective Date, Review Date
   - Policy Owner, Approver, Classification
   - Document Status: Approved

2. PURPOSE (2-3 paragraphs)
   - Why this policy exists
   - What business problem it solves
   - Link to company values/strategy

3. SCOPE
   - Who this applies to (specific roles, departments)
   - What systems/processes are covered
   - Geographic scope if relevant
   - Any exclusions

4. DEFINITIONS (5-10 terms)
   - Define key terms used in policy
   - Use realistic business terminology

5. POLICY STATEMENTS ({spec["requirements"]})
   Create realistic, specific requirements using:

   MANDATORY (use "must", "shall", "will", "required to"):
   - Include specific thresholds, amounts, timeframes
   - Name specific roles/departments
   - Add conditions: "when X exceeds $Y", "if Z occurs"
   - Note exceptions: "except for emergency", "unless approved by"

   RECOMMENDED (use "should", "recommended", "encouraged"):
   - Best practices
   - Optional improvements

   PROHIBITED (use "must not", "shall not", "prohibited", "forbidden"):
   - Clear prohibitions
   - Consequences stated

   {self._get_domain_specific_guidance(policy_type)}

6. PROCEDURES (2-4 detailed procedures)
   - Step-by-step processes
   - Clear numbering (1.1, 1.2, etc.)
   - Reference requirements
   - Include approval workflows where relevant

7. ROLES AND RESPONSIBILITIES
   - Create a table or list showing:
     * Role/Title
     * Specific responsibilities under this policy
     * Approval authorities

8. COMPLIANCE AND ENFORCEMENT
   - How compliance is monitored
   - Audit procedures
   - Consequences of violations (warnings, termination, legal action)
   - Reporting violations

9. EXCEPTIONS
   - Process for requesting exceptions
   - Who can approve exceptions
   - Documentation requirements

10. RELATED DOCUMENTS
    - List 3-5 related policies (make up realistic policy names)
    - Reference relevant regulations if applicable

11. APPENDICES (if complex)
    - Forms, templates, examples
    - Approval matrices
    - Thresholds tables

12. VERSION HISTORY
    Create realistic version history table:
    | Version | Date | Changes | Approved By |
    |---------|------|---------|-------------|
    | 1.0 | 2022-06-01 | Initial release | [Name] |
    | 1.1 | 2023-03-15 | Updated approval thresholds | [Name] |
    | 1.2 | 2024-01-15 | Added remote work provisions | [Name] |

QUALITY REQUIREMENTS:
- Use realistic company examples (TechCorp, Acme Solutions, etc.)
- Include specific dollar amounts, percentages, timeframes
- Make requirements testable/measurable
- Use consistent formatting and numbering
- Professional business writing style
- Include regulatory references where appropriate (SOX, GDPR, PCI-DSS, HIPAA, etc.)

FORMAT: Output as well-structured markdown with:
- Clear heading hierarchy (# ## ### ####)
- Tables where appropriate
- Numbered lists for procedures
- Bullet points for requirements
- Bold for key terms
"""

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model="gemini-flash-lite-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
            ),
        )

        return response.text

    def _get_policy_owner(self, policy_type: str) -> str:
        """Get appropriate policy owner for policy type."""
        owners = {
            "Financial": "Chief Financial Officer (CFO)",
            "IT Security": "Chief Information Security Officer (CISO)",
            "HR": "Chief Human Resources Officer (CHRO)",
            "Legal": "General Counsel",
            "Compliance": "Chief Compliance Officer (CCO)",
        }
        return owners.get(policy_type, "Chief Operating Officer (COO)")

    def _get_approver(self, policy_type: str) -> str:
        """Get appropriate approver for policy type."""
        approvers = {
            "Financial": "Audit Committee",
            "IT Security": "Chief Executive Officer (CEO)",
            "HR": "Chief Executive Officer (CEO)",
            "Legal": "Board of Directors",
            "Compliance": "Board of Directors",
        }
        return approvers.get(policy_type, "Chief Executive Officer (CEO)")

    def _get_domain_specific_guidance(self, policy_type: str) -> str:
        """Get domain-specific requirement guidance."""
        guidance = {
            "Financial": """
   FINANCIAL SPECIFIC REQUIREMENTS:
   - Approval thresholds at multiple levels ($1K, $10K, $50K, $100K, $500K+)
   - Segregation of duties (who requests vs. who approves vs. who processes)
   - Budget controls and variance reporting
   - Financial reporting deadlines
   - Audit trail requirements
   - SOX 404 compliance where relevant
   - Vendor payment terms and approvals
   - Capital vs. operational expense classification
""",
            "IT Security": """
   IT SECURITY SPECIFIC REQUIREMENTS:
   - Access control levels (read, write, admin)
   - Authentication requirements (MFA, password complexity)
   - Data classification (public, internal, confidential, restricted)
   - Encryption requirements (at rest, in transit)
   - Logging and monitoring requirements
   - Incident response timeframes (detect, contain, remediate)
   - Patch management schedules
   - Third-party security assessments
   - GDPR, SOC2, ISO 27001 compliance
""",
            "HR": """
   HR SPECIFIC REQUIREMENTS:
   - Employee conduct expectations
   - Performance review cycles and criteria
   - Leave accrual and approval requirements
   - Training and certification requirements
   - Disciplinary procedures and escalation
   - Equal opportunity and anti-discrimination
   - Workplace safety obligations
   - Confidentiality and non-compete
""",
            "Legal": """
   LEGAL SPECIFIC REQUIREMENTS:
   - Regulatory compliance obligations
   - Disclosure and reporting requirements
   - Contract approval thresholds
   - Intellectual property protection
   - Litigation holds and document retention
   - Whistleblower protections
   - Regulatory citations (specific laws, regulations)
   - Risk assessment and mitigation
""",
            "Compliance": """
   COMPLIANCE SPECIFIC REQUIREMENTS:
   - Regulatory framework references (specific regulations)
   - Monitoring and reporting schedules
   - Audit and verification procedures
   - Certification and attestation requirements
   - Regulatory training requirements
   - Compliance committee oversight
   - Risk assessments and controls testing
   - Regulatory change management
""",
        }
        return guidance.get(policy_type, "")

    def save_as_markdown(self, content: str, output_path: Path) -> None:
        """Save policy content as markdown file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(content)


async def generate_full_dataset(count: int | None = None) -> None:
    """Generate comprehensive policy dataset.

    Args:
        count: Optional number of policies to generate (default: all 13).
    """
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Please set your Google API key:")
        print("  export GOOGLE_API_KEY='your-api-key-here'")
        return

    print()
    print("=" * 80)
    print("Generating Full Sample Dataset")
    print("=" * 80)
    print()

    # Define all policies to generate
    all_policies = [
        # Financial (3)
        {
            "policy_id": "FIN-001",
            "policy_title": "Expense Reimbursement Policy",
            "policy_type": "Financial",
            "complexity": "simple",
            "filename": "FIN-001_expense_reimbursement.md",
        },
        {
            "policy_id": "FIN-002",
            "policy_title": "Capital Expenditure Approval Policy",
            "policy_type": "Financial",
            "complexity": "medium",
            "filename": "FIN-002_capital_expenditure.md",
        },
        {
            "policy_id": "FIN-003",
            "policy_title": "Financial Authority Matrix and Approval Limits",
            "policy_type": "Financial",
            "complexity": "complex",
            "filename": "FIN-003_financial_authority_matrix.md",
        },
        # IT Security (3)
        {
            "policy_id": "IT-001",
            "policy_title": "Acceptable Use Policy",
            "policy_type": "IT Security",
            "complexity": "simple",
            "filename": "IT-001_acceptable_use.md",
        },
        {
            "policy_id": "IT-002",
            "policy_title": "Access Control and Identity Management Policy",
            "policy_type": "IT Security",
            "complexity": "medium",
            "filename": "IT-002_access_control.md",
        },
        {
            "policy_id": "IT-003",
            "policy_title": "Information Security and Data Protection Policy",
            "policy_type": "IT Security",
            "complexity": "complex",
            "filename": "IT-003_information_security.md",
        },
        # HR (3)
        {
            "policy_id": "HR-001",
            "policy_title": "Code of Conduct",
            "policy_type": "HR",
            "complexity": "simple",
            "filename": "HR-001_code_of_conduct.md",
        },
        {
            "policy_id": "HR-002",
            "policy_title": "Remote Work and Flexible Work Arrangements",
            "policy_type": "HR",
            "complexity": "medium",
            "filename": "HR-002_remote_work.md",
        },
        {
            "policy_id": "HR-003",
            "policy_title": "Performance Management and Employee Development",
            "policy_type": "HR",
            "complexity": "complex",
            "filename": "HR-003_performance_management.md",
        },
        # Legal (2)
        {
            "policy_id": "LEG-001",
            "policy_title": "Conflict of Interest and Disclosure Policy",
            "policy_type": "Legal",
            "complexity": "medium",
            "filename": "LEG-001_conflict_of_interest.md",
        },
        {
            "policy_id": "LEG-002",
            "policy_title": "Records Retention and Document Management Policy",
            "policy_type": "Legal",
            "complexity": "complex",
            "filename": "LEG-002_records_retention.md",
        },
        # Compliance (2)
        {
            "policy_id": "COMP-001",
            "policy_title": "Privacy and Data Protection Compliance",
            "policy_type": "Compliance",
            "complexity": "medium",
            "filename": "COMP-001_privacy_compliance.md",
        },
        {
            "policy_id": "COMP-002",
            "policy_title": "Anti-Corruption and Ethical Business Practices",
            "policy_type": "Compliance",
            "complexity": "complex",
            "filename": "COMP-002_anti_corruption.md",
        },
    ]

    # Limit if count specified
    if count:
        policies = all_policies[:count]
    else:
        policies = all_policies

    print(f"Generating {len(policies)} policies...")
    print()

    # Create output directory
    output_dir = Path("sample_policies/full_dataset")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize generator
    generator = FullDatasetGenerator()

    # Generate policies
    metadata_list = []
    for idx, policy in enumerate(policies, 1):
        print(f"[{idx}/{len(policies)}] {policy['policy_title']}")
        print(f"            ID: {policy['policy_id']}")
        print(f"            Type: {policy['policy_type']}")
        print(f"            Complexity: {policy['complexity']}")

        try:
            # Generate policy text (vary temperature for diversity)
            temp = 0.7 + (idx % 3) * 0.1  # 0.7, 0.8, 0.9
            content = await generator.generate_policy_text(
                policy_id=policy["policy_id"],
                policy_title=policy["policy_title"],
                policy_type=policy["policy_type"],
                complexity=policy["complexity"],
                temperature=temp,
            )

            # Save markdown
            md_path = output_dir / policy["filename"]
            generator.save_as_markdown(content, md_path)

            print(f"            ✓ Saved: {md_path.name}")
            print(f"            Length: {len(content):,} characters")
            print()

            # Build metadata
            metadata = {
                "policy_id": policy["policy_id"],
                "policy_title": policy["policy_title"],
                "policy_type": policy["policy_type"],
                "policy_version": "1.2",
                "effective_date": "2024-01-15",
                "filename": policy["filename"],
                "complexity": policy["complexity"],
                "character_count": len(content),
                "generated_at": datetime.utcnow().isoformat(),
                "model": "gemini-flash-lite-latest",
                "temperature": temp,
            }
            metadata_list.append(metadata)

        except Exception as e:
            print(f"            ✗ Error: {e}")
            import traceback

            traceback.print_exc()
            print()
            continue

    # Save metadata as JSON
    metadata_json_path = output_dir / "metadata.json"
    with open(metadata_json_path, "w") as f:
        json.dump(metadata_list, f, indent=2)

    # Save metadata as CSV
    metadata_csv_path = output_dir / "metadata.csv"
    if metadata_list:
        with open(metadata_csv_path, "w", newline="") as f:
            fieldnames = metadata_list[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(metadata_list)

    # Generate summary statistics
    print("=" * 80)
    print("Dataset Generation Complete")
    print("=" * 80)
    print()
    print(f"Location: {output_dir}")
    print(f"Total Policies: {len(metadata_list)}")
    print()

    # Breakdown by type
    by_type = {}
    by_complexity = {}
    for meta in metadata_list:
        ptype = meta["policy_type"]
        complexity = meta["complexity"]
        by_type[ptype] = by_type.get(ptype, 0) + 1
        by_complexity[complexity] = by_complexity.get(complexity, 0) + 1

    print("By Policy Type:")
    for ptype, count in sorted(by_type.items()):
        print(f"  {ptype}: {count}")
    print()

    print("By Complexity:")
    for complexity, count in sorted(by_complexity.items()):
        print(f"  {complexity}: {count}")
    print()

    print(f"Metadata saved:")
    print(f"  JSON: {metadata_json_path}")
    print(f"  CSV: {metadata_csv_path}")
    print()

    print("Next Steps:")
    print("1. Review the generated policies")
    print("2. Test extraction with:")
    print("   uv run python examples/extract_policy_requirements.py \\")
    print(f"     {output_dir}/FIN-001_expense_reimbursement.md \\")
    print(f"     --metadata {metadata_json_path}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate comprehensive policy dataset")
    parser.add_argument(
        "--count",
        type=int,
        help="Number of policies to generate (default: all 13)",
    )
    args = parser.parse_args()

    asyncio.run(generate_full_dataset(count=args.count))
