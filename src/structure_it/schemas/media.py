"""Schema for YouTube/podcast transcript extraction."""

from structure_it.schemas.base import BaseSchema


class Timestamp(BaseSchema):
    """Timestamp marker in media."""

    time: str  # Format: "HH:MM:SS" or "MM:SS"
    label: str | None = None


class Speaker(BaseSchema):
    """Speaker in media content."""

    name: str
    role: str | None = None
    bio: str | None = None


class Segment(BaseSchema):
    """Segment/chapter of media content."""

    title: str
    start_time: str | None = None
    end_time: str | None = None
    summary: str | None = None
    key_points: list[str] = []
    transcript: str | None = None


class Resource(BaseSchema):
    """Resource mentioned in media."""

    title: str
    url: str | None = None
    description: str | None = None
    type: str | None = None  # e.g., "book", "website", "tool"


class MediaTranscript(BaseSchema):
    """Structured media transcript (YouTube, podcast, etc.)."""

    title: str
    description: str | None = None
    url: str | None = None

    # Content creators
    channel: str | None = None
    host: str | None = None
    guests: list[Speaker] = []

    # Metadata
    duration: str | None = None
    publish_date: str | None = None
    episode_number: int | None = None
    season_number: int | None = None
    category: str | None = None
    tags: list[str] = []

    # Content structure
    summary: str | None = None
    key_takeaways: list[str] = []
    segments: list[Segment] = []
    timestamps: list[Timestamp] = []

    # Full transcript
    full_transcript: str | None = None

    # Resources
    resources_mentioned: list[Resource] = []
    links_in_description: list[str] = []

    # Engagement
    topics_discussed: list[str] = []
    questions_answered: list[str] = []
    quotes: list[str] = []
