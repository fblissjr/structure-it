"""Generate metadata files for policy datasets without calling the API.

This script creates metadata.json files for micro and full datasets
without generating the actual policy content. Useful for:
- Planning dataset structure
- Testing extraction scripts
- Avoiding API costs
- Regenerating metadata for existing policy files

If policy files (.md) already exist, the script will include them in metadata.
Otherwise, it generates metadata based on the standard structure.

Usage:
    uv run python scripts/generate_metadata_only.py
    uv run python scripts/generate_metadata_only.py --micro  # micro dataset only
    uv run python scripts/generate_metadata_only.py --full   # full dataset only
    uv run python scripts/generate_metadata_only.py --scan   # scan existing files
"""

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path


def scan_existing_policies(output_dir: Path) -> list[dict]:
    """Scan directory for existing .md files and extract metadata.

    Args:
        output_dir: Directory to scan for policy files.

    Returns:
        List of metadata dicts for found policies, or empty list if none found.
    """
    if not output_dir.exists():
        return []

    policy_files = list(output_dir.glob("*.md"))
    if not policy_files:
        return []

    metadata_list = []
    for policy_file in sorted(policy_files):
        # Extract policy_id from filename (e.g., FIN-001 from FIN-001_expense_reimbursement.md)
        filename = policy_file.name
        match = re.match(r"^([A-Z]+-\d+)_", filename)
        if not match:
            print(f"  Warning: Skipping {filename} (invalid format)")
            continue

        policy_id = match.group(1)

        # Try to extract title from filename
        stem = policy_file.stem
        title_part = stem.split("_", 1)[1] if "_" in stem else stem
        title = " ".join(word.capitalize() for word in title_part.split("_"))

        # Determine policy type from prefix
        prefix = policy_id.split("-")[0]
        policy_type_map = {
            "FIN": "Financial",
            "IT": "IT Security",
            "HR": "HR",
            "LEG": "Legal",
            "COMP": "Compliance",
        }
        policy_type = policy_type_map.get(prefix, "Unknown")

        # Try to read first few lines for additional metadata
        try:
            with open(policy_file, "r") as f:
                content = f.read(1000)  # Read first 1000 chars

                # Look for version in content
                version_match = re.search(r"Version[:\s]+([0-9.]+)", content, re.IGNORECASE)
                version = version_match.group(1) if version_match else "1.0"

                # Look for effective date
                date_match = re.search(r"Effective Date[:\s]+([0-9-]+)", content, re.IGNORECASE)
                effective_date = date_match.group(1) if date_match else "2024-01-15"
        except Exception as e:
            print(f"  Warning: Could not read {filename}: {e}")
            version = "1.0"
            effective_date = "2024-01-15"

        # Estimate complexity based on file size
        file_size = policy_file.stat().st_size
        if file_size < 3000:
            complexity = "simple"
        elif file_size < 10000:
            complexity = "medium"
        else:
            complexity = "complex"

        metadata = {
            "policy_id": policy_id,
            "policy_title": title,
            "policy_type": policy_type,
            "policy_version": version,
            "effective_date": effective_date,
            "filename": filename,
            "complexity": complexity,
            "file_size": file_size,
            "scanned_at": datetime.utcnow().isoformat(),
        }
        metadata_list.append(metadata)

    return metadata_list


