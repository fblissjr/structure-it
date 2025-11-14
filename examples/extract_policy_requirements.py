"""Example: Extract structured requirements from policy documents.

This example demonstrates:
1. Converting policy PDFs to markdown using markitdown
2. Extracting structured requirements with Gemini
3. Displaying results in readable format
4. Saving full JSON output

Usage:
    uv run python examples/extract_policy_requirements.py <pdf_path> [options]

Examples:
    # Basic extraction with manual metadata
    uv run python examples/extract_policy_requirements.py policy.pdf

    # With metadata file
    uv run python examples/extract_policy_requirements.py policy.pdf --metadata metadata.json

    # With inline metadata
    uv run python examples/extract_policy_requirements.py policy.pdf \
        --policy-id FIN-001 \
        --policy-title "Capital Expenditure Policy" \
        --policy-type Financial
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from structure_it.config import DEFAULT_MODEL
from structure_it.extractors import PolicyRequirementsExtractor


def load_metadata_from_file(metadata_path: str, pdf_path: Path) -> dict:
    """Load policy metadata from JSON file.

    Args:
        metadata_path: Path to metadata JSON file.
        pdf_path: Path to PDF file (used to match metadata if list).

    Returns:
        Policy metadata dictionary.
    """
    with open(metadata_path) as f:
        metadata = json.load(f)

    # If metadata is a list, find matching entry by filename
    if isinstance(metadata, list):
        pdf_filename = pdf_path.name
        for entry in metadata:
            if entry.get("filename") == pdf_filename:
                return entry
        # If no exact match, try without extension
        pdf_stem = pdf_path.stem
        for entry in metadata:
            entry_stem = Path(entry.get("filename", "")).stem
            if entry_stem == pdf_stem:
                return entry
        # No match found
        raise ValueError(
            f"No metadata found for {pdf_filename} in {metadata_path}. "
            f"Available files: {[e.get('filename') for e in metadata]}"
        )

    # If metadata is a single dict, return it
    return metadata


def prompt_for_metadata(pdf_path: Path) -> dict:
    """Interactively prompt for required policy metadata.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Policy metadata dictionary.
    """
    print("\n" + "=" * 80)
    print("Policy Metadata Required")
    print("=" * 80)
    print(f"PDF: {pdf_path.name}")
    print()

    # Prompt for required fields
    policy_id = input("Policy ID (e.g., FIN-001): ").strip()
    policy_title = input("Policy Title (e.g., Capital Expenditure Policy): ").strip()

    print("\nPolicy Types:")
    print("  1. Financial")
    print("  2. IT Security")
    print("  3. HR")
    print("  4. Legal")
    print("  5. Compliance")
    policy_type_choice = input("Select policy type (1-5): ").strip()

    policy_types = {
        "1": "Financial",
        "2": "IT Security",
        "3": "HR",
        "4": "Legal",
        "5": "Compliance",
    }
    policy_type = policy_types.get(policy_type_choice, "Financial")

    # Optional fields
    policy_version = input("Policy Version (optional, press Enter to skip): ").strip()
    effective_date = input("Effective Date (optional, YYYY-MM-DD, press Enter to skip): ").strip()

    metadata = {
        "policy_id": policy_id,
        "policy_title": policy_title,
        "policy_type": policy_type,
    }

    if policy_version:
        metadata["policy_version"] = policy_version
    if effective_date:
        metadata["effective_date"] = effective_date

    return metadata


async def main() -> None:
    """Run the policy requirements extraction example."""
    parser = argparse.ArgumentParser(
        description="Extract structured requirements from policy documents."
    )
    parser.add_argument("pdf_path", help="Path to policy PDF file")
    parser.add_argument(
        "--metadata",
        help="Path to metadata JSON file",
    )
    parser.add_argument("--policy-id", help="Policy ID (e.g., FIN-001)")
    parser.add_argument("--policy-title", help="Policy title (e.g., Capital Expenditure Policy)")
    parser.add_argument(
        "--policy-type",
        choices=["Financial", "IT Security", "HR", "Legal", "Compliance"],
        help="Policy type",
    )
    parser.add_argument("--policy-version", help="Policy version")
    parser.add_argument("--effective-date", help="Effective date (YYYY-MM-DD)")
    parser.add_argument(
        "--output",
        help="Output JSON file path (default: <policy_id>_requirements.json)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help=f"Gemini model to use (default from config: {DEFAULT_MODEL})",
    )

    args = parser.parse_args()

    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY environment variable not set")
        print("Please set your Google API key:")
        print("  export GOOGLE_API_KEY='your-api-key-here'")
        return

    # Validate PDF exists
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        return

    print()
    print("=" * 80)
    print("Policy Requirements Extraction")
    print("=" * 80)
    print()

    # Load or prompt for metadata
    if args.metadata:
        print(f"Loading metadata from: {args.metadata}")
        policy_metadata = load_metadata_from_file(args.metadata, pdf_path)
    elif args.policy_id and args.policy_title and args.policy_type:
        # Use command line args
        policy_metadata = {
            "policy_id": args.policy_id,
            "policy_title": args.policy_title,
            "policy_type": args.policy_type,
        }
        if args.policy_version:
            policy_metadata["policy_version"] = args.policy_version
        if args.effective_date:
            policy_metadata["effective_date"] = args.effective_date
    else:
        # Interactive prompt
        policy_metadata = prompt_for_metadata(pdf_path)

    print()
    print(f"Policy: {policy_metadata['policy_title']} ({policy_metadata['policy_id']})")
    print(f"Type: {policy_metadata['policy_type']}")
    print(f"Model: {args.model}")
    print()

    # Extract requirements
    print("Extracting requirements...")
    print(f"  Converting PDF to markdown...")

    extractor = PolicyRequirementsExtractor(model_name=args.model)

    try:
        requirements = await extractor.extract(
            pdf_path=pdf_path,
            policy_metadata=policy_metadata,
        )
        print("  ✓ Extraction complete")
        print()
    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback

        traceback.print_exc()
        return

    # Display results
    print("=" * 80)
    print("Extraction Results")
    print("=" * 80)
    print()
    print(f"Policy: {requirements.policy_title}")
    print(f"Type: {requirements.policy_type}")
    if requirements.policy_version:
        print(f"Version: {requirements.policy_version}")
    if requirements.effective_date:
        print(f"Effective Date: {requirements.effective_date}")
    print()

    print(f"Total Requirements: {requirements.total_requirements}")
    print(f"  Mandatory: {requirements.total_mandatory}")
    print(f"  Recommended: {requirements.total_recommended}")
    print(f"  Prohibited: {requirements.total_prohibited}")
    print()

    # Show first 5 requirements as examples
    if requirements.requirements:
        print("Sample Requirements (first 5):")
        print("-" * 80)
        for idx, req in enumerate(requirements.requirements[:5], 1):
            print(f"\n{idx}. [{req.requirement_type.upper()}] {req.statement}")
            if req.applies_to:
                print(f"   Applies to: {', '.join(req.applies_to)}")
            if req.conditions:
                print(f"   Conditions: {'; '.join(req.conditions)}")
            if req.regulatory_basis:
                print(f"   Regulatory: {', '.join(req.regulatory_basis)}")
        print()

    # Show breakdown by type
    if requirements.requirements:
        print("\nRequirements by Type:")
        print("-" * 80)

        mandatory = [r for r in requirements.requirements if r.requirement_type == "mandatory"]
        recommended = [r for r in requirements.requirements if r.requirement_type == "recommended"]
        prohibited = [r for r in requirements.requirements if r.requirement_type == "prohibited"]

        if mandatory:
            print(f"\nMandatory ({len(mandatory)}):")
            for req in mandatory[:3]:
                print(f"  - {req.statement[:100]}...")

        if recommended:
            print(f"\nRecommended ({len(recommended)}):")
            for req in recommended[:3]:
                print(f"  - {req.statement[:100]}...")

        if prohibited:
            print(f"\nProhibited ({len(prohibited)}):")
            for req in prohibited[:3]:
                print(f"  - {req.statement[:100]}...")
        print()

    # Save JSON output
    output_path = args.output or f"{policy_metadata['policy_id']}_requirements.json"
    with open(output_path, "w") as f:
        f.write(requirements.to_json())

    print("=" * 80)
    print(f"✓ Results saved to: {output_path}")
    print("=" * 80)
    print()

    # Show extraction metadata
    print("Extraction Metadata:")
    print(f"  Model: {requirements.model_used}")
    print(f"  Timestamp: {requirements.extraction_timestamp}")
    if requirements.extraction_notes:
        print(f"  Notes: {', '.join(requirements.extraction_notes)}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
