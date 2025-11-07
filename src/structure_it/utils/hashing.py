"""SHA256-based deterministic ID generation.

Inspired by star-schema-llm-context's hash-based ID system.
Uses SHA256 for deterministic, collision-resistant identifiers.
"""

import hashlib
from typing import Any


def generate_id(*components: Any) -> str:
    """Generate a deterministic SHA256-based ID from components.

    This function creates a unique identifier by hashing the concatenation
    of all provided components. The same inputs will always produce the
    same ID, making it deterministic and suitable for deduplication.

    Args:
        *components: Variable number of components to hash together.
                    Each component is converted to string before hashing.

    Returns:
        64-character hexadecimal SHA256 hash string.

    Examples:
        >>> generate_id("project", "path/to/file.py")
        'a3f5...'  # 64-char hash

        >>> generate_id("user@example.com", "2025-01-01", "session")
        'b7e2...'  # Different hash

        >>> # Same inputs = same hash (deterministic)
        >>> id1 = generate_id("foo", "bar")
        >>> id2 = generate_id("foo", "bar")
        >>> id1 == id2
        True
    """
    # Convert all components to strings and concatenate
    combined = "".join(str(c) for c in components)

    # Generate SHA256 hash
    hash_obj = hashlib.sha256(combined.encode("utf-8"))

    # Return hexadecimal digest
    return hash_obj.hexdigest()


def generate_entity_id(source_url: str, entity_type: str) -> str:
    """Generate ID for an extracted entity.

    Args:
        source_url: URL or path of the source document.
        entity_type: Type of entity (e.g., 'academic_paper', 'article').

    Returns:
        SHA256 hash of source_url + entity_type.

    Examples:
        >>> generate_entity_id("https://example.com/article", "article")
        'c8a9...'
    """
    return generate_id(source_url, entity_type)


def generate_relationship_id(source_id: str, target_id: str, relationship_type: str) -> str:
    """Generate ID for a relationship between entities.

    Args:
        source_id: ID of the source entity.
        target_id: ID of the target entity.
        relationship_type: Type of relationship (e.g., 'cites', 'references').

    Returns:
        SHA256 hash of source_id + target_id + relationship_type.

    Examples:
        >>> generate_relationship_id("abc...", "def...", "cites")
        '1f3e...'
    """
    return generate_id(source_id, target_id, relationship_type)


def generate_content_id(content: str) -> str:
    """Generate ID based on content hash.

    Useful for deduplication - same content always produces same ID.

    Args:
        content: The content to hash.

    Returns:
        SHA256 hash of the content.

    Examples:
        >>> content = "This is my article content..."
        >>> generate_content_id(content)
        '7d4c...'
    """
    return generate_id(content)
