"""Main entry point for the application."""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

from src.extractors.pdf_extractor import PDFExtractor
from src.analyzers.structure_analyzer import StructureAnalyzer


def show_usage():
    """Display usage information."""
    print("Usage: python -m src.main <pdf_file> [options]")
    print("  <pdf_file>: Path to a PDF file to analyze")
    print("\nOptions:")
    print("  --full-output: Show full document structure")
    print("  --extract-only: Only extract text, don't analyze structure")
    print("  --save <file>: Save structured output to a JSON file")


def print_structure_summary(doc_dict: Dict[str, Any]) -> None:
    """Print a summary of the document structure.
    
    Args:
        doc_dict: Document dictionary representation
    """
    print("\n" + "="*80)
    print("DOCUMENT STRUCTURE SUMMARY")
    print("="*80)
    
    # Metadata summary
    print("\nDocument Metadata:")
    if "Title" in doc_dict["metadata"].get("metadata", {}):
        print(f"  Title: {doc_dict['metadata']['metadata']['Title']}")
    if "Author" in doc_dict["metadata"].get("metadata", {}):
        print(f"  Author: {doc_dict['metadata']['metadata']['Author']}")
    print(f"  Pages: {doc_dict['metadata'].get('pages', 'Unknown')}")
    
    # Paragraph classification counts
    tag_counts = {}
    for paragraph in doc_dict["paragraphs"]:
        tag = paragraph["structural_tag"]
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    print("\nParagraph Classification:")
    for tag, count in tag_counts.items():
        print(f"  {tag.capitalize()}: {count} paragraphs")
    
    # Argument tree summary
    print("\nArgument Structure:")
    
    # Thesis
    thesis_text = doc_dict["argument_tree"]["thesis"].get("text", "")
    if thesis_text:
        print(f"  Thesis: {thesis_text[:100]}..." if len(thesis_text) > 100 else f"  Thesis: {thesis_text}")
    
    # Points summary
    points = doc_dict["argument_tree"]["points"]
    print(f"  Main Points: {len(points)}")
    
    # Sample of points
    if points:
        print("\nSample Points:")
        for i, point in enumerate(points[:3]):  # Show first 3 points
            print(f"  Point {i+1}: {point['gist']}")
        if len(points) > 3:
            print(f"  ... and {len(points) - 3} more points")
    
    # Conclusion
    conclusion_text = doc_dict["argument_tree"]["conclusion"].get("text", "")
    if conclusion_text:
        print(f"\nConclusion: {conclusion_text[:100]}..." if len(conclusion_text) > 100 else f"\nConclusion: {conclusion_text}")


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
    
    # Parse arguments
    pdf_path = args[0]
    show_full_output = "--full-output" in args
    extract_only = "--extract-only" in args
    save_file = None
    
    if "--save" in args:
        save_index = args.index("--save")
        if save_index + 1 < len(args):
            save_file = args[save_index + 1]
    
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return 1
    
    if not pdf_path.lower().endswith('.pdf'):
        print(f"Error: File is not a PDF: {pdf_path}")
        return 1
    
    try:
        print(f"\nProcessing: {pdf_path}")
        
        # Extract text and metadata
        extractor = PDFExtractor()
        paragraphs = extractor.extract_paragraphs(pdf_path)
        metadata = extractor.extract_with_metadata(pdf_path)
        
        print(f"Extracted {len(paragraphs)} paragraphs from {metadata['pages']} pages")
        
        # If extract-only flag is set, just show extraction results
        if extract_only:
            print("\n" + "="*80)
            print("TEXT EXTRACTION RESULTS")
            print("="*80)
            
            print("\nFirst few paragraphs:")
            for i, paragraph in enumerate(paragraphs[:5], 1):
                print(f"\nParagraph {i}:")
                # Print only the first 100 characters if the paragraph is longer
                display_text = (paragraph[:100] + "...") if len(paragraph) > 100 else paragraph
                print(display_text)
            
            print("\nDocument Information:")
            print(f"Pages: {metadata['pages']}")
            print(f"Filename: {metadata['filename']}")
            
            if metadata['metadata']:
                print("\nMetadata:")
                for key, value in list(metadata['metadata'].items())[:10]:  # Show first 10 metadata items
                    print(f"  {key}: {value}")
                if len(metadata['metadata']) > 10:
                    print(f"  ... and {len(metadata['metadata']) - 10} more metadata items")
            
            return 0
        
        # Analyze the document structure
        print("Analyzing document structure...")
        analyzer = StructureAnalyzer()
        document = analyzer.process_document(paragraphs, metadata)
        
        # Convert to dictionary for output
        doc_dict = document.to_dict()
        
        # Print summary or full output
        if show_full_output:
            print("\n" + "="*80)
            print("FULL DOCUMENT STRUCTURE")
            print("="*80)
            
            # For full output, we limit the sentences to avoid flooding the console
            simplified_doc = doc_dict.copy()
            for paragraph in simplified_doc["paragraphs"]:
                sentence_count = len(paragraph["sentences"])
                paragraph["sentences"] = f"[{sentence_count} sentences]"
            
            print(json.dumps(simplified_doc, indent=2))
        else:
            print_structure_summary(doc_dict)
        
        # Save to file if requested
        if save_file:
            with open(save_file, 'w') as f:
                json.dump(doc_dict, f, indent=2)
            print(f"\nDocument structure saved to: {save_file}")
        
        return 0
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())