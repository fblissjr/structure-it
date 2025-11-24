"""Example of extracting structured data from a media transcript."""

import asyncio
import sys

from structure_it.extractors import MediaExtractor
from structure_it.config import GOOGLE_API_KEY


async def extract_media_transcript() -> None:
    """Extract and print structured data from a sample media transcript."""
    sample_transcript = """
(0:00) Host: Welcome back to "Tech Innovations Today"! I'm your host, Alex, and today we have a fascinating discussion on the future of AI in healthcare.

(0:15) Guest: Thanks for having me, Alex. I'm Dr. Evelyn Reed, a lead researcher at BioMind AI, and I'm thrilled to talk about our latest advancements.

(0:45) Host: Dr. Reed, your recent paper on "Predictive Diagnostics with Large Language Models" has been making waves. Can you tell us about the core idea?

(1:10) Guest: Certainly. We're leveraging LLMs to analyze vast amounts of patient data – medical records, imaging, even genomic data – to predict disease onset long before traditional methods. The key is in identifying subtle patterns.

(2:00) Host: That sounds revolutionary! What kind of diseases are you seeing the most promise with?

(2:15) Guest: Early detection of certain cancers, neurological disorders like Alzheimer's, and even personalized treatment plans for chronic conditions. It's truly about bringing precision medicine to the forefront.

(3:00) Host: Incredible. For our listeners who want to dive deeper, where can they find your work?

(3:15) Guest: Our research is published on PubMed, and you can also find summaries and updates on the BioMind AI website, biomind.ai. We also have a GitHub repository for our open-source tools at github.com/biomind-ai/predx.

(3:45) Host: Fantastic resources. We'll be sure to link those in our show notes. Dr. Reed, thank you for sharing your insights today.

(3:55) Guest: My pleasure.

(4:00) Host: And that wraps up another episode of "Tech Innovations Today." Don't forget to subscribe and leave us a review!
"""
    extractor = MediaExtractor(api_key=GOOGLE_API_KEY)

    try:
        media_data = await extractor.extract(content=sample_transcript)
        print(f"--- Extracted Media Transcript Data ---")
        print(media_data.to_json())
    except Exception as e:
        print(f"Error extracting media transcript data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(extract_media_transcript())
