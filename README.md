# PDF to Markdown Converter

Convert PDF documents to clean, well-structured Markdown using LLM-assisted processing powered by Claude API.

## Features

- **Smart Conversion**: Uses Claude API to intelligently convert PDF content to clean markdown
- **Large File Support**: Automatically chunks large PDFs for optimal processing
- **Batch Processing**: Convert entire folders of PDFs with preserved directory structure
- **Format Cleanup**: Removes PDF artifacts, fixes spacing, and ensures proper formatting
- **Table Preservation**: Converts tables to proper markdown table format
- **Structure Detection**: Automatically generates appropriate heading hierarchy

## Requirements

- Python 3.13 or higher
- Anthropic API key

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management:

```bash
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

The CLI is built with Click and provides two main commands: `convert` for single files and `batch` for folders.

### Single File Conversion

```bash
# Convert with auto-generated output filename
python pdf_to_markdown.py convert document.pdf

# Convert with custom output filename
python pdf_to_markdown.py convert document.pdf output.md

# Convert with custom chunk size
python pdf_to_markdown.py convert document.pdf --pages-per-chunk 10
```

### Batch Conversion

```bash
# Convert all PDFs in a folder (output to same folder)
python pdf_to_markdown.py batch ./input-folder

# Convert with custom output folder
python pdf_to_markdown.py batch ./input-folder ./output-folder
```

### With uv

```bash
uv run pdf_to_markdown.py convert document.pdf
uv run pdf_to_markdown.py batch ./input-folder
```

### Getting Help

```bash
# Show general help
python pdf_to_markdown.py --help

# Show help for a specific command
python pdf_to_markdown.py convert --help
python pdf_to_markdown.py batch --help
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

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
