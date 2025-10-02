# PDF to Markdown Converter

Convert PDF documents to clean, well-structured Markdown using LLM-assisted processing powered by Claude API.

## Features

- **Smart Conversion**: Uses Claude API to intelligently convert PDF content to clean markdown
- **Large File Support**: Automatically chunks large PDFs for optimal processing
- **Batch Processing**: Convert entire folders of PDFs with preserved directory structure
- **Format Cleanup**: Removes PDF artifacts, fixes spacing, and ensures proper formatting
- **Table Preservation**: Converts tables to proper markdown table format
- **Structure Detection**: Automatically generates appropriate heading hierarchy
- **Dual Interface**: Use as both a CLI tool and a Python library

## Requirements

- Python 3.9 or higher
- Anthropic API key

## Installation

### From PyPI (Recommended)

```bash
pip install pdf-to-md-llm
```

### From Source

This project uses [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
# Clone the repository
git clone https://github.com/densom/pdf-to-md-llm.git
cd pdf-to-md-llm

# Install dependencies
uv sync
```

## Configuration

Create a `.env.local` file in the project root with your API key:

```bash
ANTHROPIC_API_KEY=your-api-key-here
```

Or set the environment variable directly:

```bash
export ANTHROPIC_API_KEY='your-api-key-here'
```

## Usage

### As a Command-Line Tool

After installation via pip, the `pdf-to-md-llm` command will be available:

#### Single File Conversion

```bash
# Convert with auto-generated output filename
pdf-to-md-llm convert document.pdf

# Convert with custom output filename
pdf-to-md-llm convert document.pdf output.md

# Convert with custom chunk size
pdf-to-md-llm convert document.pdf --pages-per-chunk 10
```

#### Batch Conversion

```bash
# Convert all PDFs in a folder (output to same folder)
pdf-to-md-llm batch ./input-folder

# Convert with custom output folder
pdf-to-md-llm batch ./input-folder ./output-folder
```

#### Alternative: Run as Python Module

```bash
python -m pdf_to_md_llm convert document.pdf
python -m pdf_to_md_llm batch ./input-folder
```

#### Getting Help

```bash
# Show general help
pdf-to-md-llm --help

# Show help for a specific command
pdf-to-md-llm convert --help
pdf-to-md-llm batch --help
```

### As a Python Library

```python
from pdf_to_md_llm import convert_pdf_to_markdown, batch_convert

# Convert a single PDF
markdown_content = convert_pdf_to_markdown(
    pdf_path="document.pdf",
    output_path="output.md",  # Optional
    pages_per_chunk=5,  # Optional
    api_key="your-api-key",  # Optional, uses ANTHROPIC_API_KEY env var by default
    verbose=True  # Optional, print progress
)

# Batch convert all PDFs in a folder
batch_convert(
    input_folder="./pdfs",
    output_folder="./markdown",  # Optional
    pages_per_chunk=5,  # Optional
    api_key="your-api-key",  # Optional
    verbose=True  # Optional
)
```

### Advanced Library Usage

```python
from pdf_to_md_llm import extract_text_from_pdf, chunk_pages

# Extract text from PDF (returns list of page strings)
pages = extract_text_from_pdf("document.pdf")
print(f"Found {len(pages)} pages")

# Chunk pages for processing
chunks = chunk_pages(pages, pages_per_chunk=5)
print(f"Created {len(chunks)} chunks")

# Process chunks with your own logic...
```

## How It Works

1. **Text Extraction**: Extracts text from PDF using PyMuPDF
2. **Chunking**: Breaks content into manageable chunks (default: 5 pages per chunk)
3. **LLM Processing**: Sends each chunk to Claude API for intelligent markdown conversion
4. **Reassembly**: Combines all chunks into a single, formatted markdown document

## Configuration Options

Edit `pdf_to_markdown.py` to adjust:

- `MODEL`: Claude model to use (default: `claude-sonnet-4-20250514`)
- `MAX_TOKENS`: Maximum tokens per API call (default: 4000)
- `PAGES_PER_CHUNK`: Pages to process per API call (default: 5)

## Dependencies

- **anthropic**: Claude API client
- **pymupdf**: PDF text extraction
- **python-dotenv**: Environment variable management
- **click**: CLI framework

## Output Format

Converted markdown files include:

- Document title header
- Clean heading hierarchy
- Properly formatted tables
- Organized lists
- Removed page numbers and PDF artifacts
- Conversion metadata

## API Reference

### Main Functions

#### `convert_pdf_to_markdown()`

```python
def convert_pdf_to_markdown(
    pdf_path: str,
    output_path: Optional[str] = None,
    pages_per_chunk: int = 5,
    api_key: Optional[str] = None,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 4000,
    verbose: bool = True
) -> str
```

Convert a single PDF to markdown.

**Parameters:**
- `pdf_path`: Path to the PDF file
- `output_path`: Optional output file path (defaults to PDF name with .md extension)
- `pages_per_chunk`: Number of pages to process per API call (default: 5)
- `api_key`: Anthropic API key (defaults to ANTHROPIC_API_KEY environment variable)
- `model`: Claude model to use
- `max_tokens`: Maximum tokens per API call
- `verbose`: Print progress messages

**Returns:** The complete markdown content as a string

**Raises:** `ValueError` if API key is not provided

#### `batch_convert()`

```python
def batch_convert(
    input_folder: str,
    output_folder: Optional[str] = None,
    pages_per_chunk: int = 5,
    api_key: Optional[str] = None,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 4000,
    verbose: bool = True
) -> None
```

Convert all PDFs in a folder to markdown.

**Parameters:**
- `input_folder`: Folder containing PDF files
- `output_folder`: Optional output folder (defaults to input folder)
- Other parameters same as `convert_pdf_to_markdown()`

#### `extract_text_from_pdf()`

```python
def extract_text_from_pdf(pdf_path: str) -> List[str]
```

Extract raw text from PDF.

**Returns:** List of strings, one per page

#### `chunk_pages()`

```python
def chunk_pages(pages: List[str], pages_per_chunk: int) -> List[str]
```

Combine pages into chunks for processing.

**Returns:** List of combined page chunks

## Publishing to PyPI

### For Package Maintainers

1. **Install build dependencies:**
   ```bash
   pip install uv
   ```

2. **Build the package:**
   ```bash
   uv build
   ```
   This creates distribution files in the `dist/` directory.

3. **Publish to PyPI:**
   ```bash
   uv publish
   ```
   You'll need a PyPI account and API token.

4. **Or publish to Test PyPI first:**
   ```bash
   uv publish --publish-url https://test.pypi.org/legacy/
   ```

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
