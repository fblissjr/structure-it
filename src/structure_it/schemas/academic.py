"""Schema for academic paper extraction."""

from structure_it.schemas.base import BaseSchema


class Author(BaseSchema):
    """Author information.

    Attributes:
        name: Name of the author.
        affiliation: Author's institutional affiliation.
        email: Author's email address.
    """

    name: str
    affiliation: str | None = None
    email: str | None = None


class Citation(BaseSchema):
    """Citation/reference information.

    Attributes:
        title: Title of the cited work.
        authors: List of authors of the cited work.
        year: Publication year.
        venue: Publication venue (journal, conference, etc.).
        doi: Digital Object Identifier.
    """

    title: str
    authors: list[str]
    year: int | None = None
    venue: str | None = None
    doi: str | None = None


class Section(BaseSchema):
    """Paper section.

    Attributes:
        heading: Section heading/title.
        content: Text content of the section.
        subsections: List of subsections within this section.
    """

    heading: str
    content: str
    subsections: list["Section"] = []


class AcademicPaper(BaseSchema):
    """Structured academic paper data.

    Attributes:
        title: Title of the paper.
        authors: List of authors.
        abstract: Paper abstract.
        keywords: List of keywords.
        publication_year: Year of publication.
        venue: Publication venue.
        doi: Digital Object Identifier.
        arxiv_id: ArXiv identifier.
        introduction: Introduction section content.
        methodology: Methodology section content.
        results: Results section content.
        discussion: Discussion section content.
        conclusion: Conclusion section content.
        sections: List of structured sections.
        citations: List of citations/references.
        research_field: General research field.
        research_topics: Specific research topics.
        key_findings: List of key findings.
        limitations: List of limitations mentioned.
        future_work: List of future work suggestions.
    """

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
