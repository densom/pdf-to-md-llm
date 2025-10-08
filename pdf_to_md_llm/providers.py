"""
AI provider abstraction for PDF to Markdown conversion
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import os


class TruncationError(Exception):
    """Raised when API response is truncated due to max_tokens limit"""
    pass

# Shared conversion prompts
CONVERSION_PROMPT = """Convert this text from a PDF document to clean, well-structured markdown.

Requirements:
- Use proper heading hierarchy (# for main titles, ## for sections, ### for subsections)
- Convert any tables to proper markdown table format with aligned columns
- Convert tables to structured headings instead of markdown tables if they are complex
- Watch out for tables that span multiple pages - treat them as one table
- Clean up formatting artifacts from PDF extraction (broken lines, weird spacing)
- Use consistent bullet points and numbered lists
- Preserve all information - don't summarize or omit content
- ALWAYS Remove page numbers, headers, and footers if they appear
- Make the document scannable with clear structure

Output ONLY the markdown - no explanations or commentary.

Text to convert:

{text}"""

VISION_CONVERSION_PROMPT = """Convert these PDF pages to clean, well-structured markdown.

I'm providing both the page image and extracted text for each page. Use the IMAGE to understand layout, structure, tables, charts, and visual hierarchy. Use the TEXT to reduce hallucination and get accurate content.

Requirements:
- Use proper heading hierarchy (# for main titles, ## for sections, ### for subsections)
- **TABLES ARE CRITICAL**: Look carefully at the images for ANY tabular data (rows and columns). Tables often have:
  * Grid lines or borders
  * Aligned columns of text
  * Header rows with column titles
  * Question/Answer pairs in columns
  * Data organized in rows and columns
- When you detect tables:
  * Create proper markdown tables with | separators
  * Use the image to understand column structure and alignment
  * If a table spans multiple pages, MERGE it into ONE continuous table (don't repeat headers)
  * Preserve all rows and columns exactly as shown
- **REMOVE REPETITIVE ELEMENTS**: Page headers, footers, and contact information that repeat on every page should only appear ONCE in the output
- For charts/diagrams: describe them clearly in markdown
- Preserve visual formatting cues (bold sections, indentation, callouts)
- Handle multi-column layouts properly
- Preserve all information - don't summarize

Output ONLY the markdown - no explanations or commentary.

---
"""


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    def convert_to_markdown(self, text: str, max_tokens: int, custom_system_prompt: Optional[str] = None) -> str:
        """
        Convert text to markdown using the AI provider.

        Args:
            text: Text to convert
            max_tokens: Maximum tokens for response
            custom_system_prompt: Optional custom instructions to append to the system prompt

        Returns:
            Converted markdown text
        """
        pass

    @abstractmethod
    def convert_to_markdown_vision(
        self,
        pages: List[Dict[str, Any]],
        max_tokens: int,
        custom_system_prompt: Optional[str] = None
    ) -> str:
        """
        Convert pages with vision data to markdown using the AI provider.

        Args:
            pages: List of page dicts with 'text' and 'image_base64' keys
            max_tokens: Maximum tokens for response
            custom_system_prompt: Optional custom instructions to append to the system prompt

        Returns:
            Converted markdown text
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support vision mode"
        )

    def _build_vision_page_text(self, page: Dict[str, Any]) -> str:
        """
        Build the text description for a vision page.

        Args:
            page: Page dict with 'page_num', 'text', 'image_base64'

        Returns:
            Formatted text block for the page
        """
        page_num = page['page_num'] + 1  # Convert to 1-indexed for display
        return f"\n**Extracted text from page {page_num}:**\n\n{page['text']}\n\n---\n"

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate that the provider is properly configured.

        Returns:
            True if valid, False otherwise
        """
        pass

    @abstractmethod
    def list_available_models(self) -> List[Dict[str, Any]]:
        """
        List available models from this provider.

        Returns:
            List of dicts with model information (id, name, etc.)
        """
        pass


class AnthropicProvider(AIProvider):
    """Anthropic (Claude) AI provider"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-haiku-20241022"
    ):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model to use
        """
        import anthropic

        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def convert_to_markdown(self, text: str, max_tokens: int, custom_system_prompt: Optional[str] = None) -> str:
        """Convert text to markdown using Claude API"""
        prompt = CONVERSION_PROMPT.format(text=text)

        # Append custom system prompt if provided
        if custom_system_prompt and custom_system_prompt.strip():
            prompt = f"{prompt}\n\nAdditional Instructions:\n{custom_system_prompt.strip()}"

        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Check for truncation
        if message.stop_reason == "max_tokens":
            raise TruncationError(
                f"Response truncated at {message.usage.output_tokens} tokens. "
                f"The markdown conversion is incomplete. "
                f"Try reducing --pages-per-chunk (current max_tokens: {max_tokens})."
            )

        return message.content[0].text

    def convert_to_markdown_vision(
        self,
        pages: List[Dict[str, Any]],
        max_tokens: int,
        custom_system_prompt: Optional[str] = None
    ) -> str:
        """Convert pages with vision data to markdown using Claude API"""
        # Build multimodal content blocks
        content_blocks = []

        # Build instruction text (base prompt + optional custom prompt)
        instruction_text = VISION_CONVERSION_PROMPT
        if custom_system_prompt and custom_system_prompt.strip():
            instruction_text = f"{instruction_text}\nAdditional Instructions:\n{custom_system_prompt.strip()}\n\n---\n"

        # Add instruction text first
        content_blocks.append({
            "type": "text",
            "text": instruction_text
        })

        # Add each page's image and text
        for page in pages:
            # Add page image
            content_blocks.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": page['image_base64']
                }
            })

            # Add extracted text with context
            content_blocks.append({
                "type": "text",
                "text": self._build_vision_page_text(page)
            })

        # Make API call
        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": content_blocks
            }]
        )

        # Check for truncation
        if message.stop_reason == "max_tokens":
            raise TruncationError(
                f"Response truncated at {message.usage.output_tokens} tokens. "
                f"The markdown conversion is incomplete. "
                f"Try reducing --pages-per-chunk or --vision-pages-per-chunk (current max_tokens: {max_tokens})."
            )

        return message.content[0].text

    def validate_config(self) -> bool:
        """Validate Anthropic API key"""
        return bool(self.api_key and self.api_key != "your-api-key-here")

    def list_available_models(self) -> List[Dict[str, Any]]:
        """List available models from Anthropic"""
        # Query the Anthropic API for available models
        models = self.client.models.list()

        # Convert to list of dicts with relevant info
        model_list = []
        for model in models.data:
            model_list.append({
                'id': model.id,
                'name': model.display_name if hasattr(model, 'display_name') else model.id,
                'created': model.created_at if hasattr(model, 'created_at') else None
            })

        return model_list


class OpenAIProvider(AIProvider):
    """OpenAI (GPT) AI provider"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini"
    ):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use (e.g., gpt-4o, gpt-4-turbo, gpt-3.5-turbo)
        """
        from openai import OpenAI

        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        self.client = OpenAI(api_key=self.api_key)

    def convert_to_markdown(self, text: str, max_tokens: int, custom_system_prompt: Optional[str] = None) -> str:
        """Convert text to markdown using OpenAI API"""
        prompt = CONVERSION_PROMPT.format(text=text)

        # Append custom system prompt if provided
        if custom_system_prompt and custom_system_prompt.strip():
            prompt = f"{prompt}\n\nAdditional Instructions:\n{custom_system_prompt.strip()}"

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Check for truncation
        if response.choices[0].finish_reason == "length":
            tokens_used = response.usage.completion_tokens if response.usage else max_tokens
            raise TruncationError(
                f"Response truncated at {tokens_used} tokens. "
                f"The markdown conversion is incomplete. "
                f"Try reducing --pages-per-chunk (current max_tokens: {max_tokens})."
            )

        return response.choices[0].message.content

    def convert_to_markdown_vision(
        self,
        pages: List[Dict[str, Any]],
        max_tokens: int,
        custom_system_prompt: Optional[str] = None
    ) -> str:
        """Convert pages with vision data to markdown using OpenAI API"""
        # Build multimodal content blocks
        content_parts = []

        # Build instruction text (base prompt + optional custom prompt)
        instruction_text = VISION_CONVERSION_PROMPT
        if custom_system_prompt and custom_system_prompt.strip():
            instruction_text = f"{instruction_text}\nAdditional Instructions:\n{custom_system_prompt.strip()}\n\n---\n"

        # Add instruction text first
        content_parts.append({
            "type": "text",
            "text": instruction_text
        })

        # Add each page's image and text
        for page in pages:
            # Add page image
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{page['image_base64']}"
                }
            })

            # Add extracted text with context
            content_parts.append({
                "type": "text",
                "text": self._build_vision_page_text(page)
            })

        # Make API call
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": content_parts
            }]
        )

        # Check for truncation
        if response.choices[0].finish_reason == "length":
            tokens_used = response.usage.completion_tokens if response.usage else max_tokens
            raise TruncationError(
                f"Response truncated at {tokens_used} tokens. "
                f"The markdown conversion is incomplete. "
                f"Try reducing --pages-per-chunk or --vision-pages-per-chunk (current max_tokens: {max_tokens})."
            )

        return response.choices[0].message.content

    def validate_config(self) -> bool:
        """Validate OpenAI API key"""
        return bool(self.api_key and self.api_key != "your-api-key-here")

    def list_available_models(self) -> List[Dict[str, Any]]:
        """List available models from OpenAI"""
        # Query the OpenAI API for available models
        models = self.client.models.list()

        # Filter for GPT models and convert to list of dicts
        model_list = []
        for model in models.data:
            # Only include GPT models (filter out embedding models, etc.)
            if 'gpt' in model.id.lower():
                model_list.append({
                    'id': model.id,
                    'name': model.id,
                    'created': model.created if hasattr(model, 'created') else None
                })

        # Sort by creation date (newest first)
        model_list.sort(key=lambda x: x['created'] if x['created'] else 0, reverse=True)

        return model_list


def validate_api_key_available(
    provider: str,
    api_key: Optional[str] = None
) -> tuple[bool, Optional[str]]:
    """
    Check if API key is available for the specified provider.

    Args:
        provider: Name of the provider ('anthropic' or 'openai')
        api_key: API key passed as parameter (optional)

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if API key is available, False otherwise
        - error_message: None if valid, friendly error message if invalid
    """
    provider = provider.lower()

    # Check if key is provided or in environment
    if provider == "anthropic":
        env_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key and not env_key:
            error_msg = """❌ Anthropic API key not found!

