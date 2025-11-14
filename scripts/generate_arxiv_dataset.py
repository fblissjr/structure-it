"""Generate synthetic ArXiv AI/ML research papers dataset.

Creates a dataset of realistic ArXiv papers across different AI focus areas:
- Machine Learning: 2 papers (simple, medium)
- Computer Vision: 2 papers (simple, medium)
- Natural Language Processing: 2 papers (medium, complex)
- Robotics: 1 paper (medium)
- Neural Networks: 1 paper (complex)

Usage:
    uv run python scripts/generate_arxiv_dataset.py [--count N]
"""

import argparse
import asyncio
import csv
import json
import os
from datetime import datetime
from pathlib import Path

from structure_it.generators import ArxivGenerator


async def generate_arxiv_dataset(count: int | None = None) -> None:
    """Generate ArXiv papers dataset.

    Args:
        count: Optional number of papers to generate (default: all 8).
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
    print("Generating ArXiv AI/ML Papers Dataset")
    print("=" * 80)
    print()

    # Define all papers to generate
    all_papers = [
        # Machine Learning (2)
        {
            "paper_id": "2401.12345",
            "title": "Efficient Training of Large Language Models with Adaptive Learning Rates",
            "focus_area": "machine_learning",
            "complexity": "simple",
            "filename": "2401.12345_efficient_llm_training.md",
        },
        {
            "paper_id": "2401.23456",
            "title": "Meta-Learning for Few-Shot Classification in Dynamic Environments",
            "focus_area": "machine_learning",
            "complexity": "medium",
            "filename": "2401.23456_meta_learning_few_shot.md",
        },
        # Computer Vision (2)
        {
            "paper_id": "2401.34567",
            "title": "Real-Time Object Detection for Autonomous Vehicles Using Lightweight CNNs",
            "focus_area": "computer_vision",
            "complexity": "simple",
            "filename": "2401.34567_realtime_object_detection.md",
        },
        {
            "paper_id": "2401.45678",
            "title": "Vision Transformers for Medical Image Segmentation: A Comprehensive Study",
            "focus_area": "computer_vision",
            "complexity": "medium",
            "filename": "2401.45678_vit_medical_segmentation.md",
        },
        # Natural Language Processing (2)
        {
            "paper_id": "2401.56789",
            "title": "Multilingual Neural Machine Translation with Cross-Lingual Attention",
            "focus_area": "natural_language",
            "complexity": "medium",
            "filename": "2401.56789_multilingual_nmt.md",
        },
        {
            "paper_id": "2401.67890",
            "title": "Large Language Models for Code Generation: Capabilities and Limitations",
            "focus_area": "natural_language",
            "complexity": "complex",
            "filename": "2401.67890_llm_code_generation.md",
        },
        # Robotics (1)
        {
            "paper_id": "2401.78901",
            "title": "Learning Dexterous Manipulation from Human Demonstrations",
            "focus_area": "robotics",
            "complexity": "medium",
            "filename": "2401.78901_dexterous_manipulation.md",
        },
        # Neural Networks (1)
        {
            "paper_id": "2401.89012",
            "title": "Understanding Neural Network Representations Through Mechanistic Interpretability",
            "focus_area": "neural_networks",
            "complexity": "complex",
            "filename": "2401.89012_mechanistic_interpretability.md",
        },
    ]

    # Limit if count specified
    if count:
        papers = all_papers[:count]
    else:
        papers = all_papers

    print(f"Generating {len(papers)} ArXiv papers...")
    print()

    # Create output directory
    output_dir = Path("data/sample_arxiv")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize generator
    generator = ArxivGenerator()

    # Generate papers
    metadata_list = []
    for idx, paper in enumerate(papers, 1):
        print(f"[{idx}/{len(papers)}] {paper['title'][:60]}...")
        print(f"            ID: {paper['paper_id']}")
        print(f"            Focus: {paper['focus_area'].replace('_', ' ').title()}")
        print(f"            Complexity: {paper['complexity']}")

        try:
            # Generate paper (vary temperature for diversity)
            temp = 0.7 + (idx % 3) * 0.1  # 0.7, 0.8, 0.9
            content = await generator.generate_paper(
                paper_id=paper["paper_id"],
                title=paper["title"],
                focus_area=paper["focus_area"],
                complexity=paper["complexity"],
                temperature=temp,
            )

            # Save markdown
            md_path = output_dir / paper["filename"]
            generator.save_as_markdown(content, md_path)

            print(f"            ✓ Saved: {md_path.name}")
            print(f"            Length: {len(content):,} characters")
            print()

            # Build metadata
            metadata = {
                "paper_id": paper["paper_id"],
                "title": paper["title"],
                "focus_area": paper["focus_area"],
                "complexity": paper["complexity"],
                "filename": paper["filename"],
                "character_count": len(content),
                "generated_at": datetime.utcnow().isoformat(),
                "model": generator.model_name,
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
    print("ArXiv Dataset Generation Complete")
    print("=" * 80)
    print()
    print(f"Location: {output_dir}")
    print(f"Total Papers: {len(metadata_list)}")
    print()

    # Breakdown by focus area
    by_focus = {}
    by_complexity = {}
    for meta in metadata_list:
        focus = meta["focus_area"]
        complexity = meta["complexity"]
        by_focus[focus] = by_focus.get(focus, 0) + 1
        by_complexity[complexity] = by_complexity.get(complexity, 0) + 1

    print("By Focus Area:")
    for focus, count in sorted(by_focus.items()):
        print(f"  {focus.replace('_', ' ').title()}: {count}")
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
    print("1. Review the generated papers")
    print("2. Test extraction with:")
    print("   uv run python examples/extract_academic_paper.py \\")
    print(f"     {output_dir}/2401.12345_efficient_llm_training.md")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate ArXiv AI/ML papers dataset"
    )
    parser.add_argument(
        "--count",
        type=int,
        help="Number of papers to generate (default: all 8)",
    )
    args = parser.parse_args()

    asyncio.run(generate_arxiv_dataset(count=args.count))
