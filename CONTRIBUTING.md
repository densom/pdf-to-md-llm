# Contributing to PDF to Markdown Converter

Thank you for your interest in contributing! This document provides guidelines for developers and maintainers.

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/densom/pdf-to-md-llm.git
cd pdf-to-md-llm

# Install uv if you don't have it
pip install uv

# Install dependencies
uv sync
```

### Configuration

Create a `.env.local` file in the project root with your API key(s):

```bash
# For Anthropic (Claude)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# For OpenAI (GPT)
OPENAI_API_KEY=your-openai-api-key-here
```

### Running from Source

After installing dependencies with `uv sync`, you can run the tool directly:

```bash
# Using uv run
uv run pdf-to-md-llm convert document.pdf

# Or as a Python module
python -m pdf_to_md_llm convert document.pdf
```

## Testing

Before submitting changes, test your modifications:

```bash
# Test single file conversion
uv run pdf-to-md-llm convert test.pdf --verbose

# Test batch conversion
uv run pdf-to-md-llm batch ./test-pdfs --verbose

# Test vision mode
uv run pdf-to-md-llm convert test.pdf --vision --verbose
```

## Building the Package

To test the build process locally without publishing:

```bash
# Build the package
uv build

# Check the built files
ls -la dist/

# The dist/ folder will contain:
# - pdf_to_md_llm-X.Y.Z-py3-none-any.whl
# - pdf_to_md_llm-X.Y.Z.tar.gz
```

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

For complete setup instructions, see [.github/PUBLISHING.md](.github/PUBLISHING.md)

## Code Contributions

### Guidelines

- Follow existing code style and conventions
- Test your changes thoroughly before submitting
- Update documentation if you add or change features
- Keep commits focused and write clear commit messages

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test your changes
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

### Code Style

- Use type hints where appropriate
- Follow PEP 8 guidelines
- Keep functions focused and well-documented
- Add docstrings for public functions

## Questions or Issues?

- Open an issue on GitHub for bugs or feature requests
- Check existing issues before creating new ones
- Provide clear reproduction steps for bugs