To use Anthropic (Claude), you need to set your API key:

Option 1 - Environment variable:
  export ANTHROPIC_API_KEY='your-api-key-here'

Option 2 - .env file:
  Create a .env file in your project directory:
  ANTHROPIC_API_KEY=your-api-key-here

Option 3 - Command line:
  pdf-to-md-llm convert document.pdf --api-key your-api-key-here

Get your API key at: https://console.anthropic.com/settings/keys"""
            return False, error_msg

    elif provider == "openai":
        env_key = os.environ.get("OPENAI_API_KEY")
        if not api_key and not env_key:
            error_msg = """❌ OpenAI API key not found!

To use OpenAI (GPT), you need to set your API key:

Option 1 - Environment variable:
  export OPENAI_API_KEY='your-api-key-here'

Option 2 - .env file:
  Create a .env file in your project directory:
  OPENAI_API_KEY=your-api-key-here

Option 3 - Command line:
  pdf-to-md-llm convert document.pdf --api-key your-api-key-here

Get your API key at: https://platform.openai.com/api-keys"""
            return False, error_msg

    else:
        return False, f"Unknown provider: {provider}. Supported providers: anthropic, openai"

    return True, None


def get_provider(
    provider_name: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> AIProvider:
    """
    Factory function to get an AI provider by name.

    Args:
        provider_name: Name of the provider ('anthropic' or 'openai')
        api_key: API key for the provider
        model: Model to use (optional, uses provider defaults if not specified)

    Returns:
        AIProvider instance

    Raises:
        ValueError: If provider name is not recognized
    """
    provider_name = provider_name.lower()

    if provider_name == "anthropic":
        kwargs = {"api_key": api_key}
        if model:
            kwargs["model"] = model
        return AnthropicProvider(**kwargs)
    elif provider_name == "openai":
        kwargs = {"api_key": api_key}
        if model:
            kwargs["model"] = model
        return OpenAIProvider(**kwargs)
    else:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            "Supported providers: anthropic, openai"
        )


