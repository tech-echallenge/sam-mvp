"""
Main entry point for the text decomposition and synthesis application.
"""
import argparse
import sys
import json
import os
from dotenv import load_dotenv

from src.extractors.text_extractor import TextExtractor
from src.processors.text_processor import TextProcessor

# Load environment variables
load_dotenv()


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Process text documents for decomposition and synthesis"
    )
    parser.add_argument(
        "file_path", 
        help="Path to the text file to process"
    )
    parser.add_argument(
        "--output", 
        help="Path to save the output document structure (JSON format)",
        default=None
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="summary",
        help="Output format (default: summary)"
    )
    parser.add_argument(
        "--process",
        action="store_true",
        help="Process document with AI to analyze structure and generate gists"
    )
    
    args = parser.parse_args()
    
    try:
        # Extract text from the file
        document = TextExtractor.extract_from_file(args.file_path)
        
        # Process with AI if requested
        if args.process:
            try:
                print("Processing document with AI... (this may take a while)")
                processor = TextProcessor()
                document = processor.process_document(document)
                print("AI processing complete")
            except Exception as e:
                print(f"Error during AI processing: {str(e)}", file=sys.stderr)
                if not args.output:  # Only exit if not saving output
                    sys.exit(1)
        
        # Display information about the document
        if args.format == "summary":
            print(f"Document: {document.metadata.get('title', 'Untitled')}")
            print(f"Source: {document.metadata.get('source_path')}")
            print(f"Paragraphs: {len(document.paragraphs)}")
            print(f"Total characters: {sum(len(p.text) for p in document.paragraphs)}")
            
            # If document was processed, show some stats
            if args.process:
                # Count paragraphs by structural tag
                tag_counts = {}
                for p in document.paragraphs:
                    tag = p.structural_tag.name
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
                
                print("\nStructural Analysis:")
                for tag, count in tag_counts.items():
                    print(f"  {tag}: {count} paragraphs")
                    
                # Show a sample gist
                for p in document.paragraphs:
                    if p.gist:
                        print("\nSample Gist:")
                        print(f"  Paragraph: {p.id}")
                        print(f"  Structural Tag: {p.structural_tag.name}")
                        print(f"  Argument Role: {p.argument_role.name}")
                        print(f"  Gist: {p.gist}")
                        break
            
        elif args.format == "json":
            # Convert document to JSON
            doc_dict = {
                "metadata": document.metadata,
                "paragraphs": [
                    {
                        "id": p.id,
                        "text": p.text,
                        "structural_tag": p.structural_tag.name,
                        "argument_role": p.argument_role.name,
                        "gist": p.gist,
                        # Add word count as additional metadata
                        "word_count": len(p.text.split())
                    } for p in document.paragraphs
                ]
            }
            
            # Save to file or print to stdout
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(doc_dict, f, indent=2)
                print(f"Document structure saved to {args.output}")
            else:
                print(json.dumps(doc_dict, indent=2))
                
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()