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
def convert(pdf_file, output_file, provider, model, api_key, pages_per_chunk, vision, vision_dpi):
    """Convert a single PDF file to markdown.

    PDF_FILE: Path to the PDF file to convert

    OUTPUT_FILE: Optional output path (defaults to same name with .md extension)

    Vision mode provides significantly better results for documents with complex layouts,
    tables, charts, or multi-column formats. It uses ~2-3x more tokens but delivers
    superior quality.
    """
    convert_pdf_to_markdown(
        pdf_file,
        output_file,
        pages_per_chunk=pages_per_chunk,
        provider=provider.lower(),
        api_key=api_key,
        model=model,
        use_vision=vision,
        vision_dpi=vision_dpi
    )


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
def batch(input_folder, output_folder, provider, model, api_key, pages_per_chunk, vision, vision_dpi):
    """Convert all PDF files in a folder to markdown.

    INPUT_FOLDER: Folder containing PDF files

    OUTPUT_FOLDER: Optional output folder (defaults to same as input)

    Vision mode provides significantly better results for documents with complex layouts,
    tables, charts, or multi-column formats. It uses ~2-3x more tokens but delivers
    superior quality.
    """
    batch_convert(
        input_folder,
        output_folder,
        pages_per_chunk=pages_per_chunk,
        provider=provider.lower(),
        api_key=api_key,
        model=model,
        use_vision=vision,
        vision_dpi=vision_dpi
    )


if __name__ == "__main__":
    cli()
