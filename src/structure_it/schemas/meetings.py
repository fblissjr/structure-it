"""Schema for meeting transcript extraction."""

from datetime import datetime

from structure_it.schemas.base import BaseSchema


class Participant(BaseSchema):
    """Meeting participant.

    Attributes:
        name: Name of the participant.
        role: Participant's role in the meeting.
        email: Participant's email address.
    """

    name: str
    role: str | None = None
    email: str | None = None


class ActionItem(BaseSchema):
    """Action item from meeting.

    Attributes:
        description: Description of the action item.
        assignee: Person assigned to the item.
        due_date: Due date for the item.
        priority: Priority level.
        status: Current status (default: "pending").
    """

    description: str
    assignee: str | None = None
    due_date: str | None = None
    priority: str | None = None
    status: str = "pending"


class Decision(BaseSchema):
    """Decision made during meeting.

    Attributes:
        description: Description of the decision.
        rationale: Rationale behind the decision.
        decided_by: List of people who made the decision.
        alternatives_considered: List of alternatives considered.
    """

    description: str
    rationale: str | None = None
    decided_by: list[str] = []
    alternatives_considered: list[str] = []


class Topic(BaseSchema):
    """Discussion topic.

    Attributes:
        title: Title of the topic.
        summary: Summary of the discussion.
        discussion_points: List of key discussion points.
        decisions: List of decisions made related to this topic.
        action_items: List of action items resulting from this topic.
        duration_minutes: Duration of discussion in minutes.
    """

    title: str
    summary: str
    discussion_points: list[str] = []
    decisions: list[Decision] = []
    action_items: list[ActionItem] = []
    duration_minutes: int | None = None


class MeetingNote(BaseSchema):
    """Structured meeting transcript.

    Attributes:
        title: Meeting title.
        date: Meeting date.
        start_time: Start time.
        end_time: End time.
        duration_minutes: Duration in minutes.
        participants: List of participants.
        organizer: Meeting organizer.
        agenda: List of agenda items.
        topics: List of discussion topics.
        decisions: List of decisions made.
        action_items: List of action items assigned.
        summary: Overall meeting summary.
        key_takeaways: List of key takeaways.
        next_steps: List of next steps.
        follow_up_required: Boolean indicating if follow-up is needed.
        meeting_type: Type of meeting (e.g., standup, planning).
        location: Meeting location.
        recording_url: URL to meeting recording.
    """

    title: str
    date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    duration_minutes: int | None = None

    # Participants
    participants: list[Participant] = []
    organizer: str | None = None

    # Content
    agenda: list[str] = []
    topics: list[Topic] = []
    decisions: list[Decision] = []
    action_items: list[ActionItem] = []

    # Summary
    summary: str | None = None
    key_takeaways: list[str] = []
    next_steps: list[str] = []
    follow_up_required: bool = False

    # Metadata
    meeting_type: str | None = None  # e.g., "standup", "planning", "retrospective"
    location: str | None = None
    recording_url: str | None = None
