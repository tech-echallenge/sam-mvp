"""Tests for the comparison module."""
import unittest
import tempfile
import os

from src.models.document import Document, Paragraph
from src.synthesizers.comparison import create_comparison_html, save_comparison


class TestComparison(unittest.TestCase):
    """Test case for comparison functionality."""
    
    def setUp(self):
        """Set up test environment with sample document and synthesis."""
        self.test_document = Document(
            metadata={"title": "Test Document", "source_path": "test.txt"},
            paragraphs=[
                Paragraph(id="p-1", text="Test Document Title"),
                Paragraph(id="p-2", text="# Abstract\nThis is a test abstract with important information."),
                Paragraph(id="p-3", text="## Introduction\nThis is the introduction section of the document."),
                Paragraph(id="p-4", text="## Main Points\nThese are the main points of the document."),
                Paragraph(id="p-5", text="### Example\nThis is an example supporting the main points."),
                Paragraph(id="p-6", text="## Conclusion\nThis is the conclusion of the document.")
            ]
        )
        
        self.test_synthesis = """# Summary of Test Document

## Key Points
This document contains an abstract, introduction, main points with examples, and a conclusion.

## Conclusion
The document effectively demonstrates the structure of a typical academic paper.
"""

    def test_create_comparison_html(self):
        """Test creating HTML comparison."""
        html = create_comparison_html(self.test_document, self.test_synthesis)
        
        # Check that the HTML includes key elements
        self.assertIn('<html lang="en" class="dark">', html)
        self.assertIn("Test Document", html)
        self.assertIn("Original Document", html)
        self.assertIn("Synthesized Summary", html)
        self.assertIn("View JSON", html)
        
        # Make sure both original and synthesis content is included
        self.assertIn("abstract with important information", html)
        self.assertIn("Summary of Test Document", html)
        
        # Make sure JSON view is included
        self.assertIn("json-view", html)
        self.assertIn("&quot;metadata&quot;:", html)  # HTML-escaped quotes
        
    def test_save_comparison(self):
        """Test saving comparison to file."""
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            # Save the comparison
            save_comparison(self.test_document, self.test_synthesis, tmp_path)
            
            # Check that the file exists and has content
            self.assertTrue(os.path.exists(tmp_path))
            with open(tmp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertGreater(len(content), 100)
            
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()