"""Example of extracting structured meeting notes."""

import asyncio
import sys

from structure_it.extractors import MeetingExtractor
from structure_it.config import GOOGLE_API_KEY


async def extract_meeting_notes() -> None:
    """Extract and print structured meeting notes from a sample transcript."""
    sample_transcript = """
Date: 2024-11-20
Time: 10:00 AM - 11:00 AM
Attendees: Alice (Project Lead), Bob (Developer), Carol (QA)

Alice: Good morning everyone. Today we're discussing the new feature for user authentication. Bob, can you give us an update on the progress?

Bob: Sure. I've completed the initial implementation of the login API. We're using OAuth2. I've also started on the frontend integration, but I'm blocked by Carol needing to define the test cases for the new endpoint.

Carol: Right, I'll prioritize that. I should have the test cases ready by end of day tomorrow, 2024-11-21. Once Bob implements the API tests, we can move forward.

Alice: Okay, so decision: Bob will finalize the frontend integration once Carol provides the test cases. Carol, please send those test cases to Bob by tomorrow. Action item for Bob: Integrate frontend and API tests by next Tuesday, 2024-11-26.

Bob: Got it.

Carol: I also wanted to mention a potential bug in the old password reset flow. It seems some users are reporting issues.

Alice: Let's create a separate ticket for that and assign it to the support team for initial investigation. Our focus for this meeting is the new authentication feature.

Summary: Progress on new authentication feature. Bob blocked by Carol for test cases.
Next steps: Carol to provide test cases by EOD 2024-11-21. Bob to complete integration by 2024-11-26.
"""
    extractor = MeetingExtractor(api_key=GOOGLE_API_KEY)

    try:
        notes = await extractor.extract(content=sample_transcript)
        print(f"--- Extracted Meeting Notes ---")
        print(notes.to_json())
    except Exception as e:
        print(f"Error extracting meeting notes: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(extract_meeting_notes())
