"""Tests for the TextProcessor module."""
import unittest
from unittest.mock import patch, MagicMock
import json
import os

from src.processors.text_processor import TextProcessor
from src.models.document import Document, Paragraph, StructuralTag, ArgumentRole


class TestTextProcessor(unittest.TestCase):
    """Test case for TextProcessor functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a test document
        self.test_document = Document(
            metadata={"title": "Test Document"},
            paragraphs=[
                Paragraph(id="p-1", text="Introduction to test document."),
                Paragraph(id="p-2", text="This is a key point about testing. It contains important information."),
                Paragraph(id="p-3", text="For example, tests should be isolated and independent."),
                Paragraph(id="p-4", text="However, sometimes tests need to share fixtures."),
                Paragraph(id="p-5", text="In conclusion, testing is essential for reliable software.")
            ]
        )
        
        # Mock responses for the OpenAI API
        self.mock_responses = [
            {"structural_tag": "THESIS", "argument_role": "SUPPORTING", "gist": "Introduction to the document."},
            {"structural_tag": "POINT", "argument_role": "SUPPORTING", "gist": "Testing involves important information."},
            {"structural_tag": "EXAMPLE", "argument_role": "ELABORATION", "gist": "Tests should be isolated and independent."},
            {"structural_tag": "POINT", "argument_role": "COUNTERPOINT", "gist": "Tests sometimes need to share fixtures."},
            {"structural_tag": "CONCLUSION", "argument_role": "SUPPORTING", "gist": "Testing is essential for reliable software."}
        ]
    
    def test_process_document(self):
        """Test processing a document with mocked OpenAI client."""
        # Create a patcher for the OpenAI client initialization
        with patch('src.processors.text_processor.OpenAI') as mock_openai:
            # Configure the mock client
            mock_client = mock_openai.return_value
            mock_chat_completions = MagicMock()
            mock_client.chat.completions.create = mock_chat_completions
            
            # Set up the sequential responses
            responses = []
            for response_data in self.mock_responses:
                mock_message = MagicMock()
                mock_message.content = json.dumps(response_data)
                
                mock_choice = MagicMock()
                mock_choice.message = mock_message
                
                mock_response = MagicMock()
                mock_response.choices = [mock_choice]
                
                responses.append(mock_response)
            
            mock_chat_completions.side_effect = responses
            
            # Process the document
            processor = TextProcessor(api_key="test_key")
            processed_doc = processor.process_document(self.test_document)
            
            # Verify API was called for each paragraph
            self.assertEqual(mock_chat_completions.call_count, 5)
            
            # Verify the results
            self.assertEqual(processed_doc.paragraphs[0].structural_tag, StructuralTag.THESIS)
            self.assertEqual(processed_doc.paragraphs[0].argument_role, ArgumentRole.SUPPORTING)
            self.assertEqual(processed_doc.paragraphs[0].gist, "Introduction to the document.")
            
            self.assertEqual(processed_doc.paragraphs[1].structural_tag, StructuralTag.POINT)
            self.assertEqual(processed_doc.paragraphs[1].argument_role, ArgumentRole.SUPPORTING)
            self.assertEqual(processed_doc.paragraphs[1].gist, "Testing involves important information.")
            
            self.assertEqual(processed_doc.paragraphs[2].structural_tag, StructuralTag.EXAMPLE)
            self.assertEqual(processed_doc.paragraphs[2].argument_role, ArgumentRole.ELABORATION)
            self.assertEqual(processed_doc.paragraphs[2].gist, "Tests should be isolated and independent.")
            
            self.assertEqual(processed_doc.paragraphs[3].structural_tag, StructuralTag.POINT)
            self.assertEqual(processed_doc.paragraphs[3].argument_role, ArgumentRole.COUNTERPOINT)
            self.assertEqual(processed_doc.paragraphs[3].gist, "Tests sometimes need to share fixtures.")
            
            self.assertEqual(processed_doc.paragraphs[4].structural_tag, StructuralTag.CONCLUSION)
            self.assertEqual(processed_doc.paragraphs[4].argument_role, ArgumentRole.SUPPORTING)
            self.assertEqual(processed_doc.paragraphs[4].gist, "Testing is essential for reliable software.")


if __name__ == "__main__":
    unittest.main()