"""Schema definitions for structured outputs."""

from structure_it.schemas.academic import AcademicPaper, Author, Citation, Section
from structure_it.schemas.articles import (
    ArticleAuthor,
    ArticleImage,
    ArticleLink,
    ArticleSection,
    CodeBlock,
    WebArticle,
)
from structure_it.schemas.base import BaseSchema
from structure_it.schemas.civic import (
    AgendaItem,
    CivicMeeting,
    RollCall,
    Vote,
)
from structure_it.schemas.code_docs import (
    ClassDoc,
    CodeDocumentation,
    Example,
    FunctionDoc,
    ModuleDoc,
    Parameter,
    ReturnValue,
)
from structure_it.schemas.meetings import (
    ActionItem,
    Decision,
    MeetingNote,
    Participant,
    Topic,
)
from structure_it.schemas.media import (
    MediaTranscript,
    Resource,
    Segment,
    Speaker,
    Timestamp,
)
from structure_it.schemas.policy_requirements import (
    PolicyRequirement,
    PolicyRequirements,
)

__all__ = [
    "BaseSchema",
    # Academic
    "AcademicPaper",
    "Author",
    "Citation",
    "Section",
    # Articles
    "WebArticle",
    "ArticleAuthor",
    "ArticleImage",
    "ArticleSection",
    "ArticleLink",
    "CodeBlock",
    # Civic
    "CivicMeeting",
    "AgendaItem",
    "Vote",
    "RollCall",
    # Code Documentation
    "CodeDocumentation",
    "ModuleDoc",
    "FunctionDoc",
    "ClassDoc",
    "Parameter",
    "ReturnValue",
    "Example",
    # Meetings
    "MeetingNote",
    "Participant",
    "Topic",
    "Decision",
    "ActionItem",
    # Media (YouTube/Podcasts)
    "MediaTranscript",
    "Speaker",
    "Segment",
    "Timestamp",
    "Resource",
    # Policy Requirements
    "PolicyRequirement",
    "PolicyRequirements",
]
