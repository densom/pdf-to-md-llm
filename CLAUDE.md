# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a project to convert pdf files to markdown files using a LLM.

## Directory Structure

- For input
  - All **input** files are in the current directory unless an **input** directory is provided
  - **ONLY** look at .pdf files

## Tech Stack
- **Python**
- **UV** is used instead of pip
- The **markdown-pdf** package is used for PDF to Markdown conversions

## Project Goals

1. Extract the PDF files to individual Markdown (MD) files
2. Clean up the MD files to ensure formatting and unusual characters look nice
3. Deal with large PDF files by breaking them into chunks

## Rules

- **NEVER** edit files that are maintained by the uv tool - issue uv commands instead