"""Unit tests for converter.py module - tests chunking logic and PDF extraction."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from pdf_to_md_llm.converter import (
    chunk_pages,
    chunk_vision_pages,
    extract_text_from_pdf,
    extract_pages_with_vision,
    convert_pdf_to_markdown,
    batch_convert,
)


class TestChunkPages:
    """Test the chunk_pages function."""

    def test_chunk_pages_basic(self):
        """Test basic chunking of pages."""
        pages = ["Page 1", "Page 2", "Page 3", "Page 4", "Page 5"]
        chunks = chunk_pages(pages, pages_per_chunk=2)

        assert len(chunks) == 3
        assert chunks[0] == "Page 1\n\nPage 2"
        assert chunks[1] == "Page 3\n\nPage 4"
        assert chunks[2] == "Page 5"

    def test_chunk_pages_single_page(self):
        """Test chunking with single page per chunk."""
        pages = ["Page 1", "Page 2", "Page 3"]
        chunks = chunk_pages(pages, pages_per_chunk=1)

        assert len(chunks) == 3
        assert chunks[0] == "Page 1"
        assert chunks[1] == "Page 2"
        assert chunks[2] == "Page 3"

    def test_chunk_pages_all_in_one(self):
        """Test chunking all pages into one chunk."""
        pages = ["Page 1", "Page 2", "Page 3"]
        chunks = chunk_pages(pages, pages_per_chunk=10)

        assert len(chunks) == 1
        assert chunks[0] == "Page 1\n\nPage 2\n\nPage 3"

    def test_chunk_pages_empty_list(self):
        """Test chunking with empty page list."""
        pages = []
        chunks = chunk_pages(pages, pages_per_chunk=2)

        assert len(chunks) == 0


class TestChunkVisionPages:
    """Test the chunk_vision_pages function."""

    def test_chunk_vision_pages_no_overlap(self):
        """Test vision page chunking without overlap."""
        pages = [
            {"page_number": 1, "text": "Page 1", "image": "img1"},
            {"page_number": 2, "text": "Page 2", "image": "img2"},
            {"page_number": 3, "text": "Page 3", "image": "img3"},
            {"page_number": 4, "text": "Page 4", "image": "img4"},
        ]
        chunks = chunk_vision_pages(pages, pages_per_chunk=2, overlap=0)

        assert len(chunks) == 2
        assert len(chunks[0]) == 2
        assert len(chunks[1]) == 2
        assert chunks[0][0]["page_number"] == 1
        assert chunks[1][0]["page_number"] == 3

    def test_chunk_vision_pages_with_overlap(self):
        """Test vision page chunking with overlap."""
        pages = [
            {"page_number": 1, "text": "Page 1", "image": "img1"},
            {"page_number": 2, "text": "Page 2", "image": "img2"},
            {"page_number": 3, "text": "Page 3", "image": "img3"},
            {"page_number": 4, "text": "Page 4", "image": "img4"},
        ]
        chunks = chunk_vision_pages(pages, pages_per_chunk=2, overlap=1)

        # With overlap of 1: chunks should be [1,2], [2,3], [3,4]
        assert len(chunks) == 3
        assert chunks[0][0]["page_number"] == 1
        assert chunks[0][1]["page_number"] == 2
        assert chunks[1][0]["page_number"] == 2
        assert chunks[1][1]["page_number"] == 3
        assert chunks[2][0]["page_number"] == 3
        assert chunks[2][1]["page_number"] == 4

    def test_chunk_vision_pages_single_page(self):
        """Test vision page chunking with single page."""
        pages = [{"page_number": 1, "text": "Page 1", "image": "img1"}]
        chunks = chunk_vision_pages(pages, pages_per_chunk=2, overlap=0)

        assert len(chunks) == 1
        assert len(chunks[0]) == 1

    def test_chunk_vision_pages_empty_list(self):
        """Test vision page chunking with empty list."""
        pages = []
        chunks = chunk_vision_pages(pages, pages_per_chunk=2, overlap=0)

        assert len(chunks) == 0


class TestExtractTextFromPDF:
    """Test the extract_text_from_pdf function with mocked PyMuPDF."""

    @patch('pymupdf.open')
    def test_extract_text_from_pdf_basic(self, mock_pymupdf_open):
        """Test basic text extraction from PDF."""
        # Mock PDF document with 3 pages
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Page 1 text"
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Page 2 text"
        mock_page3 = MagicMock()
        mock_page3.get_text.return_value = "Page 3 text"

        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 3
        mock_doc.__getitem__.side_effect = [mock_page1, mock_page2, mock_page3]
        mock_pymupdf_open.return_value = mock_doc

        pages = extract_text_from_pdf("dummy.pdf")

        assert len(pages) == 3
        assert pages[0] == "Page 1 text"
        assert pages[1] == "Page 2 text"
        assert pages[2] == "Page 3 text"
        mock_pymupdf_open.assert_called_once_with("dummy.pdf")

    @patch('pymupdf.open')
    def test_extract_text_from_pdf_empty_pages(self, mock_pymupdf_open):
        """Test extraction from PDF with empty pages."""
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = ""
        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Some text"

        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 2
        mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
        mock_pymupdf_open.return_value = mock_doc

        pages = extract_text_from_pdf("dummy.pdf")

        assert len(pages) == 2
        assert pages[0] == ""
        assert pages[1] == "Some text"


class TestExtractPagesWithVision:
    """Test the extract_pages_with_vision function with mocked PyMuPDF."""

    @patch('pymupdf.open')
    @patch('base64.b64encode')
    def test_extract_pages_with_vision_basic(self, mock_base64_encode, mock_pymupdf_open):
        """Test basic vision extraction from PDF."""
        # Mock base64 encoding
        mock_base64_encode.return_value = b'encoded_image_data'

        # Mock PDF document
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Page 1 text"
        mock_page.get_images.return_value = []  # No embedded images
        mock_pixmap = MagicMock()
        mock_pixmap.tobytes.return_value = b'image_bytes'
        mock_page.get_pixmap.return_value = mock_pixmap

        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_doc.__getitem__.return_value = mock_page
        mock_pymupdf_open.return_value = mock_doc

        pages = extract_pages_with_vision("dummy.pdf", dpi=150)

        assert len(pages) == 1
        assert pages[0]["page_num"] == 0  # 0-indexed
        assert pages[0]["text"] == "Page 1 text"
        assert pages[0]["image_base64"] == "encoded_image_data"
        mock_page.get_pixmap.assert_called_once()


class TestConvertPdfToMarkdown:
    """Test the convert_pdf_to_markdown function with mocked dependencies."""

    @patch('pdf_to_md_llm.converter.extract_text_from_pdf')
    @patch('pdf_to_md_llm.converter.chunk_pages')
    @patch('pdf_to_md_llm.converter.get_provider')
    @patch('builtins.open', new_callable=MagicMock)
    def test_convert_pdf_to_markdown_text_mode(self, mock_open, mock_get_provider, mock_chunk_pages, mock_extract_text):
        """Test PDF to markdown conversion in text mode."""
        # Setup mocks
        mock_extract_text.return_value = ["Page 1", "Page 2"]
        mock_chunk_pages.return_value = ["Page 1\nPage 2"]

        # Mock provider
        mock_provider = Mock()
        mock_provider.convert_to_markdown.return_value = "# Converted Markdown"
        mock_get_provider.return_value = mock_provider

        # Mock file writing to prevent test.md creation
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Call function (without vision)
        result = convert_pdf_to_markdown(
            pdf_path="test.pdf",
            output_path=None,
            pages_per_chunk=5,
            provider="anthropic",
            api_key="test_key",
            max_tokens=4096,
            use_vision=False,
        )

        # Result should include header and converted markdown
        assert "# Converted Markdown" in result
        assert "Converted from PDF" in result
        mock_extract_text.assert_called_once_with("test.pdf")
        mock_chunk_pages.assert_called_once()
        mock_provider.convert_to_markdown.assert_called_once()
        # Verify file was opened for writing
        mock_open.assert_called_once_with("test.md", "w", encoding="utf-8")

    @patch('pdf_to_md_llm.converter.extract_pages_with_vision')
    @patch('pdf_to_md_llm.converter.chunk_vision_pages')
    @patch('pdf_to_md_llm.converter.get_provider')
    @patch('builtins.open', new_callable=MagicMock)
    def test_convert_pdf_to_markdown_vision_mode(self, mock_open, mock_get_provider, mock_chunk_vision, mock_extract_vision):
        """Test PDF to markdown conversion in vision mode."""
        # Setup mocks
        mock_extract_vision.return_value = [
            {"page_num": 0, "text": "Page 1", "image_base64": "img1", "has_images": False, "has_tables": False},
        ]
        mock_chunk_vision.return_value = [
            [{"page_num": 0, "text": "Page 1", "image_base64": "img1", "has_images": False, "has_tables": False}]
        ]

        # Mock provider
        mock_provider = Mock()
        mock_provider.convert_to_markdown_vision.return_value = "# Vision Markdown"
        mock_get_provider.return_value = mock_provider

        # Mock file writing to prevent test.md creation
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Call function (with vision)
        result = convert_pdf_to_markdown(
            pdf_path="test.pdf",
            output_path=None,
            pages_per_chunk=5,
            provider="anthropic",
            api_key="test_key",
            max_tokens=4096,
            use_vision=True,
            vision_dpi=150,
        )

        # Result should include header and converted markdown
        assert "# Vision Markdown" in result
        assert "Converted from PDF" in result
        mock_extract_vision.assert_called_once()
        mock_provider.convert_to_markdown_vision.assert_called_once()
        # Verify file was opened for writing
        mock_open.assert_called_once_with("test.md", "w", encoding="utf-8")

    @patch('pdf_to_md_llm.converter.extract_text_from_pdf')
    @patch('pdf_to_md_llm.converter.chunk_pages')
    @patch('pdf_to_md_llm.converter.get_provider')
    @patch('builtins.open', new_callable=MagicMock)
    def test_convert_pdf_to_markdown_saves_to_file(self, mock_open, mock_get_provider, mock_chunk_pages, mock_extract_text):
        """Test that conversion saves to output file when specified."""
        # Setup mocks
        mock_extract_text.return_value = ["Page 1"]
        mock_chunk_pages.return_value = ["Page 1"]

        mock_provider = Mock()
        mock_provider.convert_to_markdown.return_value = "# Markdown Output"
        mock_get_provider.return_value = mock_provider

        # Mock file writing
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Call function with output path
        result = convert_pdf_to_markdown(
            pdf_path="test.pdf",
            output_path="output.md",
            pages_per_chunk=5,
            provider="anthropic",
            api_key="test_key",
            max_tokens=4096,
            use_vision=False,
        )

        # Result should include header and converted markdown
        assert "# Markdown Output" in result
        assert "Converted from PDF" in result
        mock_open.assert_called_once_with("output.md", "w", encoding="utf-8")
        # The write should include the full output with header
        write_call = mock_file.write.call_args[0][0]
        assert "# Markdown Output" in write_call
        assert "Converted from PDF" in write_call


class TestBatchConvert:
    """Test the batch_convert function with mocked dependencies."""

    @patch('pdf_to_md_llm.converter.convert_pdf_to_markdown')
    @patch('pdf_to_md_llm.converter.Path')
    def test_batch_convert_basic(self, mock_path_class, mock_convert):
        """Test basic batch conversion."""
        # Mock input folder with 2 PDF files
        mock_input_folder = MagicMock()
        mock_pdf1 = MagicMock()
        mock_pdf1.suffix = ".pdf"
        mock_pdf1.name = "file1.pdf"
        mock_pdf2 = MagicMock()
        mock_pdf2.suffix = ".pdf"
        mock_pdf2.name = "file2.pdf"
        mock_input_folder.glob.return_value = [mock_pdf1, mock_pdf2]

        # Mock output folder
        mock_output_folder = MagicMock()

        mock_path_class.side_effect = lambda x: mock_input_folder if "input" in x else mock_output_folder

        # Call batch_convert (with threads=1 to avoid threading complexity)
        batch_convert(
            input_folder="input",
            output_folder="output",
            pages_per_chunk=5,
            provider="anthropic",
            api_key="test_key",
            max_tokens=4096,
            use_vision=False,
            threads=1,
        )

        # Verify convert_pdf_to_markdown was called for each PDF
        assert mock_convert.call_count == 2
