"""
AI provider abstraction for PDF to Markdown conversion
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import os


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    def convert_to_markdown(self, text: str, max_tokens: int) -> str:
        """
        Convert text to markdown using the AI provider.

        Args:
            text: Text to convert
            max_tokens: Maximum tokens for response

        Returns:
            Converted markdown text
        """
        pass

    @abstractmethod
    def convert_to_markdown_vision(
        self,
        pages: List[Dict[str, Any]],
        max_tokens: int
    ) -> str:
        """
        Convert pages with vision data to markdown using the AI provider.

        Args:
            pages: List of page dicts with 'text' and 'image_base64' keys
            max_tokens: Maximum tokens for response

        Returns:
            Converted markdown text
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support vision mode"
        )

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate that the provider is properly configured.

        Returns:
            True if valid, False otherwise
        """
        pass


class AnthropicProvider(AIProvider):
    """Anthropic (Claude) AI provider"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514"
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

    def convert_to_markdown(self, text: str, max_tokens: int) -> str:
        """Convert text to markdown using Claude API"""
        prompt = f"""Convert this text from a PDF document to clean, well-structured markdown.

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

        message = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return message.content[0].text

    def convert_to_markdown_vision(
        self,
        pages: List[Dict[str, Any]],
        max_tokens: int
    ) -> str:
        """Convert pages with vision data to markdown using Claude API"""
        # Build multimodal content blocks
        content_blocks = []

        # Add instruction text first
        instruction = """Convert these PDF pages to clean, well-structured markdown.

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
        content_blocks.append({
            "type": "text",
            "text": instruction
        })

        # Add each page's image and text
        for page in pages:
            page_num = page['page_num'] + 1  # Convert to 1-indexed for display

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
            text_block = f"\n**Extracted text from page {page_num}:**\n\n{page['text']}\n\n---\n"
            content_blocks.append({
                "type": "text",
                "text": text_block
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

        return message.content[0].text

    def validate_config(self) -> bool:
        """Validate Anthropic API key"""
        return bool(self.api_key and self.api_key != "your-api-key-here")


class OpenAIProvider(AIProvider):
    """OpenAI (GPT) AI provider"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o"
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

    def convert_to_markdown(self, text: str, max_tokens: int) -> str:
        """Convert text to markdown using OpenAI API"""
        prompt = f"""Convert this text from a PDF document to clean, well-structured markdown.

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

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        return response.choices[0].message.content

    def convert_to_markdown_vision(
        self,
        pages: List[Dict[str, Any]],
        max_tokens: int
    ) -> str:
        """Convert pages with vision data to markdown using OpenAI API"""
        # Build multimodal content blocks
        content_parts = []

        # Add instruction text first
        instruction = """Convert these PDF pages to clean, well-structured markdown.

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
        content_parts.append({
            "type": "text",
            "text": instruction
        })

        # Add each page's image and text
        for page in pages:
            page_num = page['page_num'] + 1  # Convert to 1-indexed for display

            # Add page image
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{page['image_base64']}"
                }
            })

            # Add extracted text with context
            text_block = f"\n**Extracted text from page {page_num}:**\n\n{page['text']}\n\n---\n"
            content_parts.append({
                "type": "text",
                "text": text_block
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

        return response.choices[0].message.content

    def validate_config(self) -> bool:
        """Validate OpenAI API key"""
        return bool(self.api_key and self.api_key != "your-api-key-here")


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
