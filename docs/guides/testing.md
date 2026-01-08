# Testing Guide

This guide covers the testing strategy and best practices for `structure-it`.

## Testing Philosophy

We follow a comprehensive testing strategy that covers:
1.  **Unit Tests**: For individual components (schemas, extractors, utilities).
2.  **Integration Tests**: For verifying component interactions (e.g., Scrapy pipeline flow).
3.  **Schema Validation**: Ensuring data models are correct and robust.

## Test Categories

### 1. Unit Tests
Located in `tests/`. These are fast-running tests that verify isolated logic.

*   **Schema Tests**: Verify Pydantic models, validation rules, and serialization (`test_schemas.py`, `test_civic_schema.py`).
*   **Extractor Tests**: Verify prompt generation and API handling (`test_policy_extractor.py`).
*   **Storage Tests**: Verify database interactions and query logic (`test_star_schema.py`).

### 2. Integration Tests
Tests that verify the interaction between multiple components.

*   **Scrapy Integration**: `test_scrapy_integration.py` verifies the pipeline flow from scraping to storage, mocking external dependencies like the LLM and network where appropriate to keep tests deterministic.

## Running Tests

We use `pytest` as our test runner.

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_star_schema.py

# Run with coverage report
uv run pytest --cov=structure_it tests/
```

## Writing New Tests

### Naming Conventions
*   Test files: `test_*.py`
*   Test classes: `Test*`
*   Test functions: `test_*`

### Mocking
Use `unittest.mock` to mock external services (LLM APIs, Network calls). This ensures tests are:
*   **Fast**: No network latency.
*   **Deterministic**: No flaky failures due to API rate limits or outages.
*   **Cost-effective**: No LLM token usage during testing.

Example of mocking the Gemini Extractor:

```python
@patch("structure_it.extractors.gemini.GeminiExtractor.extract")
async def test_extraction(mock_extract):
    mock_extract.return_value = MySchema(...)
    # ... run test ...
```

### Fixtures
Use `pytest` fixtures for common setup (e.g., temporary databases, mock configs).

```python
@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test.db"
    # ... setup ...
    yield db_path
    # ... cleanup ...
```
