#!/usr/bin/env python3
"""
Command-line interface for PDF to Markdown converter
"""

import os
import click
from dotenv import load_dotenv
from .converter import (
    convert_pdf_to_markdown,
    batch_convert,
    DEFAULT_PAGES_PER_CHUNK,
    DEFAULT_PROVIDER,
    DEFAULT_VISION_DPI
)
from .providers import validate_api_key_available, list_models_for_providers

# Load environment variables from .env file
load_dotenv()


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """PDF to Markdown Converter (LLM-Assisted)

    Convert PDF documents to clean, well-structured Markdown using AI providers.

    Supported providers: anthropic (Claude), openai (GPT)

    Set the appropriate API key environment variable:
    - ANTHROPIC_API_KEY for Anthropic/Claude
    - OPENAI_API_KEY for OpenAI/GPT
    """
    # If no subcommand is provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument('pdf_file', type=click.Path(exists=True, dir_okay=False))
@click.argument('output_file', type=click.Path(), required=False)
@click.option('--provider', default=DEFAULT_PROVIDER, type=click.Choice(['anthropic', 'openai'], case_sensitive=False),
              help=f'AI provider to use (default: {DEFAULT_PROVIDER})')
@click.option('--model', default=None, type=str,
              help='Model to use (optional, uses provider defaults if not specified)')
@click.option('--api-key', default=None, type=str,
              help='API key for the provider (optional, uses environment variable if not specified)')
@click.option('--pages-per-chunk', default=DEFAULT_PAGES_PER_CHUNK, type=int,
              help=f'Number of pages to process per API call (default: {DEFAULT_PAGES_PER_CHUNK})')
@click.option('--vision/--no-vision', default=False,
              help='Enable vision mode for better layout/table/chart extraction (recommended)')
@click.option('--vision-dpi', default=DEFAULT_VISION_DPI, type=int,
              help=f'DPI for rendering page images in vision mode (default: {DEFAULT_VISION_DPI})')
@click.option('--vision-pages-per-chunk', default=None, type=int,
              help='Pages per chunk in vision mode (overrides --pages-per-chunk for vision mode)')
def convert(pdf_file, output_file, provider, model, api_key, pages_per_chunk, vision, vision_dpi, vision_pages_per_chunk):
    """Convert a single PDF file to markdown.

    PDF_FILE: Path to the PDF file to convert

    OUTPUT_FILE: Optional output path (defaults to same name with .md extension)

    Vision mode provides significantly better results for documents with complex layouts,
    tables, charts, or multi-column formats. It uses ~2-3x more tokens but delivers
    superior quality.
    """
    # Validate API key is available before processing
    is_valid, error_message = validate_api_key_available(provider.lower(), api_key)
    if not is_valid:
        click.echo(error_message, err=True)
        raise click.Abort()

    # Determine effective pages per chunk for vision mode
    effective_pages_per_chunk = pages_per_chunk
    if vision and vision_pages_per_chunk is not None:
        effective_pages_per_chunk = vision_pages_per_chunk

    convert_pdf_to_markdown(
        pdf_file,
        output_file,
        pages_per_chunk=effective_pages_per_chunk,
        provider=provider.lower(),
        api_key=api_key,
        model=model,
        use_vision=vision,
        vision_dpi=vision_dpi
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

        if not available_providers:
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
                    click.echo(f"{provider_name.title()}: {data.get('error', 'Not available')}\n")
                continue

            # Provider header
            provider_display = {
                'anthropic': 'Anthropic (Claude)',
                'openai': 'OpenAI (GPT)'
            }.get(provider_name, provider_name.title())

            click.echo(f"{provider_display}:")

            # List models
            default_model = data.get('default_model')
            models_list = data.get('models', [])

            if not models_list:
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
@click.option('--provider', default=DEFAULT_PROVIDER, type=click.Choice(['anthropic', 'openai'], case_sensitive=False),
              help=f'AI provider to use (default: {DEFAULT_PROVIDER})')
@click.option('--model', default=None, type=str,
              help='Model to use (optional, uses provider defaults if not specified)')
@click.option('--api-key', default=None, type=str,
              help='API key for the provider (optional, uses environment variable if not specified)')
@click.option('--pages-per-chunk', default=DEFAULT_PAGES_PER_CHUNK, type=int,
              help=f'Number of pages to process per API call (default: {DEFAULT_PAGES_PER_CHUNK})')
@click.option('--vision/--no-vision', default=False,
              help='Enable vision mode for better layout/table/chart extraction (recommended)')
@click.option('--vision-dpi', default=DEFAULT_VISION_DPI, type=int,
              help=f'DPI for rendering page images in vision mode (default: {DEFAULT_VISION_DPI})')
@click.option('--vision-pages-per-chunk', default=None, type=int,
              help='Pages per chunk in vision mode (overrides --pages-per-chunk for vision mode)')
def batch(input_folder, output_folder, provider, model, api_key, pages_per_chunk, vision, vision_dpi, vision_pages_per_chunk):
    """Convert all PDF files in a folder to markdown.

    INPUT_FOLDER: Folder containing PDF files

    OUTPUT_FOLDER: Optional output folder (defaults to same as input)

    Vision mode provides significantly better results for documents with complex layouts,
    tables, charts, or multi-column formats. It uses ~2-3x more tokens but delivers
    superior quality.
    """
    # Validate API key is available before processing
    is_valid, error_message = validate_api_key_available(provider.lower(), api_key)
    if not is_valid:
        click.echo(error_message, err=True)
        raise click.Abort()

    # Determine effective pages per chunk for vision mode
    effective_pages_per_chunk = pages_per_chunk
    if vision and vision_pages_per_chunk is not None:
        effective_pages_per_chunk = vision_pages_per_chunk

    batch_convert(
        input_folder,
        output_folder,
        pages_per_chunk=effective_pages_per_chunk,
        provider=provider.lower(),
        api_key=api_key,
        model=model,
        use_vision=vision,
        vision_dpi=vision_dpi
    )


if __name__ == "__main__":
    cli()
