# PDF-to-MD-LLM Test Suite

This directory contains the test suite for the pdf-to-md-llm project.

## Overview

The test suite uses **pytest** as the testing framework and includes comprehensive unit tests that mock all LLM API calls to avoid costs during testing.

## Test Structure

```
tests/
├── conftest.py              # Shared pytest fixtures and configuration
├── README.md                # This file
├── unit/                    # Unit tests (no external API calls)
│   ├── __init__.py
│   ├── test_converter.py    # Tests for PDF conversion and chunking logic
│   ├── test_providers.py    # Tests for AI provider abstraction (mocked APIs)
│   └── test_cli.py          # Tests for CLI commands
└── test_*.py                # Legacy integration tests (require API keys)
```

## Test Framework

We use **pytest** with the following plugins:
- `pytest` - Main testing framework
- `pytest-mock` - Enhanced mocking capabilities

## Running Tests

### Run All Unit Tests

```bash
pytest tests/unit/
```

### Run Specific Test File

```bash
pytest tests/unit/test_converter.py
pytest tests/unit/test_providers.py
pytest tests/unit/test_cli.py
```

### Run Specific Test Class or Function

```bash
# Run a specific test class
pytest tests/unit/test_converter.py::TestChunkPages

# Run a specific test function
pytest tests/unit/test_converter.py::TestChunkPages::test_chunk_pages_basic
```

### Run Tests with Coverage

```bash
# Install coverage first
uv add --dev pytest-cov

# Run with coverage report
pytest tests/unit/ --cov=pdf_to_md_llm --cov-report=term-missing
```

### Run Tests in Verbose Mode

```bash
pytest tests/unit/ -v
```

### Run Tests with Output

```bash
pytest tests/unit/ -s
```

## Test Categories

Tests are marked with pytest markers:

- `@pytest.mark.unit` - Unit tests that don't require external services (DEFAULT for tests/unit/)
- `@pytest.mark.integration` - Integration tests that may require API keys

To run only unit tests:
```bash
pytest -m unit
```

## Key Features

### 1. No LLM API Calls

All tests in `tests/unit/` use mocking to avoid calling actual LLM APIs:
- **Anthropic API** - Mocked using `unittest.mock`
- **OpenAI API** - Mocked using `unittest.mock`
- **PyMuPDF** - PDF extraction is mocked to avoid file I/O dependencies

### 2. Test Coverage

The unit tests cover:
- **Chunking logic** (`chunk_pages`, `chunk_vision_pages`)
- **PDF extraction** (text and vision modes with mocked PyMuPDF)
- **Provider abstraction** (Anthropic and OpenAI providers)
- **Error handling** (TruncationError, API key validation)
- **CLI commands** (convert, batch, models)
- **Provider factory** (`get_provider`)

### 3. Shared Fixtures

Common test fixtures are defined in `conftest.py`:
- `mock_anthropic_client` - Pre-configured mock Anthropic client
- `mock_openai_client` - Pre-configured mock OpenAI client
- `sample_pdf_pages` - Sample PDF text pages
- `sample_vision_pages` - Sample vision pages with images
- `sample_markdown_output` - Sample markdown output

## Writing New Tests

### Example Test

```python
import pytest
from unittest.mock import Mock, patch

def test_my_function():
    """Test description."""
    # Arrange
    mock_client = Mock()
    mock_client.method.return_value = "expected_value"

    # Act
    with patch('module.Client', return_value=mock_client):
        result = my_function()

    # Assert
    assert result == "expected_value"
    mock_client.method.assert_called_once()
```

### Using Fixtures

```python
def test_with_fixture(mock_anthropic_client):
    """Test using a shared fixture."""
    # mock_anthropic_client is automatically injected
    result = some_function_using_anthropic(mock_anthropic_client)
    assert result is not None
```

## Legacy Integration Tests

The root `tests/` directory contains legacy integration tests that make real API calls:
- `test_truncation.py` - Tests TruncationError with Anthropic (requires ANTHROPIC_API_KEY)
- `test_truncation_openai.py` - Tests TruncationError with OpenAI (requires OPENAI_API_KEY)
- `test_max_tokens.py` - Tests token limit handling

**Note:** These tests are NOT run by default and require valid API keys.

## Continuous Integration

For CI/CD pipelines, run only unit tests to avoid API costs:

```bash
pytest tests/unit/ --tb=short
```

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed in development mode:

```bash
uv pip install -e .
```

### Mock Not Working

Ensure you're patching the correct location. Patch where the object is **used**, not where it's **defined**:

```python
# If converter.py does: from providers import get_provider
# Then patch in converter's namespace:
@patch('pdf_to_md_llm.converter.get_provider')

# NOT:
@patch('pdf_to_md_llm.providers.get_provider')  # Wrong!
```

## Contributing

When adding new features:
1. Write unit tests first (TDD approach)
2. Mock all external API calls
3. Ensure tests are isolated and repeatable
4. Add docstrings to test functions
5. Run tests before committing: `pytest tests/unit/`

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-mock documentation](https://pytest-mock.readthedocs.io/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
