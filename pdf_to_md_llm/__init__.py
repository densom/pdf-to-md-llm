"""
PDF to Markdown Converter using AI providers

A tool to convert PDF documents to clean, well-structured Markdown
using LLM-assisted processing with support for multiple AI providers.
"""

from .converter import (
    convert_pdf_to_markdown,
    batch_convert,
    extract_text_from_pdf,
    extract_pages_with_vision,
    chunk_pages,
    chunk_vision_pages,
    DEFAULT_PROVIDER,
    DEFAULT_MAX_TOKENS,
    DEFAULT_PAGES_PER_CHUNK,
    DEFAULT_VISION_DPI,
    DEFAULT_VISION_PAGES_PER_CHUNK,
    DEFAULT_THREADS,
)
from .providers import (
    AIProvider,
    AnthropicProvider,
    OpenAIProvider,
    get_provider,
    CONVERSION_PROMPT,
    VISION_CONVERSION_PROMPT,
)

__version__ = "0.2.0"
__all__ = [
    "convert_pdf_to_markdown",
    "batch_convert",
    "extract_text_from_pdf",
    "extract_pages_with_vision",
    "chunk_pages",
    "chunk_vision_pages",
    "DEFAULT_PROVIDER",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_PAGES_PER_CHUNK",
    "DEFAULT_VISION_DPI",
    "DEFAULT_VISION_PAGES_PER_CHUNK",
    "DEFAULT_THREADS",
    "CONVERSION_PROMPT",
    "VISION_CONVERSION_PROMPT",
    "AIProvider",
    "AnthropicProvider",
    "OpenAIProvider",
    "get_provider",
]
