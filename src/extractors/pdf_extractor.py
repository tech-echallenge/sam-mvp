"""PDF extraction module for extracting text from PDF documents."""

from typing import Dict, List, Optional, Tuple
import os
from pathlib import Path
import PyPDF2
from io import StringIO

from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams


class PDFExtractor:
    """Extracts text and structure from PDF documents.
    
    This class provides methods to extract text from PDF files while preserving
    structural information like paragraphs and sections.
    """
    
    def __init__(self) -> None:
        """Initialize the PDF extractor."""
        self.last_extracted_file = None
    
    def extract_text(self, file_path: str) -> str:
        """Extract full text from a PDF document.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            The extracted text as a string
            
        Raises:
            FileNotFoundError: If the PDF file is not found
            ValueError: If the file is not a valid PDF
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"File is not a PDF: {file_path}")
        
        self.last_extracted_file = file_path
        
        # Using PyPDF2 for basic extraction
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n\n"
                    
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")
    
    def extract_structured_text(self, file_path: str) -> Dict[int, str]:
        """Extract text from PDF with page structure preserved.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary mapping page numbers (starting at 1) to page text
            
        Raises:
            FileNotFoundError: If the PDF file is not found
            ValueError: If the file is not a valid PDF
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"File is not a PDF: {file_path}")
        
        self.last_extracted_file = file_path
        
        # Using PyPDF2 for page-by-page extraction
        page_texts = {}
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)
                
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    page_texts[page_num + 1] = page.extract_text().strip()
                    
            return page_texts
        except Exception as e:
            raise ValueError(f"Error extracting structured text from PDF: {str(e)}")
    
    def extract_paragraphs(self, file_path: str) -> List[str]:
        """Extract paragraphs from PDF document.
        
        Uses more precise extraction with PDFMiner to better preserve paragraph breaks.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of paragraphs
            
        Raises:
            FileNotFoundError: If the PDF file is not found
            ValueError: If the file is not a valid PDF
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"File is not a PDF: {file_path}")
        
        self.last_extracted_file = file_path
        
        # Using PDFMiner for more accurate paragraph extraction
        output = StringIO()
        with open(file_path, 'rb') as file:
            extract_text_to_fp(file, output, laparams=LAParams())
            text = output.getvalue()
        
        # Split by double newlines to get paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return paragraphs
    
    def extract_with_metadata(self, file_path: str) -> Dict:
        """Extract text with metadata from PDF.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary with text content and metadata
            
        Raises:
            FileNotFoundError: If the PDF file is not found
            ValueError: If the file is not a valid PDF
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"File is not a PDF: {file_path}")
        
        self.last_extracted_file = file_path
        
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Extract text
                text = ""
                num_pages = len(reader.pages)
                for page_num in range(num_pages):
                    text += reader.pages[page_num].extract_text() + "\n\n"
                
                # Extract metadata
                metadata = {}
                info = reader.metadata
                if info:
                    for key in info:
                        metadata[key[1:]] = info[key]  # Remove the leading '/'
                
                return {
                    "text": text.strip(),
                    "metadata": metadata,
                    "pages": num_pages,
                    "filename": Path(file_path).name
                }
        except Exception as e:
            raise ValueError(f"Error extracting PDF with metadata: {str(e)}")