"""
PDF to Markdown conversion functions
"""

import pymupdf  # PyMuPDF
from pathlib import Path
from typing import List, Optional, Dict, Any
from .providers import AIProvider, get_provider, validate_api_key_available, TruncationError
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Default configuration
DEFAULT_PROVIDER = "anthropic"
DEFAULT_MAX_TOKENS = 4000
DEFAULT_PAGES_PER_CHUNK = 5
DEFAULT_VISION_DPI = 150
DEFAULT_VISION_PAGES_PER_CHUNK = 8
DEFAULT_THREADS = 1


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


def extract_pages_with_vision(
    pdf_path: str,
    dpi: int = DEFAULT_VISION_DPI
) -> List[Dict[str, Any]]:
    """
    Extract both text and images from PDF pages for vision-based processing.

    Args:
        pdf_path: Path to the PDF file
        dpi: DPI for rendering page images (default: 150)

    Returns:
        List of dicts with keys:
            - page_num: Page number (0-indexed)
            - text: Extracted text
            - image_base64: Base64-encoded PNG image of the page
            - has_images: Whether page contains embedded images
            - has_tables: Whether page likely contains tables
    """
    doc = pymupdf.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Extract text
        text = page.get_text()

        # Render page as image
        # Calculate zoom factor for desired DPI (default PDF is 72 DPI)
        zoom = dpi / 72.0
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)

        # Convert to PNG bytes (using PyMuPDF's native method)
        img_bytes = pix.tobytes(output="png")

        # Encode to base64
        image_base64 = base64.b64encode(img_bytes).decode('utf-8')

        # Detect if page has images
        has_images = len(page.get_images()) > 0

        # Heuristic for table detection: check for multiple tab characters or grid-like text
        has_tables = text.count('\t') > 5 or text.count('|') > 5

        pages.append({
            'page_num': page_num,
            'text': text,
            'image_base64': image_base64,
            'has_images': has_images,
            'has_tables': has_tables
        })

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


def chunk_vision_pages(
    pages: List[Dict[str, Any]],
    pages_per_chunk: int
) -> List[List[Dict[str, Any]]]:
    """
    Group vision-extracted pages into chunks for processing.

    Args:
        pages: List of page dicts from extract_pages_with_vision
        pages_per_chunk: Number of pages to combine per chunk

    Returns:
        List of page chunks (each chunk is a list of page dicts)
    """
    chunks = []
    for i in range(0, len(pages), pages_per_chunk):
        chunk = pages[i:i + pages_per_chunk]
        chunks.append(chunk)
    return chunks


def convert_chunk_to_markdown(
    provider: AIProvider,
    chunk: str,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    system_prompt: Optional[str] = None
) -> str:
    """
    Send a chunk of text to AI provider for markdown conversion.

    Args:
        provider: AI provider instance
        chunk: Text chunk to convert
        max_tokens: Maximum tokens for response
        system_prompt: Optional custom system prompt to append to conversion instructions

    Returns:
        Converted markdown text
    """
    return provider.convert_to_markdown(chunk, max_tokens, system_prompt)


def convert_vision_chunk_to_markdown(
    provider: AIProvider,
    chunk: List[Dict[str, Any]],
    max_tokens: int = DEFAULT_MAX_TOKENS,
    system_prompt: Optional[str] = None
) -> str:
    """
    Send a chunk of pages with vision data to AI provider for markdown conversion.

    Args:
        provider: AI provider instance
        chunk: List of page dicts with text and image data
        max_tokens: Maximum tokens for response
        system_prompt: Optional custom system prompt to append to conversion instructions

    Returns:
        Converted markdown text
    """
    return provider.convert_to_markdown_vision(chunk, max_tokens, system_prompt)


