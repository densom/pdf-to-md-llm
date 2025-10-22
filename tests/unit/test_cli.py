"""Unit tests for cli.py module - tests CLI commands with mocked dependencies."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from pdf_to_md_llm.cli import cli, convert, batch, models


class TestConvertCommand:
    """Test the convert CLI command."""

    @patch('pdf_to_md_llm.cli.validate_api_key_available')
    @patch('pdf_to_md_llm.cli.convert_pdf_to_markdown')
    def test_convert_command_basic(self, mock_convert, mock_validate):
        """Test basic convert command execution."""
        # Mock validation and conversion
        mock_validate.return_value = (True, None)  # Returns tuple (is_valid, error_msg)
        mock_convert.return_value = "# Markdown output"

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create a dummy PDF file
            with open('test.pdf', 'w') as f:
                f.write('dummy pdf content')

            result = runner.invoke(convert, ['test.pdf'])

            assert result.exit_code == 0
            mock_validate.assert_called_once()
            mock_convert.assert_called_once()

    @patch('pdf_to_md_llm.cli.validate_api_key_available')
    @patch('pdf_to_md_llm.cli.convert_pdf_to_markdown')
    def test_convert_command_with_output_path(self, mock_convert, mock_validate):
        """Test convert command with output path specified."""
        mock_validate.return_value = (True, None)
        mock_convert.return_value = "# Markdown output"

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('test.pdf', 'w') as f:
                f.write('dummy')

            result = runner.invoke(convert, ['test.pdf', '--output', 'output.md'])

            assert result.exit_code == 0
            # Verify output path was passed to convert function
            call_args = mock_convert.call_args[1]
            assert call_args['output_path'] == 'output.md'

    @patch('pdf_to_md_llm.cli.validate_api_key_available')
    @patch('pdf_to_md_llm.cli.convert_pdf_to_markdown')
    def test_convert_command_with_vision_flag(self, mock_convert, mock_validate):
        """Test convert command with vision flag enabled."""
        mock_validate.return_value = (True, None)
        mock_convert.return_value = "# Vision markdown"

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('test.pdf', 'w') as f:
                f.write('dummy')

            result = runner.invoke(convert, ['test.pdf', '--vision'])

            assert result.exit_code == 0
            call_args = mock_convert.call_args[1]
            assert call_args['use_vision'] is True

    @patch('pdf_to_md_llm.cli.validate_api_key_available')
    @patch('pdf_to_md_llm.cli.convert_pdf_to_markdown')
    def test_convert_command_with_custom_chunks(self, mock_convert, mock_validate):
        """Test convert command with custom pages per chunk."""
        mock_validate.return_value = (True, None)
        mock_convert.return_value = "# Markdown"

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('test.pdf', 'w') as f:
                f.write('dummy')

            result = runner.invoke(convert, ['test.pdf', '--pages-per-chunk', '10'])

            assert result.exit_code == 0
            call_args = mock_convert.call_args[1]
            assert call_args['pages_per_chunk'] == 10

    @patch('pdf_to_md_llm.cli.validate_api_key_available')
    @patch('pdf_to_md_llm.cli.convert_pdf_to_markdown')
    def test_convert_command_with_openai_provider(self, mock_convert, mock_validate):
        """Test convert command with OpenAI provider."""
        mock_validate.return_value = (True, None)
        mock_convert.return_value = "# Markdown"

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('test.pdf', 'w') as f:
                f.write('dummy')

            result = runner.invoke(convert, ['test.pdf', '--provider', 'openai'])

            assert result.exit_code == 0
            call_args = mock_convert.call_args[1]
            assert call_args['provider'] == 'openai'

    @patch('pdf_to_md_llm.cli.validate_api_key_available')
    def test_convert_command_missing_api_key(self, mock_validate):
        """Test that missing API key produces error."""
        mock_validate.return_value = (False, "API key not found")

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('test.pdf', 'w') as f:
                f.write('dummy')

            result = runner.invoke(convert, ['test.pdf'])

            assert result.exit_code != 0
            assert "API key not found" in result.output

    @patch('pdf_to_md_llm.cli.validate_api_key_available')
    @patch('pdf_to_md_llm.cli.convert_pdf_to_markdown')
    def test_convert_command_with_custom_model(self, mock_convert, mock_validate):
        """Test convert command with custom model specified."""
        mock_validate.return_value = (True, None)
        mock_convert.return_value = "# Markdown"

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('test.pdf', 'w') as f:
                f.write('dummy')

            result = runner.invoke(convert, ['test.pdf', '--model', 'gpt-4o'])

            assert result.exit_code == 0
            call_args = mock_convert.call_args[1]
            assert call_args['model'] == 'gpt-4o'


class TestBatchCommand:
    """Test the batch CLI command."""

    @patch('pdf_to_md_llm.cli.validate_api_key_available')
    @patch('pdf_to_md_llm.cli.batch_convert')
    def test_batch_command_basic(self, mock_batch_convert, mock_validate):
        """Test basic batch command execution."""
        mock_validate.return_value = (True, None)

        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create input and output directories
            import os
            os.makedirs('input')
            os.makedirs('output')

            result = runner.invoke(batch, ['input', 'output'])

            assert result.exit_code == 0
            mock_batch_convert.assert_called_once()

    @patch('pdf_to_md_llm.cli.validate_api_key_available')
    @patch('pdf_to_md_llm.cli.batch_convert')
    def test_batch_command_with_max_workers(self, mock_batch_convert, mock_validate):
        """Test batch command with custom max workers."""
        mock_validate.return_value = (True, None)

        runner = CliRunner()
        with runner.isolated_filesystem():
            import os
            os.makedirs('input')
            os.makedirs('output')

            result = runner.invoke(batch, ['input', 'output', '--threads', '8'])

            assert result.exit_code == 0
            call_args = mock_batch_convert.call_args[1]
            assert call_args['threads'] == 8

    @patch('pdf_to_md_llm.cli.validate_api_key_available')
    @patch('pdf_to_md_llm.cli.batch_convert')
    def test_batch_command_with_vision(self, mock_batch_convert, mock_validate):
        """Test batch command with vision enabled."""
        mock_validate.return_value = (True, None)

        runner = CliRunner()
        with runner.isolated_filesystem():
            import os
            os.makedirs('input')
            os.makedirs('output')

            result = runner.invoke(batch, ['input', 'output', '--vision'])

            assert result.exit_code == 0
            call_args = mock_batch_convert.call_args[1]
            assert call_args['use_vision'] is True


class TestModelsCommand:
    """Test the models CLI command."""

    @patch('pdf_to_md_llm.providers.list_models_for_providers')
    def test_models_command_success(self, mock_list_models):
        """Test models command with successful response."""
        mock_list_models.return_value = {
            "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
            "openai": ["gpt-4o", "gpt-4o-mini"],
        }

        runner = CliRunner()
        result = runner.invoke(models)

        assert result.exit_code == 0
        assert "anthropic" in result.output.lower()
        assert "openai" in result.output.lower()
        assert "claude" in result.output.lower() or "sonnet" in result.output.lower()
        assert "gpt" in result.output.lower()

    @patch('pdf_to_md_llm.providers.list_models_for_providers')
    def test_models_command_no_api_keys(self, mock_list_models):
        """Test models command when no API keys are available."""
        mock_list_models.return_value = {}

        runner = CliRunner()
        result = runner.invoke(models)

        assert result.exit_code == 0
        # Should still complete but show no models

    @patch('pdf_to_md_llm.providers.list_models_for_providers')
    def test_models_command_with_error(self, mock_list_models):
        """Test models command when an error occurs."""
        mock_list_models.side_effect = Exception("API error")

        runner = CliRunner()
        result = runner.invoke(models)

        # Should handle error gracefully
        assert "API error" in result.output or result.exit_code != 0


class TestCLIValidation:
    """Test CLI input validation."""

    def test_convert_nonexistent_file(self):
        """Test that convert command fails with nonexistent file."""
        runner = CliRunner()
        result = runner.invoke(convert, ['nonexistent.pdf'])

        assert result.exit_code != 0
        assert "does not exist" in result.output.lower() or "error" in result.output.lower()

    @patch('pdf_to_md_llm.cli.validate_api_key_available')
    @patch('pdf_to_md_llm.cli.convert_pdf_to_markdown')
    def test_convert_with_max_tokens(self, mock_convert, mock_validate):
        """Test convert command with custom max tokens."""
        mock_validate.return_value = (True, None)
        mock_convert.return_value = "# Markdown"

        runner = CliRunner()
        with runner.isolated_filesystem():
            with open('test.pdf', 'w') as f:
                f.write('dummy')

            result = runner.invoke(convert, ['test.pdf', '--max-tokens', '8000'])

            assert result.exit_code == 0
            call_args = mock_convert.call_args[1]
            assert call_args['max_tokens'] == 8000
