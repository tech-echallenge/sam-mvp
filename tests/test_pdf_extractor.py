"""Tests for the PDF extractor module."""

import os
import sys
import json
import pytest
from pathlib import Path
from pprint import pprint

# Make sure we can import from the src directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.extractors.pdf_extractor import PDFExtractor


# Get the path to the sample PDF
SAMPLE_PDF_PATH = str(Path(__file__).parent.parent / "data" / "sample.pdf")


# Set to True to print detailed output of each extraction
SHOW_OUTPUT = True

class TestPDFExtractor:
    """Test suite for PDFExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = PDFExtractor()
    
    def test_pdf_exists(self):
        """Test that sample PDF file exists."""
        assert os.path.exists(SAMPLE_PDF_PATH), f"Sample PDF not found at {SAMPLE_PDF_PATH}"
    
    def test_extract_text(self):
        """Test basic text extraction."""
        text = self.extractor.extract_text(SAMPLE_PDF_PATH)
        
        # Output the extracted text
        if SHOW_OUTPUT:
            print("\n")
            print("="*80)
            print("EXTRACTED TEXT OUTPUT:")
            print("="*80)
            print(f"Text length: {len(text)} characters")
            print("Text preview:")
            preview_length = min(500, len(text))
            print(text[:preview_length] + ("..." if len(text) > preview_length else ""))
        
        # Basic validation that we got some text
        assert isinstance(text, str)
        assert len(text) > 0
        
        # Check that the extractor tracked the file
        assert self.extractor.last_extracted_file == SAMPLE_PDF_PATH
    
    def test_extract_structured_text(self):
        """Test structured text extraction."""
        structured_text = self.extractor.extract_structured_text(SAMPLE_PDF_PATH)
        
        # Output the structured text
        if SHOW_OUTPUT:
            print("\n")
            print("="*80)
            print("STRUCTURED TEXT OUTPUT (BY PAGE):")
            print("="*80)
            print(f"Number of pages: {len(structured_text)}")
            for page_num, text in structured_text.items():
                preview_length = min(200, len(text))
                print(f"\nPage {page_num} (preview):")
                print(text[:preview_length] + ("..." if len(text) > preview_length else ""))
        
        # Validate we got a dictionary with at least one page
        assert isinstance(structured_text, dict)
        assert len(structured_text) > 0
        
        # Validate page numbering starts at 1
        assert 1 in structured_text
        
        # Check that every page has some text
        for page_num, text in structured_text.items():
            assert isinstance(page_num, int)
            assert isinstance(text, str)
            assert len(text) > 0
    
    def test_extract_paragraphs(self):
        """Test paragraph extraction."""
        paragraphs = self.extractor.extract_paragraphs(SAMPLE_PDF_PATH)
        
        # Output the paragraphs
        if SHOW_OUTPUT:
            print("\n")
            print("="*80)
            print("PARAGRAPH EXTRACTION OUTPUT:")
            print("="*80)
            print(f"Number of paragraphs: {len(paragraphs)}")
            for i, paragraph in enumerate(paragraphs[:10]):  # Show first 10 paragraphs
                preview_length = min(150, len(paragraph))
                print(f"\nParagraph {i+1} (preview):")
                print(paragraph[:preview_length] + ("..." if len(paragraph) > preview_length else ""))
        
        # Validate we got a list of paragraphs
        assert isinstance(paragraphs, list)
        assert len(paragraphs) > 0
        
        # Check that each paragraph has text
        for paragraph in paragraphs:
            assert isinstance(paragraph, str)
            assert len(paragraph.strip()) > 0
    
    def test_extract_with_metadata(self):
        """Test extraction with metadata."""
        result = self.extractor.extract_with_metadata(SAMPLE_PDF_PATH)
        
        # Output the metadata
        if SHOW_OUTPUT:
            print("\n")
            print("="*80)
            print("METADATA EXTRACTION OUTPUT:")
            print("="*80)
            print("Complete result structure:")
            print(json.dumps({
                "text": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"],
                "metadata": result["metadata"],
                "pages": result["pages"],
                "filename": result["filename"]
            }, indent=2, default=str))
            
            print("\nData structure types:")
            print(f"- result: {type(result)}")
            print(f"- text: {type(result['text'])}, length: {len(result['text'])}")
            print(f"- metadata: {type(result['metadata'])}, keys: {list(result['metadata'].keys())}")
            print(f"- pages: {type(result['pages'])}, value: {result['pages']}")
            print(f"- filename: {type(result['filename'])}, value: {result['filename']}")
        
        # Validate the structure of the result
        assert isinstance(result, dict)
        assert "text" in result
        assert "metadata" in result
        assert "pages" in result
        assert "filename" in result
        
        # Validate basic data types
        assert isinstance(result["text"], str)
        assert isinstance(result["metadata"], dict)
        assert isinstance(result["pages"], int)
        assert isinstance(result["filename"], str)
        
        # Validate filename
        assert result["filename"] == "sample.pdf"
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.extractor.extract_text("nonexistent_file.pdf")
    
    def test_invalid_file_extension(self):
        """Test handling of invalid file extension."""
        # Create a temporary text file
        temp_file = "temp.txt"
        with open(temp_file, "w") as f:
            f.write("This is not a PDF file")
        
        try:
            with pytest.raises(ValueError):
                self.extractor.extract_text(temp_file)
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)