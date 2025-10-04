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
    DEFAULT_PROVIDER
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
def convert(pdf_file, output_file, provider, model, api_key, pages_per_chunk):
    """Convert a single PDF file to markdown.

    PDF_FILE: Path to the PDF file to convert

    OUTPUT_FILE: Optional output path (defaults to same name with .md extension)
    """
    convert_pdf_to_markdown(
        pdf_file,
        output_file,
        pages_per_chunk=pages_per_chunk,
        provider=provider.lower(),
        api_key=api_key,
        model=model
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
def batch(input_folder, output_folder, provider, model, api_key, pages_per_chunk):
    """Convert all PDF files in a folder to markdown.

    INPUT_FOLDER: Folder containing PDF files

    OUTPUT_FOLDER: Optional output folder (defaults to same as input)
    """
    batch_convert(
        input_folder,
        output_folder,
        pages_per_chunk=pages_per_chunk,
        provider=provider.lower(),
        api_key=api_key,
        model=model
    )


if __name__ == "__main__":
    cli()
