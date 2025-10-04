"""
PDF to Markdown Converter using AI providers

A tool to convert PDF documents to clean, well-structured Markdown
using LLM-assisted processing with support for multiple AI providers.
"""

from .converter import (
    convert_pdf_to_markdown,
    batch_convert,
    extract_text_from_pdf,
    chunk_pages,
    DEFAULT_PROVIDER,
    DEFAULT_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_PAGES_PER_CHUNK,
)
from .providers import (
    AIProvider,
    AnthropicProvider,
    OpenAIProvider,
    get_provider,
)

__version__ = "0.2.0"
__all__ = [
    "convert_pdf_to_markdown",
    "batch_convert",
    "extract_text_from_pdf",
    "chunk_pages",
    "DEFAULT_PROVIDER",
    "DEFAULT_MODEL",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_PAGES_PER_CHUNK",
    "AIProvider",
    "AnthropicProvider",
    "OpenAIProvider",
    "get_provider",
]