def list_models_for_providers(
    provider_filter: Optional[str] = None
) -> Dict[str, Dict[str, Any]]:
    """
    List available models from all providers (or a specific provider).

    Only queries providers for which API keys are available.

    Args:
        provider_filter: Optional provider name to filter by ('anthropic' or 'openai')

    Returns:
        Dict mapping provider names to their data:
        {
            'anthropic': {
                'available': True/False,
                'default_model': 'model-id',
                'models': [{'id': '...', 'name': '...', ...}]
            },
            'openai': {...}
        }
    """
    result = {}

    # Define providers to check
    providers_to_check = {
        'anthropic': AnthropicProvider,
        'openai': OpenAIProvider
    }

    # Filter if requested
    if provider_filter:
        provider_filter = provider_filter.lower()
        if provider_filter not in providers_to_check:
            raise ValueError(
                f"Unknown provider: {provider_filter}. "
                "Supported providers: anthropic, openai"
            )
        providers_to_check = {provider_filter: providers_to_check[provider_filter]}

    # Check each provider
    for provider_name, provider_class in providers_to_check.items():
        # Check if API key is available
        is_valid, _ = validate_api_key_available(provider_name)

        if is_valid:
            try:
                # Initialize provider and get models
                provider = provider_class()

                # Get default model from provider instance
                default_model = provider.model

                # Get available models
                models = provider.list_available_models()

                result[provider_name] = {
                    'available': True,
                    'default_model': default_model,
                    'models': models
                }
            except Exception as e:
                # Provider initialization failed
                result[provider_name] = {
                    'available': False,
                    'error': str(e),
                    'models': []
                }
        else:
            # No API key available
            result[provider_name] = {
                'available': False,
                'error': 'API key not found',
                'models': []
            }

    return result