def convert_pdf_to_markdown(
    pdf_path: str,
    output_path: Optional[str] = None,
    pages_per_chunk: int = DEFAULT_PAGES_PER_CHUNK,
    provider: str = DEFAULT_PROVIDER,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    verbose: bool = True,
    use_vision: bool = False,
    vision_dpi: int = DEFAULT_VISION_DPI,
    system_prompt: Optional[str] = None
) -> str:
    """
    Convert a PDF file to markdown using an AI provider.

    Args:
        pdf_path: Path to the PDF file
        output_path: Optional path for output file (defaults to same name with .md)
        pages_per_chunk: Number of pages to process per API call
        provider: AI provider to use ('anthropic' or 'openai')
        api_key: API key for the provider (defaults to provider-specific env var)
        model: Model to use (optional, uses provider defaults if not specified)
        max_tokens: Maximum tokens per API call
        verbose: Print progress messages
        use_vision: Use vision-based processing (images + text)
        vision_dpi: DPI for rendering page images when using vision mode
        system_prompt: Optional custom system prompt to append to conversion instructions

    Returns:
        Complete markdown document

    Raises:
        ValueError: If API key is not provided and not in environment
    """
    # Validate API key is available before initializing provider
    is_valid, error_message = validate_api_key_available(provider, api_key)
    if not is_valid:
        raise ValueError(error_message)

    # Initialize AI provider
    ai_provider = get_provider(provider, api_key=api_key, model=model)

    if verbose:
        print(f"Processing: {pdf_path}")
        print(f"Using provider: {provider}")
        print(f"Using model: {ai_provider.model}")
        print(f"Vision mode: {'enabled' if use_vision else 'disabled'}")

    # Double-check provider configuration (backup validation)
    if not ai_provider.validate_config():
        provider_upper = provider.upper()
        raise ValueError(
            f"{provider_upper} API key is invalid or not properly configured."
        )

    # Check if vision mode is supported
    if use_vision and not hasattr(ai_provider, 'convert_to_markdown_vision'):
        raise ValueError(f"Vision mode is not supported by {provider} provider")

    # Determine output path early for cleanup on failure
    if output_path is None:
        output_path = str(Path(pdf_path).with_suffix('.md'))

    try:
        # Extract from PDF
        if use_vision:
            if verbose:
                print(f"Extracting text and images from PDF (DPI: {vision_dpi})...")
            vision_pages = extract_pages_with_vision(pdf_path, dpi=vision_dpi)
            if verbose:
                print(f"  Found {len(vision_pages)} pages")
                images_count = sum(1 for p in vision_pages if p['has_images'])
                tables_count = sum(1 for p in vision_pages if p['has_tables'])
                print(f"  Detected {images_count} pages with images, {tables_count} pages with tables")

            # Use vision-specific chunk size if pages_per_chunk wasn't explicitly set
            # Otherwise respect the user's choice
            effective_pages_per_chunk = pages_per_chunk if pages_per_chunk != DEFAULT_PAGES_PER_CHUNK else DEFAULT_VISION_PAGES_PER_CHUNK
            chunks = chunk_vision_pages(vision_pages, effective_pages_per_chunk)
            if verbose:
                print(f"  Created {len(chunks)} chunks ({effective_pages_per_chunk} pages per chunk)")

            # Convert each chunk using vision
            markdown_chunks = []
            for i, chunk in enumerate(chunks, 1):
                if verbose:
                    print(f"  Converting chunk {i}/{len(chunks)} (vision mode)...")
                markdown = convert_vision_chunk_to_markdown(ai_provider, chunk, max_tokens, system_prompt)
                markdown_chunks.append(markdown)
        else:
            # Original text-only mode
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
                markdown = convert_chunk_to_markdown(ai_provider, chunk, max_tokens, system_prompt)
                markdown_chunks.append(markdown)

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
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_markdown)

        if verbose:
            print(f"Saved to: {output_path}")

        return full_markdown

    except Exception:
        # Clean up partial output file if it exists
        if Path(output_path).exists():
            Path(output_path).unlink()
        # Re-raise the exception to fail the conversion
        raise


