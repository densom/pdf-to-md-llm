"""
PDF to Markdown Converter using Claude API

A tool to convert PDF documents to clean, well-structured Markdown
using LLM-assisted processing.
"""

from .converter import (
    convert_pdf_to_markdown,
    batch_convert,
    extract_text_from_pdf,
    chunk_pages,
    DEFAULT_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_PAGES_PER_CHUNK,
)

__version__ = "0.1.0"
__all__ = [
    "convert_pdf_to_markdown",
    "batch_convert",
    "extract_text_from_pdf",
    "chunk_pages",
    "DEFAULT_MODEL",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_PAGES_PER_CHUNK",
]
