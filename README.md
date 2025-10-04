# PDF to Markdown Converter

Convert PDF documents to clean, well-structured Markdown using LLM-assisted processing powered by Claude API.

## Features

- **Multi-Provider Support**: Use Anthropic (Claude) or OpenAI (GPT) models
- **Vision Mode**: Enhanced extraction using image analysis for complex layouts, tables, and charts
- **Smart Conversion**: Intelligently converts PDF content to clean markdown with LLM assistance
- **Large File Support**: Automatically chunks large PDFs for optimal processing
- **Batch Processing**: Convert entire folders of PDFs with preserved directory structure
- **Format Cleanup**: Removes PDF artifacts, fixes spacing, and ensures proper formatting
- **Table Preservation**: Converts tables to proper markdown table format with vision-enhanced accuracy
- **Structure Detection**: Automatically generates appropriate heading hierarchy
- **Dual Interface**: Use as both a CLI tool and a Python library

## Requirements

- Python 3.9 or higher
- API key for at least one provider:
  - Anthropic API key (for Claude models)
  - OpenAI API key (for GPT models)

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

Create a `.env.local` file in the project root with your API key(s):

```bash
# For Anthropic (Claude)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# For OpenAI (GPT)
OPENAI_API_KEY=your-openai-api-key-here
```

Or set the environment variables directly:

```bash
export ANTHROPIC_API_KEY='your-anthropic-api-key-here'
export OPENAI_API_KEY='your-openai-api-key-here'
```

## Usage

### As a Command-Line Tool

After installation via pip, the `pdf-to-md-llm` command will be available:

#### Single File Conversion

```bash
# Convert with auto-generated output filename (uses Anthropic by default)
pdf-to-md-llm convert document.pdf

# Convert with custom output filename
pdf-to-md-llm convert document.pdf output.md

# Convert with vision mode (recommended for complex layouts and tables)
pdf-to-md-llm convert document.pdf --vision

# Use OpenAI instead of Anthropic
pdf-to-md-llm convert document.pdf --provider openai --vision

# Custom chunk size for vision mode
pdf-to-md-llm convert document.pdf --vision --vision-pages-per-chunk 6

# Specify model
pdf-to-md-llm convert document.pdf --provider anthropic --model claude-sonnet-4-20250514
```

#### Batch Conversion