def batch_convert(
    input_folder: str,
    output_folder: Optional[str] = None,
    pages_per_chunk: int = DEFAULT_PAGES_PER_CHUNK,
    provider: str = DEFAULT_PROVIDER,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    verbose: bool = True,
    use_vision: bool = False,
    vision_dpi: int = DEFAULT_VISION_DPI,
    threads: int = DEFAULT_THREADS,
    skip_existing: bool = False,
    system_prompt: Optional[str] = None
) -> None:
    """
    Convert all PDF files in a folder and its subdirectories to markdown.

    Args:
        input_folder: Folder containing PDF files
        output_folder: Optional output folder (defaults to same as input)
        pages_per_chunk: Number of pages to process per API call
        provider: AI provider to use ('anthropic' or 'openai')
        api_key: API key for the provider (defaults to provider-specific env var)
        model: Model to use (optional, uses provider defaults if not specified)
        max_tokens: Maximum tokens per API call
        verbose: Print progress messages
        use_vision: Use vision-based processing (images + text)
        vision_dpi: DPI for rendering page images when using vision mode
        threads: Number of threads for parallel processing (default: 1)
        skip_existing: Skip files that already have corresponding .md files in output directory
        system_prompt: Optional custom system prompt to append to conversion instructions

    Raises:
        ValueError: If API key is not provided and not in environment
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder) if output_folder else input_path

    # Validate API key and initialize provider to get model information
    is_valid, error_message = validate_api_key_available(provider, api_key)
    if not is_valid:
        raise ValueError(error_message)

    # Initialize AI provider to display configuration
    ai_provider = get_provider(provider, api_key=api_key, model=model)

    # Create output folder if needed
    output_path.mkdir(parents=True, exist_ok=True)

    # Find all PDFs recursively
    pdf_files = list(input_path.rglob("*.pdf"))

    if not pdf_files:
        if verbose:
            print(f"No PDF files found in {input_folder}")
        return

    # Filter out files that already exist if skip_existing is True
    skipped_files = []
    if skip_existing:
        files_to_process = []
        for pdf_file in pdf_files:
            relative_path = pdf_file.relative_to(input_path)
            output_file = output_path / relative_path.with_suffix('.md')

            if output_file.exists():
                skipped_files.append(pdf_file)
                if verbose:
                    print(f"Skipping {pdf_file.name} (already exists)")
            else:
                files_to_process.append(pdf_file)

        pdf_files = files_to_process

    if not pdf_files:
        if verbose:
            if skipped_files:
                print(f"\nAll {len(skipped_files)} PDF files already converted (use without --skip-existing to reconvert)")
            else:
                print(f"No PDF files to process")
        return

    if verbose:
        mode = f"multithreaded ({threads} threads)" if threads > 1 else "single-threaded"
        print(f"\nBatch Processing Configuration:")
        print(f"  Provider: {provider}")
        print(f"  Model: {ai_provider.model}")
        print(f"  Vision mode: {'enabled' if use_vision else 'disabled'}")
        print(f"  Mode: {mode}")
        if skip_existing and skipped_files:
            print(f"  Skipped: {len(skipped_files)} files (already exist)")
        print(f"  Files to process: {len(pdf_files)} PDF files")
        print()

    # Track failed conversions
    failed_files = []

    # Single-threaded execution (original behavior)
    if threads == 1:
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
                    provider=provider,
                    api_key=api_key,
                    model=model,
                    max_tokens=max_tokens,
                    verbose=verbose,
                    use_vision=use_vision,
                    vision_dpi=vision_dpi,
                    system_prompt=system_prompt
                )
            except TruncationError as e:
                # Track truncation failure
                failed_files.append({
                    'file': str(pdf_file),
                    'error': str(e),
                    'error_type': 'truncation'
                })
                if verbose:
                    print(f"Failed (truncation): {e}")
            except Exception as e:
                # Track other failures
                failed_files.append({
                    'file': str(pdf_file),
                    'error': str(e),
                    'error_type': 'other'
                })
                if verbose:
                    print(f"Failed: {e}")
    else:
        # Multithreaded execution
        completed_count = 0
        progress_lock = threading.Lock()

        def convert_single_file(pdf_file: Path) -> tuple[bool, str, Optional[str], str]:
            """Convert a single PDF file and return success status, filename, error message, and error type."""
            nonlocal completed_count

            # Preserve subdirectory structure in output
            relative_path = pdf_file.relative_to(input_path)
            output_file = output_path / relative_path.with_suffix('.md')

            # Create subdirectory if needed
            output_file.parent.mkdir(parents=True, exist_ok=True)

            try:
                # For multithreaded mode, reduce verbosity of individual file processing
                convert_pdf_to_markdown(
                    str(pdf_file),
                    str(output_file),
                    pages_per_chunk=pages_per_chunk,
                    provider=provider,
                    api_key=api_key,
                    model=model,
                    max_tokens=max_tokens,
                    verbose=False,  # Suppress per-file output in multithreaded mode
                    use_vision=use_vision,
                    vision_dpi=vision_dpi,
                    system_prompt=system_prompt
                )

                with progress_lock:
                    completed_count += 1
                    if verbose:
                        print(f"[OK] [{completed_count}/{len(pdf_files)}] {pdf_file.name}")

                return True, str(pdf_file), None, ""
            except TruncationError as e:
                with progress_lock:
                    completed_count += 1
                    if verbose:
                        print(f"[FAILED] [{completed_count}/{len(pdf_files)}] {pdf_file.name}: (truncation) {e}")

                return False, str(pdf_file), str(e), "truncation"
            except Exception as e:
                with progress_lock:
                    completed_count += 1
                    if verbose:
                        print(f"[FAILED] [{completed_count}/{len(pdf_files)}] {pdf_file.name}: {e}")

                return False, str(pdf_file), str(e), "other"

        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # Submit all tasks
            future_to_pdf = {
                executor.submit(convert_single_file, pdf_file): pdf_file
                for pdf_file in pdf_files
            }

            # Wait for all tasks to complete
            for future in as_completed(future_to_pdf):
                try:
                    success, filename, error, error_type = future.result()
                    if not success:
                        failed_files.append({
                            'file': filename,
                            'error': error,
                            'error_type': error_type
                        })
                except Exception as e:
                    pdf_file = future_to_pdf[future]
                    failed_files.append({
                        'file': str(pdf_file),
                        'error': f"Unexpected error: {e}",
                        'error_type': 'other'
                    })
                    if verbose:
                        print(f"Unexpected error processing {pdf_file.name}: {e}")

    if verbose:
        print(f"\nBatch conversion complete!")
        print(f"  Output directory: {output_path}")

        # Report summary statistics
        successful_count = len(pdf_files) - len(failed_files)
        print(f"\nSummary:")
        print(f"  Total files: {len(pdf_files)}")
        print(f"  Successful: {successful_count}")
        print(f"  Failed: {len(failed_files)}")

        # List failed files if any
        if failed_files:
            # Group failures by error type
            truncation_failures = [f for f in failed_files if f.get('error_type') == 'truncation']
            other_failures = [f for f in failed_files if f.get('error_type') != 'truncation']

            if truncation_failures:
                print(f"\nTruncation errors ({len(truncation_failures)} files):")
                print(f"  These files exceeded the max_tokens limit during conversion.")
                print(f"  Try reducing --pages-per-chunk (e.g., --pages-per-chunk 3)")
                print(f"  Or reduce --vision-pages-per-chunk if using vision mode")
                for failure in truncation_failures:
                    filename = Path(failure['file']).name
                    print(f"  - {filename}")

            if other_failures:
                print(f"\nOther errors ({len(other_failures)} files):")
                for failure in other_failures:
                    filename = Path(failure['file']).name
                    error = failure['error']
                    print(f"  - {filename}")
                    print(f"    Error: {error}")
