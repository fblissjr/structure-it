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

from structure_it.config import DEFAULT_MODEL
from structure_it.generators import PolicyGenerator


class FullDatasetGenerator(PolicyGenerator):
    """Generate comprehensive policy dataset (extends PolicyGenerator)."""


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
    output_dir = Path("data/sample_policies/full_dataset")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize generator (uses DEFAULT_MODEL from config)
    generator = FullDatasetGenerator(model_name=DEFAULT_MODEL)

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
            content = await generator.generate_policy(
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
                "model": DEFAULT_MODEL,
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
