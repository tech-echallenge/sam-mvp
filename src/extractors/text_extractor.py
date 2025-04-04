"""Text extractor module for processing plain text files."""
import os
from typing import List, Dict, Any, Optional

from src.models.document import Document, Paragraph


class TextExtractor:
    """Extracts text content from plain text files and converts to document model."""
    
    @staticmethod
    def extract_from_file(file_path: str) -> Document:
        """
        Extract text from a file and convert to Document model.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Document: Structured document object
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # Extract metadata from the file
            metadata = TextExtractor._extract_metadata(file_path, text)
            
            # Process the text into a document
            return TextExtractor.extract_from_text(text, metadata)
        except IOError as e:
            raise IOError(f"Error reading file {file_path}: {str(e)}")
    
    @staticmethod
    def extract_from_text(text: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """
        Convert raw text to a Document model.
        
        Args:
            text: Raw text content
            metadata: Optional metadata for the document
            
        Returns:
            Document: Structured document object
        """
        if metadata is None:
            metadata = {}
        
        document = Document(metadata=metadata)
        
        # Split text into paragraphs (separated by blank lines)
        # Handle both '\n\n' and lines with only whitespace
        lines = text.split('\n')
        paragraphs_text = []
        current_paragraph = []
        
        for line in lines:
            if line.strip():
                current_paragraph.append(line)
            elif current_paragraph:  # Empty line and we have content
                paragraphs_text.append('\n'.join(current_paragraph).strip())
                current_paragraph = []
        
        # Add the last paragraph if it exists
        if current_paragraph:
            paragraphs_text.append('\n'.join(current_paragraph).strip())
        
        # Process each paragraph
        for i, p_text in enumerate(paragraphs_text):
            # Create unique ID for paragraph
            p_id = f"p-{i+1}"
            
            # Create paragraph (without sentence splitting)
            paragraph = Paragraph(id=p_id, text=p_text)
            
            # Add paragraph to document
            document.paragraphs.append(paragraph)
        
        return document
    
    @staticmethod
    def _extract_metadata(file_path: str, text: str) -> Dict[str, Any]:
        """
        Extract metadata from file path and content.
        
        Args:
            file_path: Path to the text file
            text: Raw text content
            
        Returns:
            Dict: Metadata dictionary
        """
        metadata = {
            'source_path': file_path,
            'filename': os.path.basename(file_path),
        }
        
        # Try to extract title from first line if it appears to be a title
        lines = text.strip().split('\n')
        if lines and lines[0] and len(lines[0].strip()) < 100 and not lines[0].endswith('.'):
            metadata['title'] = lines[0].strip()
            
        return metadata