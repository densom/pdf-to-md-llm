#!/usr/bin/env python3
"""
Command-line interface for PDF to Markdown converter
"""

import os
import click
from functools import wraps
from dotenv import load_dotenv
from .converter import (
    convert_pdf_to_markdown,
    batch_convert,
    DEFAULT_PAGES_PER_CHUNK,
    DEFAULT_PROVIDER,
    DEFAULT_VISION_DPI,
    DEFAULT_THREADS
)
from .providers import validate_api_key_available, list_models_for_providers

# Load environment variables from .env file
load_dotenv()

# Provider display names
PROVIDER_DISPLAY_NAMES = {
    'anthropic': 'Anthropic (Claude)',
    'openai': 'OpenAI (GPT)'
}

# Helper functions for validation
def validate_provider_or_abort(provider: str, api_key: str = None):
    """Validate API key is available or abort the CLI command"""
    is_valid, error_message = validate_api_key_available(provider.lower(), api_key)
    if not is_valid:
        click.echo(error_message, err=True)
        raise click.Abort()

def get_effective_pages_per_chunk(pages_per_chunk: int, vision: bool, vision_pages_per_chunk: int = None) -> int:
    """Determine effective pages per chunk for vision mode"""
    if vision and vision_pages_per_chunk is not None:
        return vision_pages_per_chunk
    return pages_per_chunk

