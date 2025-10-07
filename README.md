# PDF to Markdown Converter

Library and CLI to convert PDF documents to clean, well-structured Markdown using LLM-assisted processing, leveraging Antrhopic and OpenAI models for intelligent extraction of text, tables, and complex layouts.

## Features

- **Vision Mode**: Enhanced extraction using multimodal AI for complex layouts, tables, charts, and diagrams
- **Multi-Provider Support**: Use Anthropic (Claude) or OpenAI (GPT) models
- **Smart Conversion**: Intelligently converts PDF content to clean markdown with proper formatting
- **Large File Support**: Automatically chunks large PDFs for optimal processing
- **Batch Processing**: Convert entire folders of PDFs with preserved directory structure
- **Table Preservation**: Accurately converts tables to markdown format with vision-enhanced detection
- **Structure Detection**: Automatically generates appropriate heading hierarchy
- **Dual Interface**: Use as both a CLI tool and a Python library

## Quick Start

```bash
# 1. Install with uv (recommended - faster)
uv tool install pdf-to-md-llm

# 2. Set your API key
export ANTHROPIC_API_KEY='your-api-key-here'

# 3. Convert a PDF
pdf-to-md-llm convert document.pdf --vision
```

## Installation

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer:

```bash
# Install the package as a tool
uv tool install pdf-to-md-llm

# Or run directly without installing
uvx pdf-to-md-llm convert document.pdf
```

### Using pip (Alternative)

```bash
pip install pdf-to-md-llm
```

## Configuration

Set your API key for at least one provider:

```bash
# For Anthropic (Claude) - recommended
export ANTHROPIC_API_KEY='your-anthropic-api-key-here'

# For OpenAI (GPT)
export OPENAI_API_KEY='your-openai-api-key-here'
```

Or create a `.env.local` file:

```bash
ANTHROPIC_API_KEY=your-anthropic-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

### Default Models (Optimized for Cost/Quality)

The tool uses cost-effective models by default:
- **Anthropic**: `claude-3-5-haiku-20241022` ($0.80 input / $4 output per million tokens)
- **OpenAI**: `gpt-4o-mini` ($0.15 input / $0.60 output per million tokens)

These defaults provide excellent quality for most PDF conversion tasks at significantly lower cost. For complex documents requiring maximum accuracy, you can override with premium models:

```bash
# Use more powerful Anthropic model for complex documents
pdf-to-md-llm convert complex-doc.pdf --model claude-sonnet-4-20250514 --vision

# Use OpenAI's flagship model
pdf-to-md-llm convert complex-doc.pdf --provider openai --model gpt-4o --vision
```

To see all available models from your configured providers, see [List Available Models](#list-available-models).

## Usage Examples

### Basic Conversion

```bash
# Simple document conversion
pdf-to-md-llm convert document.pdf

# Specify output filename
pdf-to-md-llm convert document.pdf output.md
```

### Scenario 1: Academic Papers with Tables

For research papers, technical documents, or any PDF with complex tables:

```bash
# Vision mode provides superior table extraction
pdf-to-md-llm convert research-paper.pdf --vision
```

### Scenario 2: Large Documents (500+ pages)

For textbooks, manuals, or large documents, use smaller chunks for better processing:

```bash
# Reduce chunk size for memory efficiency
pdf-to-md-llm convert textbook.pdf --vision --vision-pages-per-chunk 4
```

### Scenario 3: Documents with Charts and Diagrams

For PDFs containing visual elements like charts, graphs, or diagrams:

```bash
# Vision mode analyzes images and describes visual content
pdf-to-md-llm convert annual-report.pdf --vision --vision-dpi 200
```

### Scenario 4: Using OpenAI GPT Models

Switch to OpenAI for different model capabilities:

```bash
# Use GPT-4o for conversion
pdf-to-md-llm convert document.pdf --provider openai --model gpt-4o --vision

