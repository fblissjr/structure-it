"""Schema for web article and blog post extraction."""

from structure_it.schemas.base import BaseSchema


class ArticleAuthor(BaseSchema):
    """Article author information."""

    name: str
    bio: str | None = None
    url: str | None = None
    twitter: str | None = None


class ArticleImage(BaseSchema):
    """Image in article."""

    url: str
    alt_text: str | None = None
    caption: str | None = None


class ArticleSection(BaseSchema):
    """Section of article."""

    heading: str
    content: str
    level: int = 2  # Heading level (h2, h3, etc.)


class ArticleLink(BaseSchema):
    """Link in article."""

    url: str
    anchor_text: str
    context: str | None = None


class CodeBlock(BaseSchema):
    """Code block in article."""

    code: str
    language: str | None = None
    caption: str | None = None


class WebArticle(BaseSchema):
    """Structured web article or blog post."""

    title: str
    subtitle: str | None = None
    author: ArticleAuthor | None = None
    published_date: str | None = None
    modified_date: str | None = None
    url: str | None = None

    # Content
    summary: str | None = None
    introduction: str | None = None
    main_content: str
    conclusion: str | None = None
    sections: list[ArticleSection] = []

    # Media
    featured_image: ArticleImage | None = None
    images: list[ArticleImage] = []
    code_blocks: list[CodeBlock] = []

    # Metadata
    categories: list[str] = []
    tags: list[str] = []
    reading_time_minutes: int | None = None
    word_count: int | None = None

    # Structured information
    key_points: list[str] = []
    takeaways: list[str] = []
    links: list[ArticleLink] = []
    related_articles: list[str] = []

    # Technical content
    technologies_mentioned: list[str] = []
    tools_mentioned: list[str] = []
    frameworks_mentioned: list[str] = []

    # SEO
    meta_description: str | None = None
    meta_keywords: list[str] = []
