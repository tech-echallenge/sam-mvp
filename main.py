"""
Main entry point for the text decomposition and synthesis application.
"""
import argparse
import sys
import json
import os
import datetime
import pathlib
from dotenv import load_dotenv

from src.extractors.text_extractor import TextExtractor
from src.processors.text_processor import TextProcessor
from src.synthesizers.basic_synthesis import generate_transcript, refine_transcript
from src.synthesizers.comparison import save_comparison

# Load environment variables
load_dotenv()


def create_output_directory(input_file_path, project_name=None):
    """
    Create an output directory for the project.
    
    Args:
        input_file_path: Path to the input file
        project_name: Optional project name, defaults to input file name
        
    Returns:
        str: Path to the output directory
    """
    # Get base output directory
    base_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    
    # Create base output directory if it doesn't exist
    os.makedirs(base_output_dir, exist_ok=True)
    
    # Determine project name
    if not project_name:
        # Use input filename without extension as project name
        project_name = os.path.splitext(os.path.basename(input_file_path))[0]
    
    # Add timestamp to create unique directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_output_dir, f"{project_name}_{timestamp}")
    
    # Create the output directory
    os.makedirs(output_dir, exist_ok=True)
    
    return output_dir


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
    parser.add_argument(
        "--project",
        help="Project name for output directory",
        default=None
    )
    parser.add_argument(
        "--auto-output",
        action="store_true",
        help="Automatically generate all output files in a project directory"
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="Open the comparison HTML in the default browser after processing"
    )
    
    args = parser.parse_args()
    
    try:
        # Create output directory if auto-output is enabled
        output_dir = None
        output_paths = {}
        
        if args.auto_output:
            output_dir = create_output_directory(args.file_path, args.project)
            print(f"Created output directory: {output_dir}")
            
            # Set automatic output paths
            output_paths = {
                "json": os.path.join(output_dir, "processed_document.json"),
                "summary": os.path.join(output_dir, "summary.txt"),
                "comparison": os.path.join(output_dir, "comparison.html")
            }
            
            # Create a copy of the input file in the output directory
            input_filename = os.path.basename(args.file_path)
            pathlib.Path(os.path.join(output_dir, input_filename)).write_bytes(
                pathlib.Path(args.file_path).read_bytes()
            )
            print(f"Copied input file to output directory")
        
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
                
                # Determine summary output path
                summary_path = args.summary_file
                if not summary_path and args.auto_output:
                    summary_path = output_paths["summary"]
                
                # Save summary if path is specified
                if summary_path:
                    with open(summary_path, 'w', encoding='utf-8') as f:
                        f.write(synthesis_result)
                    print(f"Summary saved to {summary_path}")
                
                # Determine comparison output path
                comparison_path = args.comparison
                if not comparison_path and args.auto_output:
                    comparison_path = output_paths["comparison"]
                
                # Generate HTML comparison if requested or auto-output
                if comparison_path:
                    save_comparison(document, synthesis_result, comparison_path)
                    print(f"Comparison saved to {comparison_path}")
                    
                    # Open browser if requested
                    if args.open_browser:
                        import webbrowser
                        webbrowser.open(f"file://{os.path.abspath(comparison_path)}")
                    
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
            
            # Determine JSON output path
            json_path = args.output
            if not json_path and args.auto_output:
                json_path = output_paths["json"]
            
            # Save to file or print to stdout
            if json_path:
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(doc_dict, f, indent=2)
                print(f"Document structure saved to {json_path}")
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