```bash
# Convert all PDFs in a folder (output to same folder)
pdf-to-md-llm batch ./input-folder

# Convert with custom output folder
pdf-to-md-llm batch ./input-folder ./output-folder

# Batch convert with vision mode
pdf-to-md-llm batch ./input-folder --vision

# Batch convert with OpenAI
pdf-to-md-llm batch ./input-folder --provider openai --vision
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

# Convert a single PDF with vision mode (recommended)
markdown_content = convert_pdf_to_markdown(
    pdf_path="document.pdf",
    output_path="output.md",  # Optional
    provider="anthropic",  # Optional: 'anthropic' or 'openai'
    use_vision=True,  # Optional: enables vision mode for better table extraction
    pages_per_chunk=8,  # Optional: pages per chunk (vision mode default: 8)
    api_key="your-api-key",  # Optional, uses provider-specific env var by default
    verbose=True  # Optional: print progress
)

# Convert with OpenAI
markdown_content = convert_pdf_to_markdown(
    pdf_path="document.pdf",
    provider="openai",
    model="gpt-4o",  # Optional: specify model
    use_vision=True,
    api_key="your-openai-key"
)

# Batch convert all PDFs in a folder
batch_convert(
    input_folder="./pdfs",
    output_folder="./markdown",  # Optional
    provider="anthropic",  # Optional
    use_vision=True,  # Optional: vision mode for all conversions
    pages_per_chunk=8,  # Optional
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

### Standard Mode
1. **Text Extraction**: Extracts text from PDF using PyMuPDF
2. **Chunking**: Breaks content into manageable chunks (default: 5 pages per chunk)
3. **LLM Processing**: Sends each chunk to your chosen AI provider for intelligent markdown conversion
4. **Reassembly**: Combines all chunks into a single, formatted markdown document

### Vision Mode (Recommended)
1. **Text + Image Extraction**: Extracts both text and renders page images from PDF
2. **Smart Chunking**: Groups pages into larger chunks (default: 8 pages per chunk) for better context
3. **Multimodal Processing**: Sends both images and text to vision-capable models for superior layout understanding
4. **Enhanced Accuracy**: Better table detection, chart description, and layout preservation
5. **Reassembly**: Combines chunks with deduplication of headers/footers

## Configuration Options

Default values in `converter.py`:

- `DEFAULT_PROVIDER`: AI provider (default: `anthropic`)
- `DEFAULT_MODEL`: Model for Anthropic (default: `claude-sonnet-4-20250514`)
- `DEFAULT_MAX_TOKENS`: Maximum tokens per API call (default: 4000)
- `DEFAULT_PAGES_PER_CHUNK`: Pages per chunk for standard mode (default: 5)
- `DEFAULT_VISION_PAGES_PER_CHUNK`: Pages per chunk for vision mode (default: 8)
- `DEFAULT_VISION_DPI`: Image rendering DPI for vision mode (default: 150)

## Dependencies

- **anthropic**: Claude API client (optional, for Anthropic provider)
- **openai**: OpenAI API client (optional, for OpenAI provider)
- **pymupdf**: PDF text and image extraction
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
- `pages_per_chunk`: Number of pages to process per API call (default: 5 for standard, 8 for vision)
- `provider`: AI provider to use - 'anthropic' or 'openai' (default: 'anthropic')
- `api_key`: API key (defaults to provider-specific environment variable)
- `model`: Model to use (optional, uses provider defaults if not specified)
- `max_tokens`: Maximum tokens per API call (default: 4000)
- `verbose`: Print progress messages (default: True)
- `use_vision`: Enable vision mode for better layout/table extraction (default: False)
- `vision_dpi`: DPI for rendering page images in vision mode (default: 150)

**Returns:** The complete markdown content as a string

**Raises:** `ValueError` if API key is not provided or provider is invalid

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
    vision_dpi: int = 150
) -> None
```

Convert all PDFs in a folder to markdown.

**Parameters:**
- `input_folder`: Folder containing PDF files
- `output_folder`: Optional output folder (defaults to input folder)
- All other parameters same as `convert_pdf_to_markdown()`

#### `extract_text_from_pdf()`

```python
def extract_text_from_pdf(pdf_path: str) -> List[str]
```

Extract raw text from PDF.

**Returns:** List of strings, one per page

#### `extract_pages_with_vision()`

```python
def extract_pages_with_vision(pdf_path: str, dpi: int = 150) -> List[Dict[str, Any]]
```

Extract both text and images from PDF pages for vision-based processing.

**Returns:** List of dicts with keys: `page_num`, `text`, `image_base64`, `has_images`, `has_tables`

#### `chunk_pages()`

```python
def chunk_pages(pages: List[str], pages_per_chunk: int) -> List[str]
```

Combine pages into chunks for processing.

**Returns:** List of combined page chunks

## Publishing to PyPI

### For Package Maintainers

This project uses automated GitHub Actions workflows for publishing to PyPI.

#### Production Releases (Automatic)

Publishing to PyPI happens automatically when commits are pushed or merged to the `main` branch:

1. **Update version numbers:**
   - Update version in `pyproject.toml`
   - Update version in `pdf_to_md_llm/__init__.py`
   - Ensure both versions match

2. **Merge to main:**
   - Create a PR with your changes
   - Merge to `main` branch
   - The workflow automatically builds and publishes to PyPI

3. **Verify:**
   - Check the GitHub Actions tab for workflow status
   - Visit [pypi.org/project/pdf-to-md-llm/](https://pypi.org/project/pdf-to-md-llm/)

#### Test Releases (Manual)

For testing before production release:

1. Go to GitHub Actions tab
2. Select "Publish to Test PyPI" workflow
3. Click "Run workflow"
4. Optionally provide a test version (e.g., `0.1.1-test1`)
5. Install from Test PyPI to verify:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pdf-to-md-llm
   ```

#### Local Build Testing

To test the build process locally without publishing:

```bash
# Install uv
pip install uv

# Build the package
uv build

# Check the built files
ls -la dist/
```

For complete setup instructions, see [.github/PUBLISHING.md](.github/PUBLISHING.md)

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
