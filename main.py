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
from src.synthesizers.basic_synthesis import generate_transcript, refine_transcript
from src.synthesizers.comparison import save_comparison

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
    parser.add_argument(
        "--synthesize",
        action="store_true",
        help="Generate a synthesized summary from the processed document"
    )
    parser.add_argument(
        "--summary-file",
        help="Path to save the synthesized summary",
        default=None
    )
    parser.add_argument(
        "--comparison",
        help="Path to save HTML comparison between original and summary",
        default=None
    )
    
    args = parser.parse_args()
    
    try:
        # Extract text from the file
        document = TextExtractor.extract_from_file(args.file_path)
        
        # Process with AI if requested
        processor = None
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
                    
        # Generate synthesis if requested
        synthesis_result = None
        if args.synthesize and args.process:  # Only synthesize if we've processed
            try:
                print("Generating synthesis...")
                
                # First generate the programmatic transcript
                transcript = generate_transcript(document)
                
                # Then refine it with AI if we have a processor available
                if processor:
                    synthesis_result = refine_transcript(transcript, processor.client)
                else:
                    synthesis_result = transcript
                    
                print("Synthesis complete")
                
                # Save to file if specified
                if args.summary_file:
                    with open(args.summary_file, 'w', encoding='utf-8') as f:
                        f.write(synthesis_result)
                    print(f"Summary saved to {args.summary_file}")
                
                # Generate HTML comparison if requested
                if args.comparison:
                    save_comparison(document, synthesis_result, args.comparison)
                    print(f"Comparison saved to {args.comparison}")
                    
            except Exception as e:
                print(f"Error during synthesis: {str(e)}", file=sys.stderr)
        
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
                    
                # Show a sample gist with sentences and image tags
                for p in document.paragraphs:
                    if p.gist and p.gist_sentences:
                        print("\nSample Gist:")
                        print(f"  Paragraph: {p.id}")
                        print(f"  Structural Tag: {p.structural_tag.name}")
                        print(f"  Argument Role: {p.argument_role.name}")
                        print(f"  Complete Gist: {p.gist}")
                        
                        print("\n  Gist Sentences with Image Tags:")
                        for i, sentence in enumerate(p.gist_sentences, 1):
                            print(f"  {i}. \"{sentence.text}\"")
                            print(f"     Image: {sentence.image_tag}")
                        break
            
            # Display synthesis if available
            if synthesis_result:
                print("\n\n--- Synthesized Summary ---\n")
                print(synthesis_result)
            
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
                        "word_count": len(p.text.split()),
                        # Add gist sentences with image tags
                        "gist_sentences": [
                            {
                                "text": s.text,
                                "image_tag": s.image_tag
                            } for s in p.gist_sentences
                        ]
                    } for p in document.paragraphs
                ]
            }
            
            # Add synthesis to JSON if available
            if synthesis_result:
                doc_dict["synthesis"] = synthesis_result
            
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