# Use GPT-4o-mini for cost savings
pdf-to-md-llm convert document.pdf --provider openai --model gpt-4o-mini
```

### Scenario 5: Batch Processing Multiple Documents

Convert entire folders of PDFs:

```bash
# Convert all PDFs in a folder (single-threaded)
pdf-to-md-llm batch ./research-papers

# With custom output folder and vision mode
pdf-to-md-llm batch ./input-pdfs ./output-markdown --vision

# Skip files that already have .md output (useful for resuming interrupted batches)
pdf-to-md-llm batch ./pdfs --skip-existing --vision

# Batch with OpenAI
pdf-to-md-llm batch ./pdfs --provider openai --vision

# Use multithreading for faster batch conversion (2 threads)
pdf-to-md-llm batch ./pdfs --threads 2 --vision

# Use 4 threads for even faster processing
pdf-to-md-llm batch ./pdfs --threads 4 --vision

# Maximum parallelization (be mindful of API rate limits)
pdf-to-md-llm batch ./large-batch --threads 8

# Combine skip-existing with multithreading for efficient resumption
pdf-to-md-llm batch ./large-batch --skip-existing --threads 4 --vision
```

**Multithreading Benefits:**
- Dramatically reduces total conversion time for large batches
- Efficiently utilizes multi-core processors
- Thread count can be adjusted based on system resources and API rate limits
- Default is single-threaded (1 thread) to avoid rate limit issues

### Scenario 6: Simple Text Documents

For PDFs with simple text layout (no tables or complex formatting), standard mode is faster and more cost-effective:

```bash
# Standard mode (no vision) - faster and cheaper
pdf-to-md-llm convert simple-doc.pdf

# Adjust chunk size for standard mode
pdf-to-md-llm convert simple-doc.pdf --pages-per-chunk 10
```

### Getting Help

```bash
# Check the installed version
pdf-to-md-llm --version

# Show all available options
pdf-to-md-llm --help

# Show help for specific commands
pdf-to-md-llm convert --help
pdf-to-md-llm batch --help
pdf-to-md-llm models --help
```

### List Available Models

Check which AI models are available from your configured providers:

```bash
# List all available models from all configured providers
pdf-to-md-llm models

# List models from a specific provider
pdf-to-md-llm models --provider anthropic
pdf-to-md-llm models --provider openai
```

The `models` command will:
- Show available models from providers that have API keys configured
- Display the default model for each provider
- Only query providers with valid API keys in your environment

## Using as a Python Library

First, add the package to your project:

```bash
# Using uv (recommended)
uv add pdf-to-md-llm

# Or using pip
pip install pdf-to-md-llm
```

Then import and use in your Python code:

```python
from pdf_to_md_llm import convert_pdf_to_markdown, batch_convert

# Convert with vision mode (recommended for complex layouts)
markdown_content = convert_pdf_to_markdown(
    pdf_path="document.pdf",
    output_path="output.md",  # Optional
    provider="anthropic",  # 'anthropic' or 'openai'
    use_vision=True,  # Enable vision mode
    pages_per_chunk=8,  # Pages per chunk (vision default: 8)
    verbose=True  # Show progress
)

# Use OpenAI with custom model
markdown_content = convert_pdf_to_markdown(
    pdf_path="document.pdf",
    provider="openai",
    model="gpt-4o",
    use_vision=True,
    api_key="your-openai-key"  # Optional if env var set
)

# Batch convert all PDFs in a folder
batch_convert(
    input_folder="./pdfs",
    output_folder="./markdown",  # Optional
    provider="anthropic",
    use_vision=True,
    verbose=True
)

# Batch convert with multithreading for faster processing
batch_convert(
    input_folder="./pdfs",
    output_folder="./markdown",
    provider="anthropic",
    use_vision=True,
    threads=4,  # Use 4 threads for parallel processing
    verbose=True
)

# Batch convert with skip_existing to resume interrupted batches
batch_convert(
    input_folder="./pdfs",
    output_folder="./markdown",
    provider="anthropic",
    use_vision=True,
    skip_existing=True,  # Skip files that already have .md output
    threads=4,
    verbose=True
)
```

### Advanced Library Usage

```python
from pdf_to_md_llm import extract_text_from_pdf, extract_pages_with_vision, chunk_pages

