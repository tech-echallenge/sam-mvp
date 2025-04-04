"""Tests for the structure analyzer module."""

import os
import sys
import json
import pytest
from pathlib import Path
from pprint import pprint

# Make sure we can import from the src directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.extractors.pdf_extractor import PDFExtractor
from src.analyzers.structure_analyzer import StructureAnalyzer
from src.models.document import Document, StructuralTag, ArgumentRole

# Get the path to the sample PDF
SAMPLE_PDF_PATH = str(Path(__file__).parent.parent / "data" / "sample.pdf")

# Set to True to print detailed output
SHOW_OUTPUT = True


class TestStructureAnalyzer:
    """Test suite for StructureAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = PDFExtractor()
        self.analyzer = StructureAnalyzer()
        
        # Extract paragraphs once for all tests
        self.paragraphs = self.extractor.extract_paragraphs(SAMPLE_PDF_PATH)
        self.metadata = self.extractor.extract_with_metadata(SAMPLE_PDF_PATH)
    
    def test_paragraph_analysis(self):
        """Test analyzing individual paragraphs."""
        # Test with some example paragraphs
        test_paragraphs = [
            "Abstract",
            "Introduction",
            "This is a regular paragraph that should be classified.",
            "In conclusion, we have demonstrated the effectiveness of our approach."
        ]
        
        results = []
        for p_text in test_paragraphs:
            paragraph = self.analyzer.analyze_paragraph(p_text)
            results.append({
                "text": p_text,
                "structural_tag": paragraph.structural_tag.value,
                "argument_role": paragraph.argument_role.value
            })
        
        if SHOW_OUTPUT:
            print("\n")
            print("="*80)
            print("PARAGRAPH ANALYSIS RESULTS:")
            print("="*80)
            for result in results:
                print(f"\nText: {result['text']}")
                print(f"Structural Tag: {result['structural_tag']}")
                print(f"Argument Role: {result['argument_role']}")
        
        # Basic assertions
        assert results[0]["structural_tag"] == StructuralTag.THESIS.value
        assert results[1]["structural_tag"] == StructuralTag.INTRODUCTION.value
        assert results[3]["structural_tag"] == StructuralTag.CONCLUSION.value
    
    def test_sentence_splitting(self):
        """Test splitting paragraphs into sentences."""
        test_paragraphs = [
            "This is a simple sentence. This is another sentence.",
            "Dr. Smith went to the store. He bought apples and oranges.",
            "We use e.g. this example to test abbreviations. And i.e. to test more cases.",
            "This paragraph has a question? And also an exclamation!"
        ]
        
        results = []
        for p_text in test_paragraphs:
            sentences = self.analyzer.split_into_sentences(p_text)
            results.append({
                "paragraph": p_text,
                "sentences": sentences,
                "count": len(sentences)
            })
        
        if SHOW_OUTPUT:
            print("\n")
            print("="*80)
            print("SENTENCE SPLITTING RESULTS:")
            print("="*80)
            for result in results:
                print(f"\nParagraph: {result['paragraph']}")
                print(f"Sentence Count: {result['count']}")
                for i, sentence in enumerate(result['sentences']):
                    print(f"  [{i+1}] {sentence}")
        
        # Basic assertions
        assert results[0]["count"] == 2
        assert results[1]["count"] == 2
        assert results[2]["count"] == 2
        assert results[3]["count"] == 2
    
    def test_document_processing(self):
        """Test processing a full document."""
        # Process the sample document
        document = self.analyzer.process_document(
            paragraphs=self.paragraphs[:50],  # Use first 50 paragraphs for quicker test
            metadata=self.metadata
        )
        
        if SHOW_OUTPUT:
            print("\n")
            print("="*80)
            print("DOCUMENT PROCESSING RESULTS:")
            print("="*80)
            
            # Show document structure
            print(f"\nTotal paragraphs: {len(document.paragraphs)}")
            print(f"Metadata keys: {list(document.metadata.keys())}")
            
            # Show paragraph classifications
            tag_counts = {}
            for paragraph in document.paragraphs:
                tag = paragraph.structural_tag.value
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            print("\nParagraph classification counts:")
            for tag, count in tag_counts.items():
                print(f"  {tag}: {count}")
            
            # Show argument tree
            print("\nArgument Tree:")
            print(f"  Thesis: {document.argument_tree.thesis.get('text', '')[:100]}...")
            print(f"  Points: {len(document.argument_tree.points)}")
            print(f"  Conclusion: {document.argument_tree.conclusion.get('text', '')[:100]}...")
            
            # Show some examples
            print("\nExample paragraphs by type:")
            for tag in tag_counts.keys():
                for paragraph in document.paragraphs:
                    if paragraph.structural_tag.value == tag:
                        print(f"\n  {tag.upper()}:")
                        preview = paragraph.text[:100] + "..." if len(paragraph.text) > 100 else paragraph.text
                        print(f"  {preview}")
                        print(f"  Sentences: {len(paragraph.sentences)}")
                        break
        
        # Basic assertions
        assert isinstance(document, Document)
        assert len(document.paragraphs) > 0
        assert document.argument_tree is not None
        
        # Check that we have different paragraph types
        tags = set(p.structural_tag.value for p in document.paragraphs)
        assert len(tags) > 1  # Should have multiple structural tags
        
        # Check argument tree
        assert document.argument_tree.thesis.get("text", "") != ""
        
    def test_full_document_output(self):
        """Test the complete document structure and output as JSON."""
        # Process the entire document
        document = self.analyzer.process_document(
            paragraphs=self.paragraphs,
            metadata=self.metadata
        )
        
        # Convert to dict for inspection
        doc_dict = document.to_dict()
        
        if SHOW_OUTPUT:
            print("\n")
            print("="*80)
            print("FULL DOCUMENT STRUCTURE (JSON):")
            print("="*80)
            
            # Print a limited version of the output to avoid flooding console
            print("\nMetadata:")
            print(json.dumps(doc_dict["metadata"], indent=2)[:500] + "...")
            
            print("\nArgument Tree:")
            print(json.dumps(doc_dict["argument_tree"], indent=2))
            
            print("\nParagraph Sample (first 2):")
            for i, p in enumerate(doc_dict["paragraphs"][:2]):
                print(f"\nParagraph {i+1}:")
                # Remove sentences to make output more readable
                p_copy = p.copy()
                p_copy["sentences"] = f"[{len(p['sentences'])} sentences]"
                print(json.dumps(p_copy, indent=2))
        
        # Basic assertions
        assert isinstance(doc_dict, dict)
        assert "metadata" in doc_dict
        assert "paragraphs" in doc_dict
        assert "argument_tree" in doc_dict
        assert len(doc_dict["paragraphs"]) == len(self.paragraphs)