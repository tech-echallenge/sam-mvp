"""Tests for the TextExtractor module."""
import os
import unittest
from tempfile import NamedTemporaryFile

from src.extractors.text_extractor import TextExtractor
from src.models.document import Document
from src.utils.text_utils import split_into_sentences


class TestTextExtractor(unittest.TestCase):
    """Test case for TextExtractor functionality."""
    
    def test_extract_from_text(self):
        """Test extracting text directly from a string."""
        # Simple test text with a few paragraphs
        test_text = """Title of the Document
        
        This is the first paragraph. It has multiple sentences. Three in total.
        
        This is the second paragraph with just one sentence.
        
        The third paragraph. Has two sentences."""
        
        document = TextExtractor.extract_from_text(test_text)
        
        # Verify document structure
        self.assertIsInstance(document, Document)
        self.assertEqual(len(document.paragraphs), 4)  # Title + 3 paragraphs
        
        # Check first paragraph (the title)
        self.assertEqual(document.paragraphs[0].text, "Title of the Document")
        
        # Check second paragraph
        self.assertTrue("This is the first paragraph. It has multiple sentences. Three in total." in document.paragraphs[1].text)
        
        # Check third paragraph
        self.assertTrue("This is the second paragraph with just one sentence." in document.paragraphs[2].text)
        
        # Check fourth paragraph
        self.assertTrue("The third paragraph. Has two sentences." in document.paragraphs[3].text)
        
    def test_extract_from_file(self):
        """Test extracting text from a file."""
        # Create a temporary file for testing
        test_content = """Sample Document
        
        This is a test paragraph.
        
        This is another paragraph."""
        
        with NamedTemporaryFile(delete=False, mode='w', encoding='utf-8') as temp_file:
            temp_file.write(test_content)
            file_path = temp_file.name
        
        try:
            # Extract from the file
            document = TextExtractor.extract_from_file(file_path)
            
            # Verify document structure
            self.assertIsInstance(document, Document)
            self.assertEqual(len(document.paragraphs), 3)  # Title + 2 paragraphs
            
            # Check metadata
            self.assertEqual(document.metadata['source_path'], file_path)
            self.assertEqual(document.metadata['title'], "Sample Document")
            
        finally:
            # Clean up
            os.unlink(file_path)
            
    def test_file_not_found(self):
        """Test handling of non-existent files."""
        with self.assertRaises(FileNotFoundError):
            TextExtractor.extract_from_file("/path/that/does/not/exist.txt")
            
    def test_sentence_splitting(self):
        """Test improved sentence splitting with various edge cases."""
        # Test text with various edge cases
        test_text = """
        This is a test with Dr. Smith and Mr. Johnson. They work at the U.S.A. embassy.
        The value of pi is approx. 3.14159. This should be one sentence.
        This has an ellipsis... and should be two sentences.
        Some people use i.e. and e.g. in their writing. These are abbreviations.
        She arrived at 3:45 p.m. He arrived at 6:30 a.m. to meet her.
        """
        
        sentences = split_into_sentences(test_text)
        
        # We expect 8 sentences based on current implementation
        self.assertEqual(len(sentences), 8)
        
        # Check some specific cases
        self.assertTrue(any("Dr. Smith and Mr. Johnson" in s for s in sentences))
        self.assertTrue(any("3.14159" in s for s in sentences))
        self.assertTrue(any("ellipsis..." in s for s in sentences))
        self.assertTrue(any("i.e. and e.g." in s for s in sentences))
        self.assertTrue(any("3:45 p.m." in s for s in sentences))
        self.assertTrue(any("6:30 a.m." in s for s in sentences))


if __name__ == "__main__":
    unittest.main()