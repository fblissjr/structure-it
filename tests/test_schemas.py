"""Tests for schema definitions."""

import pytest
from pydantic import ValidationError

from structure_it.schemas import BaseSchema


class SampleSchema(BaseSchema):
    """Sample schema for testing."""

    name: str
    value: int
    optional_field: str | None = None


def test_base_schema_creation() -> None:
    """Test creating a schema instance."""
    schema = SampleSchema(name="test", value=42)
    assert schema.name == "test"
    assert schema.value == 42
    assert schema.optional_field is None


def test_base_schema_validation() -> None:
    """Test schema validation."""
    with pytest.raises(ValidationError):
        SampleSchema(name="test")  # Missing required field 'value'


def test_base_schema_to_dict() -> None:
    """Test converting schema to dictionary."""
    schema = SampleSchema(name="test", value=42, optional_field="optional")
    result = schema.to_dict()

    assert isinstance(result, dict)
    assert result["name"] == "test"
    assert result["value"] == 42
    assert result["optional_field"] == "optional"


def test_base_schema_to_json() -> None:
    """Test converting schema to JSON."""
    schema = SampleSchema(name="test", value=42)
    json_str = schema.to_json()

    assert isinstance(json_str, str)
    assert '"name": "test"' in json_str
    assert '"value": 42' in json_str


def test_base_schema_extra_fields_forbidden() -> None:
    """Test that extra fields are forbidden."""
    with pytest.raises(ValidationError):
        SampleSchema(name="test", value=42, extra_field="not allowed")
