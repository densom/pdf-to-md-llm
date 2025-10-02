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
    DEFAULT_PAGES_PER_CHUNK
)

# Load environment variables from .env file
load_dotenv()


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """PDF to Markdown Converter (LLM-Assisted)

    Convert PDF documents to clean, well-structured Markdown using Claude API.
    """
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key == "your-api-key-here" or not api_key:
        click.echo("Error: Please set ANTHROPIC_API_KEY environment variable", err=True)
        click.echo("  export ANTHROPIC_API_KEY='your-key-here'", err=True)
        ctx.exit(1)

    # If no subcommand is provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument('pdf_file', type=click.Path(exists=True, dir_okay=False))
@click.argument('output_file', type=click.Path(), required=False)
@click.option('--pages-per-chunk', default=DEFAULT_PAGES_PER_CHUNK, type=int,
              help=f'Number of pages to process per API call (default: {DEFAULT_PAGES_PER_CHUNK})')
def convert(pdf_file, output_file, pages_per_chunk):
    """Convert a single PDF file to markdown.

    PDF_FILE: Path to the PDF file to convert

    OUTPUT_FILE: Optional output path (defaults to same name with .md extension)
    """
    convert_pdf_to_markdown(pdf_file, output_file, pages_per_chunk)


@cli.command()
@click.argument('input_folder', type=click.Path(exists=True, file_okay=False))
@click.argument('output_folder', type=click.Path(), required=False)
@click.option('--pages-per-chunk', default=DEFAULT_PAGES_PER_CHUNK, type=int,
              help=f'Number of pages to process per API call (default: {DEFAULT_PAGES_PER_CHUNK})')
def batch(input_folder, output_folder, pages_per_chunk):
    """Convert all PDF files in a folder to markdown.

    INPUT_FOLDER: Folder containing PDF files

    OUTPUT_FOLDER: Optional output folder (defaults to same as input)
    """
    batch_convert(input_folder, output_folder, pages_per_chunk)


if __name__ == "__main__":
    cli()