def resolve_system_prompt(system_prompt: str = None, system_prompt_file: str = None) -> str:
    """Resolve the final system prompt from options"""
    # File takes precedence if both are provided
    if system_prompt_file:
        with open(system_prompt_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    elif system_prompt:
        return system_prompt.strip()
    return None

# Shared CLI option decorators
# These decorators implement the Decorator Pattern to add reusable option groups to Click commands.
# They eliminate duplication by allowing multiple commands to share the same option definitions.

def provider_options(f):
    """Add provider-related options to a command"""
    @click.option('--provider', default=DEFAULT_PROVIDER, type=click.Choice(['anthropic', 'openai'], case_sensitive=False),
                  help=f'AI provider to use (default: {DEFAULT_PROVIDER})')
    @click.option('--model', default=None, type=str,
                  help='Model to use (optional, uses provider defaults if not specified)')
    @click.option('--api-key', default=None, type=str,
                  help='API key for the provider (optional, uses environment variable if not specified)')
    # @wraps preserves the original function's metadata (name, docstring, signature).
    # Without it, Click's introspection would see 'wrapper' instead of the actual command,
    # breaking help text generation and command registration.
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper

def chunking_options(f):
    """Add chunking-related options to a command"""
    @click.option('--pages-per-chunk', default=DEFAULT_PAGES_PER_CHUNK, type=int,
                  help=f'Number of pages to process per API call (default: {DEFAULT_PAGES_PER_CHUNK})')
    # @wraps preserves the original function's metadata (name, docstring, signature).
    # Without it, Click's introspection would see 'wrapper' instead of the actual command,
    # breaking help text generation and command registration.
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper

def vision_options(f):
    """Add vision-related options to a command"""
    @click.option('--vision/--no-vision', default=False,
                  help='Enable vision mode for better layout/table/chart extraction (recommended)')
    @click.option('--vision-dpi', default=DEFAULT_VISION_DPI, type=int,
                  help=f'DPI for rendering page images in vision mode (default: {DEFAULT_VISION_DPI})')
    @click.option('--vision-pages-per-chunk', default=None, type=int,
                  help='Pages per chunk in vision mode (overrides --pages-per-chunk for vision mode)')
    # @wraps preserves the original function's metadata (name, docstring, signature).
    # Without it, Click's introspection would see 'wrapper' instead of the actual command,
    # breaking help text generation and command registration.
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper

def system_prompt_options(f):
    """Add system prompt customization options to a command"""
    @click.option('--system-prompt', default=None, type=str,
                  help='Custom instructions to append to the default conversion prompt')
    @click.option('--system-prompt-file', default=None, type=click.Path(exists=True, dir_okay=False),
                  help='File containing custom instructions to append to the default conversion prompt')
    # @wraps preserves the original function's metadata (name, docstring, signature).
    # Without it, Click's introspection would see 'wrapper' instead of the actual command,
    # breaking help text generation and command registration.
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version and exit')
@click.pass_context
def cli(ctx, version):
    """PDF to Markdown Converter (LLM-Assisted)

    Convert PDF documents to clean, well-structured Markdown using AI providers.

    Supported providers: anthropic (Claude), openai (GPT)

    Set the appropriate API key environment variable:
    - ANTHROPIC_API_KEY for Anthropic/Claude
    - OPENAI_API_KEY for OpenAI/GPT
    """
    # If --version flag is provided, show version and exit
    if version:
        from importlib.metadata import version as get_version
        try:
            pkg_version = get_version('pdf-to-md-llm')
            click.echo(pkg_version)
        except Exception:
            click.echo('unknown', err=True)
        ctx.exit()

    # If no subcommand is provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument('pdf_file', type=click.Path(exists=True, dir_okay=False))
@click.argument('output_file', type=click.Path(), required=False)
@system_prompt_options
@vision_options
@chunking_options
@provider_options
def convert(pdf_file, output_file, provider, model, api_key, pages_per_chunk, vision, vision_dpi, vision_pages_per_chunk, system_prompt, system_prompt_file):
    """Convert a single PDF file to markdown.

    PDF_FILE: Path to the PDF file to convert

    OUTPUT_FILE: Optional output path (defaults to same name with .md extension)

    Vision mode provides significantly better results for documents with complex layouts,
    tables, charts, or multi-column formats. It uses ~2-3x more tokens but delivers
    superior quality.
    """
    # Validate API key is available before processing
    validate_provider_or_abort(provider, api_key)

    # Determine effective pages per chunk for vision mode
    effective_pages_per_chunk = get_effective_pages_per_chunk(pages_per_chunk, vision, vision_pages_per_chunk)

    # Resolve system prompt from options
    final_system_prompt = resolve_system_prompt(system_prompt, system_prompt_file)

    convert_pdf_to_markdown(
        pdf_file,
        output_file,
        pages_per_chunk=effective_pages_per_chunk,
        provider=provider.lower(),
        api_key=api_key,
        model=model,
        use_vision=vision,
        vision_dpi=vision_dpi,
        system_prompt=final_system_prompt
    )


@cli.command()
@click.option('--provider', default=None, type=click.Choice(['anthropic', 'openai'], case_sensitive=False),
              help='Filter by specific provider (optional, shows all providers by default)')
def models(provider):
    """List available AI models from configured providers.

    Shows models from providers that have API keys configured.
    Use --provider to filter by a specific provider.

    Examples:
        pdf-to-md-llm models
        pdf-to-md-llm models --provider anthropic
        pdf-to-md-llm models --provider openai
    """
    try:
        # Get models from all or specific provider
        providers_data = list_models_for_providers(provider)

        # Check if any providers are available
        available_providers = [p for p, data in providers_data.items() if data['available']]

        # Check if there were errors trying to access providers
        providers_with_errors = [
            (p, data) for p, data in providers_data.items()
            if not data['available'] and data.get('error') and data['error'] != 'API key not found'
        ]

        if not available_providers:
            # If we have errors (like invalid keys), show those
            if providers_with_errors:
                click.echo("\nFailed to list models:\n", err=True)
                for provider_name, data in providers_with_errors:
                    provider_display = PROVIDER_DISPLAY_NAMES.get(provider_name, provider_name.title())

                    error_msg = data['error']
                    click.echo(f"{provider_display}:", err=True)
                    click.echo(f"  {error_msg}", err=True)

                    # Check if it's an authentication error
                    if 'authentication' in error_msg.lower() or '401' in error_msg:
                        click.echo(f"\n  Your API key appears to be invalid. Please check:", err=True)
                        env_var = f"{provider_name.upper()}_API_KEY"
                        click.echo(f"  - The {env_var} environment variable", err=True)
                        click.echo(f"  - Get a valid key at:", err=True)
                        if provider_name == 'anthropic':
                            click.echo(f"    https://console.anthropic.com/settings/keys", err=True)
                        elif provider_name == 'openai':
                            click.echo(f"    https://platform.openai.com/api-keys", err=True)
                    click.echo()
                return

            # Otherwise, no API keys configured at all
            click.echo("No API keys configured!")
            click.echo("\nTo list models, you need to configure at least one provider:")
            click.echo("\n  Anthropic (Claude):")
            click.echo("    export ANTHROPIC_API_KEY='your-api-key-here'")
            click.echo("\n  OpenAI (GPT):")
            click.echo("    export OPENAI_API_KEY='your-api-key-here'")
            return

        # Display models organized by provider
        click.echo("\nAvailable Models:\n")

        for provider_name, data in providers_data.items():
            if not data['available']:
                # Skip unavailable providers unless specifically requested
                if provider and provider.lower() == provider_name:
                    error_msg = data.get('error', 'Not available')
                    click.echo(f"\n{provider_name.title()}: Failed to list models", err=True)
                    click.echo(f"Error: {error_msg}", err=True)

                    # Provide helpful troubleshooting info
                    if 'API key' in error_msg or 'not found' in error_msg:
                        env_var = f"{provider_name.upper()}_API_KEY"
                        click.echo(f"\nMake sure your {env_var} is configured correctly.", err=True)
                        click.echo(f"  export {env_var}='your-api-key-here'", err=True)
                continue

            # Provider header
            provider_display = PROVIDER_DISPLAY_NAMES.get(provider_name, provider_name.title())

            click.echo(f"{provider_display}:")

            # List models
            default_model = data.get('default_model')
            models_list = data.get('models', [])

            if 'error' in data:
                # API call succeeded but there was an issue
                click.echo(f"  Error: {data['error']}", err=True)
            elif not models_list:
                click.echo("  No models found")
            else:
                for model in models_list:
                    model_id = model['id']
                    is_default = model_id == default_model
                    default_marker = " (default)" if is_default else ""
                    click.echo(f"  • {model_id}{default_marker}")

            click.echo()  # Blank line between providers

    except Exception as e:
        click.echo(f"Error listing models: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('input_folder', type=click.Path(exists=True, file_okay=False))
@click.argument('output_folder', type=click.Path(), required=False)
@click.option('--threads', type=int, default=DEFAULT_THREADS,
              help=f'Number of threads for parallel processing (default: {DEFAULT_THREADS}). Use 2+ for faster batch conversion.')
@click.option('--skip-existing', is_flag=True, default=False,
              help='Skip files that already have corresponding .md files in the output directory')
@system_prompt_options
@vision_options
@chunking_options
@provider_options
def batch(input_folder, output_folder, threads, skip_existing, provider, model, api_key, pages_per_chunk, vision, vision_dpi, vision_pages_per_chunk, system_prompt, system_prompt_file):
    """Convert all PDF files in a folder to markdown.

    INPUT_FOLDER: Folder containing PDF files

    OUTPUT_FOLDER: Optional output folder (defaults to same as input)

    Vision mode provides significantly better results for documents with complex layouts,
    tables, charts, or multi-column formats. It uses ~2-3x more tokens but delivers
    superior quality.

    Use --threads to enable parallel processing for faster batch conversion. Note that
    higher thread counts may increase API rate limit risks.
    """
    # Validate API key is available before processing
    validate_provider_or_abort(provider, api_key)

    # Determine effective pages per chunk for vision mode
    effective_pages_per_chunk = get_effective_pages_per_chunk(pages_per_chunk, vision, vision_pages_per_chunk)

    # Resolve system prompt from options
    final_system_prompt = resolve_system_prompt(system_prompt, system_prompt_file)

    batch_convert(
        input_folder,
        output_folder,
        pages_per_chunk=effective_pages_per_chunk,
        provider=provider.lower(),
        api_key=api_key,
        model=model,
        use_vision=vision,
        vision_dpi=vision_dpi,
        threads=threads,
        skip_existing=skip_existing,
        system_prompt=final_system_prompt
    )


if __name__ == "__main__":
    cli()
