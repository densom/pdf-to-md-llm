#!/usr/bin/env python3
"""
PDF to Markdown Converter using Claude API
Converts PDF documents to clean markdown with LLM assistance
"""

import os
import sys
import anthropic
import pymupdf  # PyMuPDF (pip install pymupdf)
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "your-api-key-here")
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4000
PAGES_PER_CHUNK = 5  # Adjust based on content density


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


def convert_chunk_to_markdown(client: anthropic.Anthropic, chunk: str) -> str:
    """
    Send a chunk of text to Claude API for markdown conversion.
    
    Args:
        client: Anthropic API client
        chunk: Text chunk to convert
        
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
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    
    return message.content[0].text


def convert_pdf_to_markdown(
    pdf_path: str,
    output_path: Optional[str] = None,
    pages_per_chunk: int = PAGES_PER_CHUNK
) -> str:
    """
    Convert a PDF file to markdown using Claude API.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Optional path for output file (defaults to same name with .md)
        pages_per_chunk: Number of pages to process per API call
        
    Returns:
        Complete markdown document
    """
    print(f"Processing: {pdf_path}")
    
    # Initialize API client
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Extract text from PDF
    print("Extracting text from PDF...")
    pages = extract_text_from_pdf(pdf_path)
    print(f"  Found {len(pages)} pages")
    
    # Chunk the pages
    chunks = chunk_pages(pages, pages_per_chunk)
    print(f"  Created {len(chunks)} chunks")
    
    # Convert each chunk
    markdown_chunks = []
    for i, chunk in enumerate(chunks, 1):
        print(f"  Converting chunk {i}/{len(chunks)}...")
        try:
            markdown = convert_chunk_to_markdown(client, chunk)
            markdown_chunks.append(markdown)
        except Exception as e:
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
    
    # Save to file
    if output_path is None:
        output_path = str(Path(pdf_path).with_suffix('.md'))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_markdown)
    
    print(f"✓ Saved to: {output_path}")
    return full_markdown


def batch_convert(input_folder: str, output_folder: Optional[str] = None):
    """
    Convert all PDF files in a folder and its subdirectories to markdown.

    Args:
        input_folder: Folder containing PDF files
        output_folder: Optional output folder (defaults to same as input)
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder) if output_folder else input_path

    # Create output folder if needed
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all PDFs recursively
    pdf_files = list(input_path.rglob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {input_folder}")
        return

    print(f"Found {len(pdf_files)} PDF files to convert\n")

    # Convert each file
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}]")

        # Preserve subdirectory structure in output
        relative_path = pdf_file.relative_to(input_path)
        output_file = output_path / relative_path.with_suffix('.md')

        # Create subdirectory if needed
        output_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            convert_pdf_to_markdown(str(pdf_file), str(output_file))
        except Exception as e:
            print(f"✗ Failed: {e}")

    print(f"\n✓ Batch conversion complete!")
    print(f"  Output directory: {output_path}")


def main():
    """Main entry point for command-line usage."""
    if len(sys.argv) < 2:
        print("""
PDF to Markdown Converter (LLM-Assisted)

Usage:
    python pdf_to_markdown.py <pdf_file>                    # Convert single file
    python pdf_to_markdown.py <pdf_file> <output_file>      # Convert with custom output
    python pdf_to_markdown.py --batch <input_folder>        # Convert all PDFs in folder
    python pdf_to_markdown.py --batch <input_folder> <output_folder>  # Batch with output folder

Environment Variables:
    ANTHROPIC_API_KEY - Your Anthropic API key (required)

Examples:
    python pdf_to_markdown.py document.pdf
    python pdf_to_markdown.py document.pdf output.md
    python pdf_to_markdown.py --batch ./pdfs
    python pdf_to_markdown.py --batch ./pdfs ./markdown_output
        """)
        sys.exit(1)
    
    # Check for API key
    if ANTHROPIC_API_KEY == "your-api-key-here":
        print("Error: Please set ANTHROPIC_API_KEY environment variable")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Batch mode
    if sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("Error: --batch requires input folder")
            sys.exit(1)
        
        input_folder = sys.argv[2]
        output_folder = sys.argv[3] if len(sys.argv) > 3 else None
        batch_convert(input_folder, output_folder)
    
    # Single file mode
    else:
        pdf_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        
        if not os.path.exists(pdf_path):
            print(f"Error: File not found: {pdf_path}")
            sys.exit(1)
        
        convert_pdf_to_markdown(pdf_path, output_path)


if __name__ == "__main__":
    main()