# Extract text only (standard mode)
pages = extract_text_from_pdf("document.pdf")
print(f"Found {len(pages)} pages")

# Extract with vision data (text + images)
vision_pages = extract_pages_with_vision("document.pdf", dpi=150)
for page in vision_pages:
    print(f"Page {page['page_num']}: has_tables={page['has_tables']}, has_images={page['has_images']}")

# Create custom chunks
chunks = chunk_pages(pages, pages_per_chunk=5)
print(f"Created {len(chunks)} chunks")
```

## How It Works

### Standard Mode

1. **Text Extraction**: Extracts text from PDF using PyMuPDF
2. **Chunking**: Breaks content into manageable chunks (default: 5 pages per chunk)
3. **LLM Processing**: Sends each chunk to your chosen AI provider for intelligent markdown conversion
4. **Reassembly**: Combines all chunks into a single, formatted markdown document

### Vision Mode (Recommended)

1. **Multimodal Extraction**: Extracts both text and renders page images from PDF
2. **Smart Chunking**: Groups pages into larger chunks (default: 8 pages) for better context
3. **Visual Analysis**: AI analyzes both text and images for superior layout understanding
4. **Enhanced Accuracy**: Better detection of tables, charts, diagrams, and complex layouts
5. **Reassembly**: Combines chunks with intelligent deduplication of headers/footers

**When to use Vision Mode:**
- Documents with tables or complex layouts
- PDFs containing charts, diagrams, or visual elements
- Academic papers or technical documentation
- Any document where layout matters

## Performance Tips

### Choosing Between Standard and Vision Mode

**Use Vision Mode when:**
- PDF contains tables, charts, or diagrams
- Layout and formatting are important
- You need accurate table extraction
- Document has complex multi-column layouts

**Use Standard Mode when:**
- Simple text-only documents
- Speed and cost are priorities
- Document has straightforward single-column layout

### Chunk Size Optimization

**Larger chunks (8-10 pages):**
- Better context for the AI model
- More efficient API usage
- Better for documents with consistent formatting
- Default for vision mode

**Smaller chunks (3-5 pages):**
- Better for very large documents (500+ pages)
- Reduces memory usage
- Helpful when hitting API token limits
- Default for standard mode

### Vision Mode Settings

**DPI Settings:**
- Default (150 DPI): Good balance of quality and performance
- High quality (200-300 DPI): For small text or detailed diagrams
- Lower (100 DPI): Faster processing, suitable for simple layouts

**Adjusting chunk size in vision mode:**
```bash
# Smaller chunks for very large documents
pdf-to-md-llm convert large.pdf --vision --vision-pages-per-chunk 4

