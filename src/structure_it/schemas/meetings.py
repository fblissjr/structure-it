"""Schema for meeting transcript extraction."""

from datetime import datetime

from structure_it.schemas.base import BaseSchema


class Participant(BaseSchema):
    """Meeting participant."""

    name: str
    role: str | None = None
    email: str | None = None


class ActionItem(BaseSchema):
    """Action item from meeting."""

    description: str
    assignee: str | None = None
    due_date: str | None = None
    priority: str | None = None
    status: str = "pending"


class Decision(BaseSchema):
    """Decision made during meeting."""

    description: str
    rationale: str | None = None
    decided_by: list[str] = []
    alternatives_considered: list[str] = []


class Topic(BaseSchema):
    """Discussion topic."""

    title: str
    summary: str
    discussion_points: list[str] = []
    decisions: list[Decision] = []
    action_items: list[ActionItem] = []
    duration_minutes: int | None = None


class MeetingNote(BaseSchema):
    """Structured meeting transcript."""

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
