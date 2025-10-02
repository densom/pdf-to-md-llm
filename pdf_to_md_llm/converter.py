"""
PDF to Markdown conversion functions
"""

import os
import anthropic
import pymupdf  # PyMuPDF
from pathlib import Path
from typing import List, Optional

# Default configuration
DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_MAX_TOKENS = 4000
DEFAULT_PAGES_PER_CHUNK = 5


def extract_text_from_pdf(pdf_path: str) -> List[str]:
    """
    Extract text from PDF, returning a list of page texts.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        List of strings, one per page
    """
    doc = pymupdf.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        pages.append(text)

    doc.close()
    return pages


def chunk_pages(pages: List[str], pages_per_chunk: int) -> List[str]:
    """
    Combine pages into chunks for processing.

    Args:
        pages: List of page texts
        pages_per_chunk: Number of pages to combine per chunk

    Returns:
        List of combined page chunks
    """
    chunks = []
    for i in range(0, len(pages), pages_per_chunk):
        chunk = "\n\n".join(pages[i:i + pages_per_chunk])
        chunks.append(chunk)
    return chunks


def convert_chunk_to_markdown(
    client: anthropic.Anthropic,
    chunk: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS
) -> str:
    """
    Send a chunk of text to Claude API for markdown conversion.

    Args:
        client: Anthropic API client
        chunk: Text chunk to convert
        model: Claude model to use
        max_tokens: Maximum tokens for response

    Returns:
        Converted markdown text
    """
    prompt = f"""Convert this text from a PDF document to clean, well-structured markdown.

Requirements:
- Use proper heading hierarchy (# for main titles, ## for sections, ### for subsections)
- Convert any tables to proper markdown table format with aligned columns
- Clean up formatting artifacts from PDF extraction (broken lines, weird spacing)
- Use consistent bullet points and numbered lists
- Preserve all information - don't summarize or omit content
- Remove page numbers, headers, and footers if they appear
- Make the document scannable with clear structure

Output ONLY the markdown - no explanations or commentary.

Text to convert:

{chunk}"""

    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    return message.content[0].text


def convert_pdf_to_markdown(
    pdf_path: str,
    output_path: Optional[str] = None,
    pages_per_chunk: int = DEFAULT_PAGES_PER_CHUNK,
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    verbose: bool = True
) -> str:
    """
    Convert a PDF file to markdown using Claude API.

    Args:
        pdf_path: Path to the PDF file
        output_path: Optional path for output file (defaults to same name with .md)
        pages_per_chunk: Number of pages to process per API call
        api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        model: Claude model to use
        max_tokens: Maximum tokens per API call
        verbose: Print progress messages

    Returns:
        Complete markdown document

    Raises:
        ValueError: If API key is not provided and not in environment
    """
    if verbose:
        print(f"Processing: {pdf_path}")

    # Get API key from parameter or environment
    if api_key is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key or api_key == "your-api-key-here":
        raise ValueError(
            "Anthropic API key required. Pass api_key parameter or set ANTHROPIC_API_KEY environment variable."
        )

    # Initialize API client
    client = anthropic.Anthropic(api_key=api_key)

    # Extract text from PDF
    if verbose:
        print("Extracting text from PDF...")
    pages = extract_text_from_pdf(pdf_path)
    if verbose:
        print(f"  Found {len(pages)} pages")

    # Chunk the pages
    chunks = chunk_pages(pages, pages_per_chunk)
    if verbose:
        print(f"  Created {len(chunks)} chunks")

    # Convert each chunk
    markdown_chunks = []
    for i, chunk in enumerate(chunks, 1):
        if verbose:
            print(f"  Converting chunk {i}/{len(chunks)}...")
        try:
            markdown = convert_chunk_to_markdown(client, chunk, model, max_tokens)
            markdown_chunks.append(markdown)
        except Exception as e:
            if verbose:
                print(f"  Error converting chunk {i}: {e}")
            markdown_chunks.append(f"\n\n<!-- Error converting chunk {i}: {e} -->\n\n")

    # Combine all chunks
    full_markdown = "\n\n---\n\n".join(markdown_chunks)

    # Add document metadata header
    filename = Path(pdf_path).stem
    header = f"""# {filename}

*Converted from PDF using LLM-assisted conversion*

---

"""
    full_markdown = header + full_markdown

    # Save to file if output path provided
    if output_path is None:
        output_path = str(Path(pdf_path).with_suffix('.md'))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_markdown)

    if verbose:
        print(f"✓ Saved to: {output_path}")

    return full_markdown


def batch_convert(
    input_folder: str,
    output_folder: Optional[str] = None,
    pages_per_chunk: int = DEFAULT_PAGES_PER_CHUNK,
    api_key: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    verbose: bool = True
) -> None:
    """
    Convert all PDF files in a folder and its subdirectories to markdown.

    Args:
        input_folder: Folder containing PDF files
        output_folder: Optional output folder (defaults to same as input)
        pages_per_chunk: Number of pages to process per API call
        api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        model: Claude model to use
        max_tokens: Maximum tokens per API call
        verbose: Print progress messages

    Raises:
        ValueError: If API key is not provided and not in environment
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder) if output_folder else input_path

    # Create output folder if needed
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all PDFs recursively
    pdf_files = list(input_path.rglob("*.pdf"))

    if not pdf_files:
        if verbose:
            print(f"No PDF files found in {input_folder}")
        return

    if verbose:
        print(f"Found {len(pdf_files)} PDF files to convert\n")

    # Convert each file
    for i, pdf_file in enumerate(pdf_files, 1):
        if verbose:
            print(f"\n[{i}/{len(pdf_files)}]")

        # Preserve subdirectory structure in output
        relative_path = pdf_file.relative_to(input_path)
        output_file = output_path / relative_path.with_suffix('.md')

        # Create subdirectory if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            convert_pdf_to_markdown(
                str(pdf_file),
                str(output_file),
                pages_per_chunk=pages_per_chunk,
                api_key=api_key,
                model=model,
                max_tokens=max_tokens,
                verbose=verbose
            )
        except Exception as e:
            if verbose:
                print(f"✗ Failed: {e}")

    if verbose:
        print(f"\n✓ Batch conversion complete!")
        print(f"  Output directory: {output_path}")