# Larger chunks for better context
pdf-to-md-llm convert doc.pdf --vision --vision-pages-per-chunk 12
```

## Troubleshooting

### API Key Errors

**Error:** `ValueError: API key not found`

**Solution:**
- Verify your API key is set in environment variables
- Check the key name matches your provider (ANTHROPIC_API_KEY or OPENAI_API_KEY)
- Ensure the key is valid and not expired

### Rate Limiting

**Error:** API rate limit exceeded

**Solution:**
- Reduce chunk size to make smaller API requests
- Add delays between batch conversions
- Upgrade your API plan for higher limits
- Switch providers if one is experiencing issues

### Large File Issues

**Error:** Memory errors or timeouts on large PDFs

**Solution:**
- Use smaller chunk sizes: `--vision-pages-per-chunk 3`
- Process in batches by splitting the PDF first
- Use standard mode instead of vision for simple documents
- Increase available system memory

### Vision Mode Memory Issues

**Error:** Out of memory when using vision mode

**Solution:**
- Reduce DPI: `--vision-dpi 100`
- Use smaller chunks: `--vision-pages-per-chunk 4`
- Process fewer pages at once
- Close other applications to free memory

### Poor Quality Output

**Problem:** Markdown output has formatting issues

**Solution:**
- Try vision mode for better layout detection: `--vision`
- Increase DPI for better image quality: `--vision-dpi 200`
- Try different models: `--provider openai --model gpt-4o`
- Adjust chunk size for better context

## API Reference

### Main Functions

#### `convert_pdf_to_markdown()`

```python
def convert_pdf_to_markdown(
    pdf_path: str,
    output_path: Optional[str] = None,
    pages_per_chunk: int = 5,
    provider: str = "anthropic",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: int = 4000,
    verbose: bool = True,
    use_vision: bool = False,
    vision_dpi: int = 150
) -> str
```

Convert a single PDF to markdown.

**Parameters:**
- `pdf_path`: Path to the PDF file
- `output_path`: Optional output file path (defaults to PDF name with .md extension)
- `pages_per_chunk`: Number of pages per API call (default: 5 for standard, 8 for vision)
- `provider`: AI provider - 'anthropic' or 'openai' (default: 'anthropic')
- `api_key`: API key (defaults to provider-specific environment variable)
- `model`: Model to use (optional, uses provider defaults)
- `max_tokens`: Maximum tokens per API call (default: 4000)
- `verbose`: Print progress messages (default: True)
- `use_vision`: Enable vision mode for better extraction (default: False)
- `vision_dpi`: DPI for page images in vision mode (default: 150)

**Returns:** The complete markdown content as a string

**Raises:** `ValueError` if API key is missing or provider is invalid

#### `batch_convert()`

```python
def batch_convert(
    input_folder: str,
    output_folder: Optional[str] = None,
    pages_per_chunk: int = 5,
    provider: str = "anthropic",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_tokens: int = 4000,
    verbose: bool = True,
    use_vision: bool = False,
    vision_dpi: int = 150,
    threads: int = 1,
    skip_existing: bool = False
) -> None
```

Convert all PDFs in a folder to markdown.

**Parameters:**
- `input_folder`: Folder containing PDF files
- `output_folder`: Optional output folder (defaults to input folder)
- `threads`: Number of threads for parallel processing (default: 1 for single-threaded)
- `skip_existing`: Skip files that already have corresponding .md files in output directory (default: False)
- All other parameters same as `convert_pdf_to_markdown()`

**Note on Multithreading:**
- Single-threaded (`threads=1`): Default, sequential processing
- Multithreaded (`threads>1`): Parallel processing for faster batch conversion
- Be mindful of API rate limits when using higher thread counts
- Progress output is simplified in multithreaded mode for clarity

#### `extract_text_from_pdf()`

```python
def extract_text_from_pdf(pdf_path: str) -> List[str]
```

Extract raw text from PDF (standard mode).

**Returns:** List of strings, one per page

#### `extract_pages_with_vision()`

```python
def extract_pages_with_vision(pdf_path: str, dpi: int = 150) -> List[Dict[str, Any]]
```

Extract text and images from PDF pages for vision processing.

**Returns:** List of dicts with keys: `page_num`, `text`, `image_base64`, `has_images`, `has_tables`

#### `chunk_pages()`

```python
def chunk_pages(pages: List[str], pages_per_chunk: int) -> List[str]
```

Combine pages into chunks for processing.

**Returns:** List of combined page chunks

## Output Format

Converted markdown files include:

- Document title header
- Clean heading hierarchy
- Properly formatted tables
- Organized lists
- Removed page numbers and PDF artifacts
- Conversion metadata footer

## Requirements

- Python 3.9 or higher
- API key for at least one provider:
  - Anthropic API key (for Claude models)
  - OpenAI API key (for GPT models)

## Dependencies

All dependencies are automatically installed:

- **anthropic**: Claude API client (for Anthropic provider)
- **openai**: OpenAI API client (for OpenAI provider)
- **pymupdf**: PDF text and image extraction
- **python-dotenv**: Environment variable management
- **click**: CLI framework

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and contribution guidelines.

For bug reports and feature requests, please open an issue on [GitHub](https://github.com/densom/pdf-to-md-llm/issues).
