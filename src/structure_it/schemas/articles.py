"""Schema for web article and blog post extraction."""

from structure_it.schemas.base import BaseSchema


class ArticleAuthor(BaseSchema):
    """Article author information.

    Attributes:
        name: Name of the author.
        bio: Author biography.
        url: URL to author's profile or website.
        twitter: Author's Twitter/X handle.
    """

    name: str
    bio: str | None = None
    url: str | None = None
    twitter: str | None = None


class ArticleImage(BaseSchema):
    """Image in article.

    Attributes:
        url: URL of the image.
        alt_text: Alternative text for accessibility.
        caption: Image caption.
    """

    url: str
    alt_text: str | None = None
    caption: str | None = None


class ArticleSection(BaseSchema):
    """Section of article.

    Attributes:
        heading: Section heading.
        content: Text content of the section.
        level: Heading level (e.g., 2 for h2).
    """

    heading: str
    content: str
    level: int = 2  # Heading level (h2, h3, etc.)


class ArticleLink(BaseSchema):
    """Link in article.

    Attributes:
        url: Target URL.
        anchor_text: Text of the link.
        context: Surrounding context text.
    """

    url: str
    anchor_text: str
    context: str | None = None


class CodeBlock(BaseSchema):
    """Code block in article.

    Attributes:
        code: Code snippet.
        language: Programming language.
        caption: Caption or description.
    """

    code: str
    language: str | None = None
    caption: str | None = None


class WebArticle(BaseSchema):
    """Structured web article or blog post.

    Attributes:
        title: Article title.
        subtitle: Article subtitle.
        author: Author information.
        published_date: Publication date string.
        modified_date: Last modified date string.
        url: Article URL.
        summary: Brief summary.
        introduction: Introduction text.
        main_content: Main content body.
        conclusion: Conclusion text.
        sections: List of article sections.
        featured_image: Main image.
        images: List of images in article.
        code_blocks: List of code blocks.
        categories: List of categories.
        tags: List of tags.
        reading_time_minutes: Estimated reading time in minutes.
        word_count: Word count.
        key_points: List of key points.
        takeaways: List of main takeaways.
        links: List of links in the article.
        related_articles: List of related article titles/links.
        technologies_mentioned: List of technologies mentioned.
        tools_mentioned: List of tools mentioned.
        frameworks_mentioned: List of frameworks mentioned.
        meta_description: SEO meta description.
        meta_keywords: SEO meta keywords.
    """

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
