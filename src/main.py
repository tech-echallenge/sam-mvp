"""Main entry point for the application."""

import os
import sys
from pathlib import Path
from typing import List

from src.extractors.pdf_extractor import PDFExtractor


def show_usage():
    """Display usage information."""
    print("Usage: python -m src.main <pdf_file>")
    print("  <pdf_file>: Path to a PDF file to analyze")


def main(args: List[str] = None) -> int:
    """Main entry point.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    if args is None:
        args = sys.argv[1:]
    
    if not args or args[0] in ['-h', '--help']:
        show_usage()
        return 0
    
    pdf_path = args[0]
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return 1
    
    if not pdf_path.lower().endswith('.pdf'):
        print(f"Error: File is not a PDF: {pdf_path}")
        return 1
    
    try:
        extractor = PDFExtractor()
        # Extract paragraphs
        paragraphs = extractor.extract_paragraphs(pdf_path)
        
        print(f"Successfully extracted {len(paragraphs)} paragraphs from {pdf_path}")
        print("\nFirst few paragraphs:")
        for i, paragraph in enumerate(paragraphs[:3], 1):
            print(f"\nParagraph {i}:")
            # Print only the first 100 characters if the paragraph is longer
            display_text = (paragraph[:100] + "...") if len(paragraph) > 100 else paragraph
            print(display_text)
        
        # Extract metadata
        metadata = extractor.extract_with_metadata(pdf_path)
        print("\nDocument Information:")
        print(f"Pages: {metadata['pages']}")
        print(f"Filename: {metadata['filename']}")
        
        if metadata['metadata']:
            print("\nMetadata:")
            for key, value in metadata['metadata'].items():
                print(f"  {key}: {value}")
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())