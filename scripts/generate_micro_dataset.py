"""Generate 3 synthetic policy documents for Phase 1 testing.

Creates a micro-dataset of realistic policy PDFs for validating extraction:
- Financial: Expense Reimbursement Policy (simple)
- IT Security: Access Control Policy (medium)
- HR: Code of Conduct (simple)

Usage:
    uv run python scripts/generate_micro_dataset.py
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from google import genai
from google.genai import types


class PolicyGenerator:
    """Generate realistic synthetic policy documents."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize the policy generator.

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
        complexity: str = "simple",
    ) -> str:
        """Generate policy document text using Gemini.

        Args:
            policy_id: Policy identifier.
            policy_title: Policy name.
            policy_type: Type (Financial, IT Security, HR).
            complexity: simple/medium/complex.

        Returns:
            Generated policy text in markdown format.
        """
        complexity_guidance = {
            "simple": "5-10 clear requirements, 2-3 pages, straightforward language",
            "medium": "10-15 requirements with some conditions, 5-7 pages, professional language",
            "complex": "20+ requirements with nested conditions, 10-15 pages, technical language",
        }

        prompt = f"""Generate a realistic {policy_type} policy document for a mid-sized technology company.

Title: {policy_title}
Policy ID: {policy_id}
Version: 1.0
Effective Date: 2024-01-15
Policy Owner: {self._get_policy_owner(policy_type)}

Complexity: {complexity} - {complexity_guidance.get(complexity, complexity_guidance["simple"])}

The policy should include:

1. HEADER SECTION
   - Policy ID, Version, Effective Date
   - Policy Owner and Approver
   - Review Date

2. PURPOSE
   - Clear 2-3 sentence statement of why this policy exists

3. SCOPE
   - Who and what this policy applies to

4. DEFINITIONS (5-8 key terms)
   - Define technical terms used in the policy

5. POLICY STATEMENTS ({complexity_guidance.get(complexity, "5-10")} requirements)
   Use clear obligation language:
   - "must", "shall", "will" for mandatory requirements
   - "should", "recommended" for recommended practices
   - "prohibited", "must not" for prohibitions

   For each requirement:
   - State clearly who it applies to (roles, departments)
   - Include specific thresholds or limits where relevant
   - Add conditions when applicable ("when amount exceeds $X")
   - Note exceptions if appropriate ("except for emergency situations")
   - Reference regulations where relevant (SOX, GDPR, etc.)

6. PROCEDURES (2-3 procedures)
   - Step-by-step processes for common scenarios
   - Clear numbering and structure

7. ROLES AND RESPONSIBILITIES
   - Who does what under this policy

8. COMPLIANCE AND ENFORCEMENT
   - How compliance is verified
   - Consequences of non-compliance

9. RELATED DOCUMENTS
   - List 2-3 related policies

10. VERSION HISTORY
    - Table showing version changes

Make it professionally written and realistic. Use specific examples and thresholds.
Focus on creating well-structured, clear requirements that an LLM can extract.

Format as markdown with proper headings and structure. Use tables where appropriate.
"""

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model="gemini-flash-lite-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=1.2,
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

    def save_as_markdown(self, content: str, output_path: Path) -> None:
        """Save policy content as markdown file.

        Args:
            content: Policy text content.
            output_path: Output file path.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(content)


async def generate_micro_dataset() -> None:
    """Generate 3 synthetic policies for Phase 1 testing."""
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Please set your Google API key:")
        print("  export GOOGLE_API_KEY='your-api-key-here'")
        return

    print()
    print("=" * 80)
    print("Generating Micro-Dataset (3 Synthetic Policies)")
    print("=" * 80)
    print()

    # Define the 3 policies to generate
    policies = [
        {
            "policy_id": "FIN-001",
            "policy_title": "Expense Reimbursement Policy",
            "policy_type": "Financial",
            "complexity": "simple",
            "filename": "FIN-001_expense_reimbursement.md",
        },
        {
            "policy_id": "IT-001",
            "policy_title": "Access Control Policy",
            "policy_type": "IT Security",
            "complexity": "medium",
            "filename": "IT-001_access_control.md",
        },
        {
            "policy_id": "HR-001",
            "policy_title": "Code of Conduct",
            "policy_type": "HR",
            "complexity": "simple",
            "filename": "HR-001_code_of_conduct.md",
        },
    ]

    # Create output directory
    output_dir = Path("sample_policies/micro_dataset")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize generator
    generator = PolicyGenerator()

    # Generate each policy
    metadata_list = []
    for idx, policy in enumerate(policies, 1):
        print(f"[{idx}/3] Generating: {policy['policy_title']}")
        print(f"        Type: {policy['policy_type']}")
        print(f"        Complexity: {policy['complexity']}")

        try:
            # Generate policy text
            content = await generator.generate_policy_text(
                policy_id=policy["policy_id"],
                policy_title=policy["policy_title"],
                policy_type=policy["policy_type"],
                complexity=policy["complexity"],
            )

            # Save markdown
            md_path = output_dir / policy["filename"]
            generator.save_as_markdown(content, md_path)

            print(f"        ✓ Saved: {md_path}")
            print(f"        Length: {len(content)} characters")
            print()

            # Build metadata entry
            metadata = {
                "policy_id": policy["policy_id"],
                "policy_title": policy["policy_title"],
                "policy_type": policy["policy_type"],
                "policy_version": "1.0",
                "effective_date": "2024-01-15",
                "filename": policy["filename"],
                "complexity": policy["complexity"],
                "generated_at": datetime.utcnow().isoformat(),
            }
            metadata_list.append(metadata)

        except Exception as e:
            print(f"        ✗ Error: {e}")
            import traceback

            traceback.print_exc()
            print()

    # Save metadata file
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata_list, f, indent=2)

    print("=" * 80)
    print("Micro-Dataset Generation Complete")
    print("=" * 80)
    print()
    print(f"Location: {output_dir}")
    print(f"Policies: {len(metadata_list)}")
    print(f"Metadata: {metadata_path}")
    print()
    print("Next Steps:")
    print("1. Review the generated policies")
    print("2. Test extraction with:")
    print("   uv run python examples/extract_policy_requirements.py \\")
    print(f"     {output_dir}/FIN-001_expense_reimbursement.md \\")
    print("     --metadata sample_policies/micro_dataset/metadata.json")
    print()


if __name__ == "__main__":
    asyncio.run(generate_micro_dataset())
