"""Schema for academic paper extraction."""

from structure_it.schemas.base import BaseSchema


class Author(BaseSchema):
    """Author information."""

    name: str
    affiliation: str | None = None
    email: str | None = None


class Citation(BaseSchema):
    """Citation/reference information."""

    title: str
    authors: list[str]
    year: int | None = None
    venue: str | None = None
    doi: str | None = None


class Section(BaseSchema):
    """Paper section."""

    heading: str
    content: str
    subsections: list["Section"] = []


class AcademicPaper(BaseSchema):
    """Structured academic paper data."""

    title: str
    authors: list[Author]
    abstract: str
    keywords: list[str] = []
    publication_year: int | None = None
    venue: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None

    # Main content
    introduction: str | None = None
    methodology: str | None = None
    results: str | None = None
    discussion: str | None = None
    conclusion: str | None = None

    # Structured sections (alternative to predefined fields)
    sections: list[Section] = []

    # References
    citations: list[Citation] = []

    # Research metadata
    research_field: str | None = None
    research_topics: list[str] = []
    key_findings: list[str] = []
    limitations: list[str] = []
    future_work: list[str] = []
