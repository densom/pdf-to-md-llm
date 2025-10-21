"""Pytest configuration and shared fixtures for all tests."""

import pytest
from unittest.mock import Mock


@pytest.fixture
def mock_anthropic_client():
    """Fixture providing a mocked Anthropic client."""
    mock_client = Mock()
    mock_message = Mock()
    mock_message.content = [Mock(text="# Mocked Anthropic Response")]
    mock_message.stop_reason = "end_turn"
    mock_client.messages.create.return_value = mock_message
    mock_client.models.list.return_value = Mock(
        data=[
            Mock(id="claude-3-5-sonnet-20241022"),
            Mock(id="claude-3-5-haiku-20241022"),
        ]
    )
    return mock_client


@pytest.fixture
def mock_openai_client():
    """Fixture providing a mocked OpenAI client."""
    mock_client = Mock()

    # Mock Chat Completions API
    mock_choice = Mock()
    mock_choice.message.content = "# Mocked OpenAI Response"
    mock_choice.finish_reason = "stop"
    mock_response = Mock(choices=[mock_choice])
    mock_client.chat.completions.create.return_value = mock_response

    # Mock Responses API (for GPT-5)
    mock_output_item = Mock(content="# Mocked GPT-5 Response")
    mock_responses_response = Mock(output=[mock_output_item], status="completed")
    mock_client.responses.create.return_value = mock_responses_response

    # Mock models list
    mock_client.models.list.return_value = Mock(
        data=[
            Mock(id="gpt-4o"),
            Mock(id="gpt-4o-mini"),
            Mock(id="gpt-5o-preview"),
        ]
    )

    return mock_client


@pytest.fixture
def sample_pdf_pages():
    """Fixture providing sample PDF pages as text."""
    return [
        "Page 1: Introduction\nThis is the first page.",
        "Page 2: Content\nThis is the second page.",
        "Page 3: Conclusion\nThis is the third page.",
    ]


@pytest.fixture
def sample_vision_pages():
    """Fixture providing sample vision pages with images."""
    return [
        {
            "page_number": 1,
            "text": "Page 1 text",
            "image": "base64_encoded_image_1",
            "media_type": "image/png"
        },
        {
            "page_number": 2,
            "text": "Page 2 text",
            "image": "base64_encoded_image_2",
            "media_type": "image/png"
        },
    ]


@pytest.fixture
def sample_markdown_output():
    """Fixture providing sample markdown output."""
    return """# Sample Document

## Introduction
This is a sample markdown document.

## Content
- Point 1
- Point 2

## Conclusion
End of document.
"""
