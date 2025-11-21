"""Schema for YouTube/podcast transcript extraction."""

from structure_it.schemas.base import BaseSchema


class Timestamp(BaseSchema):
    """Timestamp marker in media.

    Attributes:
        time: Time string (e.g., "HH:MM:SS" or "MM:SS").
        label: Description or label for the timestamp.
    """

    time: str  # Format: "HH:MM:SS" or "MM:SS"
    label: str | None = None


class Speaker(BaseSchema):
    """Speaker in media content.

    Attributes:
        name: Name of the speaker.
        role: Role of the speaker (e.g., host, guest).
        bio: Biography or background of the speaker.
    """

    name: str
    role: str | None = None
    bio: str | None = None


class Segment(BaseSchema):
    """Segment/chapter of media content.

    Attributes:
        title: Title of the segment.
        start_time: Start time of the segment.
        end_time: End time of the segment.
        summary: Summary of the segment content.
        key_points: List of key points covered in the segment.
        transcript: Verbatim transcript of the segment.
    """

    title: str
    start_time: str | None = None
    end_time: str | None = None
    summary: str | None = None
    key_points: list[str] = []
    transcript: str | None = None


class Resource(BaseSchema):
    """Resource mentioned in media.

    Attributes:
        title: Title of the resource.
        url: URL to the resource.
        description: Description of the resource.
        type: Type of resource (e.g., "book", "website", "tool").
    """

    title: str
    url: str | None = None
    description: str | None = None
    type: str | None = None  # e.g., "book", "website", "tool"


class MediaTranscript(BaseSchema):
    """Structured media transcript (YouTube, podcast, etc.).

    Attributes:
        title: Title of the media.
        description: Description of the media.
        url: URL to the media source.
        channel: Channel or show name.
        host: Name of the host.
        guests: List of guests.
        duration: Duration string.
        publish_date: Publication date string.
        episode_number: Episode number.
        season_number: Season number.
        category: Content category.
        tags: List of tags.
        summary: Overall summary.
        key_takeaways: List of key takeaways.
        segments: List of content segments.
        timestamps: List of important timestamps.
        full_transcript: Complete transcript text.
        resources_mentioned: List of resources mentioned.
        links_in_description: List of links found in description.
        topics_discussed: List of topics discussed.
        questions_answered: List of questions answered.
        quotes: List of notable quotes.
    """

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
