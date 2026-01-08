"""Generate 3 synthetic policy documents for Phase 1 testing.

Creates a micro-dataset of realistic policy documents for validating extraction:
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

from structure_it.config import DEFAULT_MODEL
from structure_it.generators import PolicyGenerator


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
    output_dir = Path("data/sample_policies/micro_dataset")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize generator (uses DEFAULT_MODEL from config)
    generator = PolicyGenerator(model_name=DEFAULT_MODEL, temperature=1.2)

    # Generate each policy
    metadata_list = []
    for idx, policy in enumerate(policies, 1):
        print(f"[{idx}/3] Generating: {policy['policy_title']}")
        print(f"        Type: {policy['policy_type']}")
        print(f"        Complexity: {policy['complexity']}")

        try:
            # Generate policy text
            content = await generator.generate_policy(
                policy_id=policy["policy_id"],
                policy_title=policy["policy_title"],
                policy_type=policy["policy_type"],
                complexity=policy["complexity"],
                version="1.0",
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
    print("     --metadata data/sample_policies/micro_dataset/metadata.json")
    print()


if __name__ == "__main__":
    asyncio.run(generate_micro_dataset())
