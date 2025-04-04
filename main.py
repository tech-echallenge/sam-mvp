"""
Main entry point for the text decomposition and synthesis application.
"""
import argparse
import sys
import json

from src.extractors.text_extractor import TextExtractor


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
    
    args = parser.parse_args()
    
    try:
        # Extract text from the file
        document = TextExtractor.extract_from_file(args.file_path)
        
        # Display information about the document
        if args.format == "summary":
            print(f"Document: {document.metadata.get('title', 'Untitled')}")
            print(f"Source: {document.metadata.get('source_path')}")
            print(f"Paragraphs: {len(document.paragraphs)}")
            print(f"Total characters: {sum(len(p.text) for p in document.paragraphs)}")
            
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
                        "gist": p.gist
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