# Publishing Setup

This document explains how to set up publishing to Test PyPI and PyPI using the GitHub Actions workflows.

## Prerequisites

1. **Test PyPI Account**: Create an account at [test.pypi.org](https://test.pypi.org/)
2. **PyPI Account**: Create an account at [pypi.org](https://pypi.org/) (for production publishing)

## Setting up API Tokens

### Test PyPI Token

1. Go to [test.pypi.org](https://test.pypi.org/)
2. Log in to your account
3. Go to Account Settings → API tokens
4. Click "Add API token"
5. Name: `pdf-to-md-llm-test` (or similar)
6. Scope: Select "Entire account" or limit to this project if it exists
7. Copy the generated token (starts with `pypi-`)

### Production PyPI Token

1. Go to [pypi.org](https://pypi.org/)
2. Log in to your account
3. Go to Account Settings → API tokens
4. Click "Add API token"
5. Name: `pdf-to-md-llm-prod` (or similar)
6. Scope: Select "Entire account" or limit to this project if it exists
7. Copy the generated token (starts with `pypi-`)

## GitHub Repository Setup

### 1. Create GitHub Environments

1. Go to your repository settings
2. Navigate to "Environments"
3. Create two environments:
   - `test-pypi` (for test publishing)
   - `production` (for production publishing)

### 2. Add Repository Secrets

#### For Test PyPI Environment:
1. Go to Settings → Environments → `test-pypi`
2. Add environment secret:
   - Name: `TEST_PYPI_API_TOKEN`
   - Value: Your Test PyPI token (from above)

#### For Production Environment (when ready):
1. Go to Settings → Environments → `production`
2. Add environment secret:
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI token (from above)

## Publishing to Test PyPI

### Manual Publishing

1. Go to the "Actions" tab in your GitHub repository
2. Select "Publish to Test PyPI" workflow
3. Click "Run workflow"
4. Optionally specify a version number (e.g., `0.1.1-test1`)
5. Click "Run workflow"

### After Publishing

1. Check the workflow run for any errors
2. Visit [test.pypi.org/project/pdf-to-md-llm/](https://test.pypi.org/project/pdf-to-md-llm/) to see your package
3. Test installation from Test PyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pdf-to-md-llm
   ```

## Version Management

- The workflow can automatically update version numbers if specified
- Version is updated in both `pyproject.toml` and `pdf_to_md_llm/__init__.py`
- If no version is specified, the current version from `pyproject.toml` is used

## Troubleshooting

### Common Issues

1. **Token errors**: Ensure the API token is correctly copied and stored in the right environment
2. **Package already exists**: Test PyPI doesn't allow overwriting. Use a different version number
3. **Build failures**: Check that all dependencies are properly specified in `pyproject.toml`

### Testing the Build Locally

Before publishing, you can test the build process locally:

```bash
# Install uv if not already installed
pip install uv

# Sync dependencies
uv sync

# Build the package
uv build

# Check the built files
ls -la dist/
```

## Next Steps

Once test publishing is working successfully:

1. Create a production publishing workflow
2. Set up proper versioning strategy
3. Add automated testing before publishing
4. Consider setting up branch protection rules