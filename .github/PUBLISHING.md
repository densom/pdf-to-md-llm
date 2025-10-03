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
   - `pypi` (for production publishing)

### 2. Add Repository Secrets

#### For Test PyPI Environment:
1. Go to Settings → Environments → `test-pypi`
2. Add environment secret:
   - Name: `TEST_PYPI_API_TOKEN`
   - Value: Your Test PyPI token (from above)

#### For Production PyPI Environment:
1. Go to Settings → Environments → `pypi`
2. Add environment secret:
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI token (from above)

## Publishing Workflows

### Test PyPI Publishing (Manual)

For testing releases before production:

1. Go to the "Actions" tab in your GitHub repository
2. Select "Publish to Test PyPI" workflow
3. Click "Run workflow"
4. Optionally specify a version number (e.g., `0.1.1-test1`)
5. Click "Run workflow"

**After Publishing:**
1. Check the workflow run for any errors
2. Visit [test.pypi.org/project/pdf-to-md-llm/](https://test.pypi.org/project/pdf-to-md-llm/) to see your package
3. Test installation from Test PyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pdf-to-md-llm
   ```

**Version Management for Test PyPI:**
- The test workflow allows manual version override
- Version is updated in both `pyproject.toml` and `pdf_to_md_llm/__init__.py`
- If no version is specified, the current version from `pyproject.toml` is used

### Production PyPI Publishing (Automatic)

Production releases are automated and triggered by commits to the `main` branch:

**Automatic Publishing:**
1. Update the version number in `pyproject.toml` and `pdf_to_md_llm/__init__.py`
2. Commit and push to `main` branch (or merge a PR to `main`)
3. The "Publish to PyPI" workflow automatically runs and publishes to PyPI
4. Visit [pypi.org/project/pdf-to-md-llm/](https://pypi.org/project/pdf-to-md-llm/) to see your published package

**Manual Publishing (Emergency/Other Branches):**
1. Go to the "Actions" tab in your GitHub repository
2. Select "Publish to PyPI" workflow
3. Click "Run workflow"
4. Select your branch
5. Click "Run workflow"

**Important Notes:**
- Version must be unique - you cannot republish the same version
- Always update version in both `pyproject.toml` and `pdf_to_md_llm/__init__.py` before merging to `main`
- The production workflow does NOT support version override (uses `pyproject.toml` version only)

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

## Workflow Files

- **`.github/workflows/publish-test.yml`**: Manual test publishing to Test PyPI
- **`.github/workflows/publish.yml`**: Automatic production publishing to PyPI (on `main` branch commits)

## Release Process

### Recommended Workflow

1. **Development**: Work on feature branches
2. **Testing**: Use Test PyPI workflow to test package installation
   - Manually trigger "Publish to Test PyPI" workflow
   - Optionally provide a test version like `0.1.1-test1`
3. **Prepare Release**: Update version numbers before merging to `main`
   - Update `pyproject.toml` version
   - Update `pdf_to_md_llm/__init__.py` version
   - Ensure both versions match
4. **Production Release**: Merge to `main`
   - Create PR with version bump
   - Merge PR to `main` branch
   - Automatic publishing to PyPI occurs
5. **Verify**: Check PyPI for the new release

### Version Numbering

Follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

Examples:
- `0.1.0` → `0.1.1` (bug fix)
- `0.1.1` → `0.2.0` (new feature)
- `0.2.0` → `1.0.0` (major release)

For test releases, append a suffix: `0.1.1-test1`, `0.1.1-rc1`, etc.