def generate_micro_metadata(scan_existing: bool = False):
    """Generate metadata for micro dataset (3 policies).

    Args:
        scan_existing: If True, scan for existing files and use actual data.
    """
    # Create output directory
    output_dir = Path("sample_policies/micro_dataset")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if we should scan existing files
    if scan_existing:
        scanned = scan_existing_policies(output_dir)
        if scanned:
            policies = scanned
            print(f"  Scanned {len(policies)} existing policy files")
        else:
            print("  No existing files found, using default structure")
            scan_existing = False  # Fall back to default

    # Default metadata structure
    if not scan_existing:
        policies = [
        {
            "policy_id": "FIN-001",
            "policy_title": "Expense Reimbursement Policy",
            "policy_type": "Financial",
            "policy_version": "1.0",
            "effective_date": "2024-01-15",
            "filename": "FIN-001_expense_reimbursement.md",
            "complexity": "simple",
        },
        {
            "policy_id": "IT-001",
            "policy_title": "Access Control Policy",
            "policy_type": "IT Security",
            "policy_version": "1.0",
            "effective_date": "2024-01-15",
            "filename": "IT-001_access_control.md",
            "complexity": "medium",
        },
        {
            "policy_id": "HR-001",
            "policy_title": "Code of Conduct",
            "policy_type": "HR",
            "policy_version": "1.0",
            "effective_date": "2024-01-15",
            "filename": "HR-001_code_of_conduct.md",
            "complexity": "simple",
        },
        ]

        # Add generated timestamp
        for policy in policies:
            policy["generated_at"] = datetime.utcnow().isoformat()

    # Save metadata as JSON
    metadata_json_path = output_dir / "metadata.json"
    with open(metadata_json_path, "w") as f:
        json.dump(policies, f, indent=2)

    # Save metadata as CSV
    metadata_csv_path = output_dir / "metadata.csv"
    with open(metadata_csv_path, "w", newline="") as f:
        fieldnames = policies[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(policies)

    print(f"✓ Micro dataset metadata created:")
    print(f"  JSON: {metadata_json_path}")
    print(f"  CSV: {metadata_csv_path}")
    print(f"  Policies: {len(policies)}")

    return policies


def generate_full_metadata(scan_existing: bool = False):
    """Generate metadata for full dataset (13 policies).

    Args:
        scan_existing: If True, scan for existing files and use actual data.
    """
    # Create output directory
    output_dir = Path("sample_policies/full_dataset")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check if we should scan existing files
    if scan_existing:
        scanned = scan_existing_policies(output_dir)
        if scanned:
            policies = scanned
            print(f"  Scanned {len(policies)} existing policy files")
        else:
            print("  No existing files found, using default structure")
            scan_existing = False  # Fall back to default

    # Default metadata structure
    if not scan_existing:
        policies = [
        # Financial (3)
        {
            "policy_id": "FIN-001",
            "policy_title": "Expense Reimbursement Policy",
            "policy_type": "Financial",
            "policy_version": "1.2",
            "effective_date": "2024-01-15",
            "filename": "FIN-001_expense_reimbursement.md",
            "complexity": "simple",
        },
        {
            "policy_id": "FIN-002",
            "policy_title": "Capital Expenditure Approval Policy",
            "policy_type": "Financial",
            "policy_version": "1.2",
            "effective_date": "2024-01-15",
            "filename": "FIN-002_capital_expenditure.md",
            "complexity": "medium",
        },
        {
            "policy_id": "FIN-003",
            "policy_title": "Financial Authority Matrix and Approval Limits",
            "policy_type": "Financial",
            "policy_version": "1.2",
            "effective_date": "2024-01-15",
            "filename": "FIN-003_financial_authority_matrix.md",
            "complexity": "complex",
        },
        # IT Security (3)
        {
            "policy_id": "IT-001",
            "policy_title": "Acceptable Use Policy",
            "policy_type": "IT Security",
            "policy_version": "1.2",
            "effective_date": "2024-01-15",
            "filename": "IT-001_acceptable_use.md",
            "complexity": "simple",
        },
        {
            "policy_id": "IT-002",
            "policy_title": "Access Control and Identity Management Policy",
            "policy_type": "IT Security",
            "policy_version": "1.2",
            "effective_date": "2024-01-15",
            "filename": "IT-002_access_control.md",
            "complexity": "medium",
        },
        {
            "policy_id": "IT-003",
            "policy_title": "Information Security and Data Protection Policy",
            "policy_type": "IT Security",
            "policy_version": "1.2",
            "effective_date": "2024-01-15",
            "filename": "IT-003_information_security.md",
            "complexity": "complex",
        },
        # HR (3)
        {
            "policy_id": "HR-001",
            "policy_title": "Code of Conduct",
            "policy_type": "HR",
            "policy_version": "1.2",
            "effective_date": "2024-01-15",
            "filename": "HR-001_code_of_conduct.md",
            "complexity": "simple",
        },
        {
            "policy_id": "HR-002",
            "policy_title": "Remote Work and Flexible Work Arrangements",
            "policy_type": "HR",
            "policy_version": "1.2",
            "effective_date": "2024-01-15",
            "filename": "HR-002_remote_work.md",
            "complexity": "medium",
        },
        {
            "policy_id": "HR-003",
            "policy_title": "Performance Management and Employee Development",
            "policy_type": "HR",
            "policy_version": "1.2",
            "effective_date": "2024-01-15",
            "filename": "HR-003_performance_management.md",
            "complexity": "complex",
        },
        # Legal (2)
        {
            "policy_id": "LEG-001",
            "policy_title": "Conflict of Interest and Disclosure Policy",
            "policy_type": "Legal",
            "policy_version": "1.2",
            "effective_date": "2024-01-15",
            "filename": "LEG-001_conflict_of_interest.md",
            "complexity": "medium",
        },
        {
            "policy_id": "LEG-002",
            "policy_title": "Records Retention and Document Management Policy",
            "policy_type": "Legal",
            "policy_version": "1.2",
            "effective_date": "2024-01-15",
            "filename": "LEG-002_records_retention.md",
            "complexity": "complex",
        },
        # Compliance (2)
        {
            "policy_id": "COMP-001",
            "policy_title": "Privacy and Data Protection Compliance",
            "policy_type": "Compliance",
            "policy_version": "1.2",
            "effective_date": "2024-01-15",
            "filename": "COMP-001_privacy_compliance.md",
            "complexity": "medium",
        },
        {
            "policy_id": "COMP-002",
            "policy_title": "Anti-Corruption and Ethical Business Practices",
            "policy_type": "Compliance",
            "policy_version": "1.2",
            "effective_date": "2024-01-15",
            "filename": "COMP-002_anti_corruption.md",
            "complexity": "complex",
        },
        ]

        # Add generated timestamp
        for policy in policies:
            policy["generated_at"] = datetime.utcnow().isoformat()

    # Save metadata as JSON
    metadata_json_path = output_dir / "metadata.json"
    with open(metadata_json_path, "w") as f:
        json.dump(policies, f, indent=2)

    # Save metadata as CSV
    metadata_csv_path = output_dir / "metadata.csv"
    with open(metadata_csv_path, "w", newline="") as f:
        fieldnames = policies[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(policies)

    # Generate summary by type and complexity
    by_type = {}
    by_complexity = {}
    for policy in policies:
        ptype = policy["policy_type"]
        complexity = policy["complexity"]
        by_type[ptype] = by_type.get(ptype, 0) + 1
        by_complexity[complexity] = by_complexity.get(complexity, 0) + 1

    print(f"✓ Full dataset metadata created:")
    print(f"  JSON: {metadata_json_path}")
    print(f"  CSV: {metadata_csv_path}")
    print(f"  Total Policies: {len(policies)}")
    print()
    print("  By Policy Type:")
    for ptype, count in sorted(by_type.items()):
        print(f"    {ptype}: {count}")
    print()
    print("  By Complexity:")
    for complexity, count in sorted(by_complexity.items()):
        print(f"    {complexity}: {count}")

    return policies


def main():
    """Generate metadata files for policy datasets."""
    parser = argparse.ArgumentParser(
        description="Generate metadata files for policy datasets without API calls"
    )
    parser.add_argument(
        "--micro",
        action="store_true",
        help="Generate only micro dataset metadata",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Generate only full dataset metadata",
    )
    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan existing .md files and generate metadata from them",
    )

    args = parser.parse_args()

    print()
    print("=" * 80)
    print("Policy Dataset Metadata Generator")
    print("=" * 80)
    print()

    # If no specific dataset requested, generate both
    if not args.micro and not args.full:
        args.micro = True
        args.full = True

    if args.micro:
        if args.scan:
            print("Scanning micro dataset for existing policies...")
        else:
            print("Generating micro dataset metadata...")
        generate_micro_metadata(scan_existing=args.scan)
        print()

    if args.full:
        if args.scan:
            print("Scanning full dataset for existing policies...")
        else:
            print("Generating full dataset metadata...")
        generate_full_metadata(scan_existing=args.scan)
        print()

    print("=" * 80)
    print("Metadata generation complete!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Review the metadata files in sample_policies/")
    print("2. Use with existing policies or generate content separately")
    print("3. Test extraction with:")
    print("   uv run python examples/extract_policy_requirements.py \\")
    print("     <policy-file>.md --metadata sample_policies/full_dataset/metadata.json")
    print()


if __name__ == "__main__":
    main()
