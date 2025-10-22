"""Unit tests for providers.py module - tests AI provider abstraction with mocked API calls."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pdf_to_md_llm.providers import (
    AnthropicProvider,
    OpenAIProvider,
    get_provider,
    validate_api_key_available,
    TruncationError,
)


class TestAnthropicProvider:
    """Test the AnthropicProvider class with mocked Anthropic API."""

    @patch('anthropic.Anthropic')
    def test_anthropic_convert_to_markdown_success(self, mock_anthropic_class):
        """Test successful text-to-markdown conversion with Anthropic."""
        # Mock Anthropic client
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock(text="# Converted Markdown")]
        mock_message.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_message
        mock_anthropic_class.return_value = mock_client

        # Create provider and convert
        provider = AnthropicProvider(api_key="test_key")
        result = provider.convert_to_markdown(
            text="Test input text",
            max_tokens=4096,
        )

        assert result == "# Converted Markdown"
        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args[1]
        assert call_args['max_tokens'] == 4096
        assert call_args['model'] == provider.model
        assert 'messages' in call_args

    @patch('anthropic.Anthropic')
    def test_anthropic_convert_to_markdown_truncation_error(self, mock_anthropic_class):
        """Test that TruncationError is raised when max_tokens is reached."""
        # Mock Anthropic client with max_tokens stop reason
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock(text="# Partial")]
        mock_message.stop_reason = "max_tokens"
        mock_client.messages.create.return_value = mock_message
        mock_anthropic_class.return_value = mock_client

        provider = AnthropicProvider(api_key="test_key")

        with pytest.raises(TruncationError) as exc_info:
            provider.convert_to_markdown(text="Test input", max_tokens=100)

        assert "max_tokens" in str(exc_info.value).lower()

    @patch('anthropic.Anthropic')
    def test_anthropic_convert_to_markdown_vision_success(self, mock_anthropic_class):
        """Test successful vision-to-markdown conversion with Anthropic."""
        # Mock Anthropic client
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock(text="# Vision Markdown")]
        mock_message.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_message
        mock_anthropic_class.return_value = mock_client

        # Create provider and convert
        provider = AnthropicProvider(api_key="test_key")
        pages = [
            {
                "page_num": 0,  # 0-indexed
                "text": "Page 1 text",
                "image_base64": "base64_encoded_image",
                "media_type": "image/png"
            }
        ]
        result = provider.convert_to_markdown_vision(
            pages=pages,
            max_tokens=4096,
        )

        assert result == "# Vision Markdown"
        mock_client.messages.create.assert_called_once()

    @patch('anthropic.Anthropic')
    def test_anthropic_convert_with_custom_prompt(self, mock_anthropic_class):
        """Test conversion with custom system prompt."""
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock(text="# Custom Output")]
        mock_message.stop_reason = "end_turn"
        mock_client.messages.create.return_value = mock_message
        mock_anthropic_class.return_value = mock_client

        provider = AnthropicProvider(api_key="test_key")
        result = provider.convert_to_markdown(
            text="Test",
            max_tokens=4096,
            custom_system_prompt="Custom instructions",
        )

        assert result == "# Custom Output"
        call_args = mock_client.messages.create.call_args[1]
        assert "Custom instructions" in call_args['system']

    @patch('anthropic.Anthropic')
    def test_anthropic_validate_config_success(self, mock_anthropic_class):
        """Test API key validation with valid key."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        provider = AnthropicProvider(api_key="valid_key")
        is_valid = provider.validate_config()

        assert is_valid is True

    @patch('anthropic.Anthropic')
    def test_anthropic_validate_config_failure(self, mock_anthropic_class):
        """Test API key validation with invalid/empty key."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        # Test with empty key
        provider = AnthropicProvider(api_key="")
        is_valid = provider.validate_config()
        assert is_valid is False

        # Test with placeholder key
        provider = AnthropicProvider(api_key="your-api-key-here")
        is_valid = provider.validate_config()
        assert is_valid is False

    @patch('anthropic.Anthropic')
    def test_anthropic_list_available_models(self, mock_anthropic_class):
        """Test listing available models."""
        mock_client = Mock()
        mock_model1 = Mock(id="claude-3-5-sonnet-20241022", created_at=1700000001)
        mock_model2 = Mock(id="claude-3-5-haiku-20241022", created_at=1700000000)
        mock_models_response = Mock(data=[mock_model1, mock_model2])
        mock_client.models.list.return_value = mock_models_response
        mock_anthropic_class.return_value = mock_client

        provider = AnthropicProvider(api_key="test_key")
        models = provider.list_available_models()

        assert len(models) == 2
        assert models[0]['id'] == "claude-3-5-sonnet-20241022"
        assert models[1]['id'] == "claude-3-5-haiku-20241022"


class TestOpenAIProvider:
    """Test the OpenAIProvider class with mocked OpenAI API."""

    @patch('openai.OpenAI')
    def test_openai_convert_to_markdown_success(self, mock_openai_class):
        """Test successful text-to-markdown conversion with OpenAI."""
        # Mock OpenAI client (Chat Completions API)
        mock_client = Mock()
        mock_choice = Mock()
        mock_choice.message.content = "# Converted Markdown"
        mock_choice.finish_reason = "stop"
        mock_usage = Mock()
        mock_usage.completion_tokens = 100
        mock_response = Mock(choices=[mock_choice], usage=mock_usage)
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        # Create provider and convert
        provider = OpenAIProvider(api_key="test_key", model="gpt-4o-mini")
        result = provider.convert_to_markdown(
            text="Test input text",
            max_tokens=4096,
        )

        assert result == "# Converted Markdown"
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        assert call_args['max_tokens'] == 4096
        assert call_args['model'] == "gpt-4o-mini"

    @patch('openai.OpenAI')
    def test_openai_convert_to_markdown_truncation_error(self, mock_openai_class):
        """Test that TruncationError is raised when length limit is reached."""
        # Mock OpenAI client with length finish reason
        mock_client = Mock()
        mock_choice = Mock()
        mock_choice.message.content = "# Partial"
        mock_choice.finish_reason = "length"
        mock_usage = Mock()
        mock_usage.completion_tokens = 100
        mock_response = Mock(choices=[mock_choice], usage=mock_usage)
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider(api_key="test_key", model="gpt-4o-mini")

        with pytest.raises(TruncationError) as exc_info:
            provider.convert_to_markdown(text="Test input", max_tokens=100)

        assert "truncated" in str(exc_info.value).lower()

    @patch('openai.OpenAI')
    def test_openai_convert_vision_mode(self, mock_openai_class):
        """Test vision-to-markdown conversion with OpenAI."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_choice = Mock()
        mock_choice.message.content = "# Vision Markdown"
        mock_choice.finish_reason = "stop"
        mock_response = Mock(choices=[mock_choice])
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider(api_key="test_key", model="gpt-4o-mini")
        pages = [
            {
                "page_num": 0,  # 0-indexed
                "text": "Page 1 text",
                "image_base64": "base64_encoded_image",
                "media_type": "image/png"
            }
        ]
        result = provider.convert_to_markdown_vision(
            pages=pages,
            max_tokens=4096,
        )

        assert result == "# Vision Markdown"
        mock_client.chat.completions.create.assert_called_once()

    @patch('openai.OpenAI')
    def test_openai_responses_api_gpt5(self, mock_openai_class):
        """Test that GPT-5 models use the Responses API."""
        # Mock OpenAI client with Responses API
        mock_client = Mock()
        mock_output_item = Mock(content="# GPT-5 Markdown", status="completed")
        mock_usage = Mock()
        mock_usage.input_tokens = 50
        mock_usage.output_tokens = 100
        mock_response = Mock(output=[mock_output_item], output_text="# GPT-5 Markdown", usage=mock_usage)
        mock_client.responses.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider(api_key="test_key", model="gpt-5o-preview")
        result = provider.convert_to_markdown(
            text="Test input",
            max_tokens=4096,
        )

        assert result == "# GPT-5 Markdown"
        # Should use responses.create for GPT-5
        mock_client.responses.create.assert_called_once()
        # Should NOT use chat.completions.create
        mock_client.chat.completions.create.assert_not_called()

    @patch('openai.OpenAI')
    def test_openai_validate_config_success(self, mock_openai_class):
        """Test API key validation with successful response."""
        mock_client = Mock()
        mock_client.models.list.return_value = Mock()  # Successful call
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider(api_key="valid_key")
        is_valid = provider.validate_config()

        assert is_valid is True

    @patch('openai.OpenAI')
    def test_openai_validate_config_failure(self, mock_openai_class):
        """Test API key validation with invalid/empty key."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Test with empty key
        provider = OpenAIProvider(api_key="")
        is_valid = provider.validate_config()
        assert is_valid is False

        # Test with placeholder key
        provider = OpenAIProvider(api_key="your-api-key-here")
        is_valid = provider.validate_config()
        assert is_valid is False

    @patch('openai.OpenAI')
    def test_openai_list_available_models(self, mock_openai_class):
        """Test listing available models."""
        mock_client = Mock()
        mock_model1 = Mock(id="gpt-4o", created=1700000000)
        mock_model2 = Mock(id="gpt-4o-mini", created=1700000001)
        mock_models_response = Mock(data=[mock_model1, mock_model2])
        mock_client.models.list.return_value = mock_models_response
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider(api_key="test_key")
        models = provider.list_available_models()

        assert len(models) == 2
        # Models are sorted by created date (most recent first), so gpt-4o-mini should be first
        assert models[0]['id'] == "gpt-4o-mini"
        assert models[1]['id'] == "gpt-4o"


class TestProviderFactory:
    """Test the get_provider factory function."""

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_anthropic_key'})
    @patch('anthropic.Anthropic')
    def test_get_provider_anthropic(self, mock_anthropic):
        """Test getting Anthropic provider."""
        provider = get_provider("anthropic")
        assert isinstance(provider, AnthropicProvider)

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_openai_key'})
    @patch('openai.OpenAI')
    def test_get_provider_openai(self, mock_openai):
        """Test getting OpenAI provider."""
        provider = get_provider("openai")
        assert isinstance(provider, OpenAIProvider)

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'})
    @patch('anthropic.Anthropic')
    def test_get_provider_with_custom_model(self, mock_anthropic):
        """Test getting provider with custom model."""
        provider = get_provider("anthropic", model="claude-3-5-sonnet-20241022")
        assert provider.model == "claude-3-5-sonnet-20241022"

    def test_get_provider_invalid_name(self):
        """Test that invalid provider name raises ValueError."""
        with pytest.raises(ValueError):
            get_provider("invalid_provider")


class TestValidateApiKeyAvailable:
    """Test the validate_api_key_available utility function."""

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test_key'})
    def test_validate_api_key_available_success(self):
        """Test validation with available API key."""
        is_valid, error_msg = validate_api_key_available("anthropic", None)
        assert is_valid is True
        assert error_msg is None

    def test_validate_api_key_available_explicit_key(self):
        """Test validation with explicitly provided API key."""
        is_valid, error_msg = validate_api_key_available("anthropic", "explicit_key")
        assert is_valid is True
        assert error_msg is None

    @patch.dict('os.environ', {}, clear=True)
    def test_validate_api_key_missing_returns_error(self):
        """Test that missing API key returns error tuple."""
        is_valid, error_msg = validate_api_key_available("anthropic", None)
        assert is_valid is False
        assert "ANTHROPIC_API_KEY" in error_msg
