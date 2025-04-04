"""Structure analyzer for decomposing document paragraphs into a structured format."""

import re
from typing import Dict, List, Optional, Tuple, Any

from src.models.document import (
    Document, Paragraph, Sentence, ArgumentTree, ArgumentPoint,
    StructuralTag, ArgumentRole
)


class StructureAnalyzer:
    """Analyzes document structure and classifies paragraphs."""
    
    def __init__(self):
        """Initialize structure analyzer."""
        self.abstract_keywords = [
            "abstract", "summary", "overview", "synopsis"
        ]
        self.introduction_keywords = [
            "introduction", "background", "context"
        ]
        self.conclusion_keywords = [
            "conclusion", "summary", "in summary", "to summarize",
            "in conclusion", "to conclude", "finally"
        ]
        
        # Compile regex patterns for better performance
        self.abstract_pattern = re.compile(
            r"^(abstract|summary)[\s\n\:]*$", re.IGNORECASE
        )
        self.heading_pattern = re.compile(
            r"^([0-9]+\.?)+\s+\w+|^[A-Z][a-z]+(\s+[A-Z][a-z]+)*[\s\n\:]*$"
        )
    
    def process_document(self, paragraphs: List[str], metadata: Dict[str, Any]) -> Document:
        """Process a document to create a structured representation.
        
        Args:
            paragraphs: List of paragraph strings from the document
            metadata: Document metadata
            
        Returns:
            A structured Document object
        """
        # Create the base document
        document = Document(metadata=metadata)
        
        # Process paragraphs
        for paragraph_text in paragraphs:
            if not paragraph_text.strip():
                continue
                
            # Create paragraph and analyze its structure
            paragraph = self.analyze_paragraph(paragraph_text)
            document.add_paragraph(paragraph)
            
            # Break paragraph into sentences
            sentences = self.split_into_sentences(paragraph_text)
            for sentence_text in sentences:
                if sentence_text.strip():
                    sentence = Sentence(text=sentence_text)
                    paragraph.add_sentence(sentence)
        
        # Perform structural analysis
        self.analyze_document_structure(document)
        
        return document
    
    def analyze_paragraph(self, text: str) -> Paragraph:
        """Analyze a paragraph to determine its structural role.
        
        Args:
            text: The paragraph text
            
        Returns:
            A Paragraph object with structural_tag and argument_role set
        """
        # Initial classification with basic heuristics
        structural_tag = StructuralTag.UNKNOWN
        argument_role = ArgumentRole.UNKNOWN
        
        # Check if this is a heading
        if self.heading_pattern.match(text):
            # Just a simple initial tag
            structural_tag = StructuralTag.INTRODUCTION
        
        # Check for abstract marker
        if self.abstract_pattern.match(text):
            structural_tag = StructuralTag.THESIS
        
        # Check for introduction/background keywords
        if any(keyword in text.lower() for keyword in self.introduction_keywords):
            if len(text.split()) < 20:  # Short paragraph
                structural_tag = StructuralTag.INTRODUCTION
        
        # Check for conclusion keywords
        if any(keyword in text.lower() for keyword in self.conclusion_keywords):
            if len(text.split()) < 20:  # Short paragraph
                structural_tag = StructuralTag.CONCLUSION
        
        # Create the paragraph
        return Paragraph(
            text=text,
            structural_tag=structural_tag,
            argument_role=argument_role
        )
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split paragraph text into sentences.
        
        Args:
            text: The paragraph text
            
        Returns:
            List of sentence strings
        """
        # Basic sentence splitting (this can be improved)
        # Handle common abbreviations and edge cases
        text = text.replace("e.g.", "e_g_")
        text = text.replace("i.e.", "i_e_")
        text = text.replace("et al.", "et_al_")
        text = text.replace("vs.", "vs_")
        text = text.replace("Dr.", "Dr_")
        text = text.replace("Mr.", "Mr_")
        text = text.replace("Mrs.", "Mrs_")
        text = text.replace("Ms.", "Ms_")
        text = text.replace("Ph.D.", "PhD_")
        
        # Split by sentence terminators
        sentences = []
        for part in re.split(r'(?<=[.!?])\s+', text):
            if part.strip():
                # Restore abbreviations
                part = part.replace("e_g_", "e.g.")
                part = part.replace("i_e_", "i.e.")
                part = part.replace("et_al_", "et al.")
                part = part.replace("vs_", "vs.")
                part = part.replace("Dr_", "Dr.")
                part = part.replace("Mr_", "Mr.")
                part = part.replace("Mrs_", "Mrs.")
                part = part.replace("Ms_", "Ms.")
                part = part.replace("PhD_", "Ph.D.")
                sentences.append(part)
        
        # If no sentences were found, return the original text as a single sentence
        if not sentences:
            sentences = [text]
            
        return sentences
    
    def analyze_document_structure(self, document: Document) -> None:
        """Analyze the overall document structure.
        
        This method refines the initial structural tags and builds 
        relationships between paragraphs.
        
        Args:
            document: The Document object to analyze
            
        Returns:
            None (modifies document in place)
        """
        paragraphs = document.paragraphs
        
        # Identify abstract/introduction (typically at beginning)
        if paragraphs and paragraphs[0].structural_tag == StructuralTag.UNKNOWN:
            paragraphs[0].structural_tag = StructuralTag.INTRODUCTION
        
        # Look for conclusion at the end
        if len(paragraphs) > 2 and paragraphs[-1].structural_tag == StructuralTag.UNKNOWN:
            paragraphs[-1].structural_tag = StructuralTag.CONCLUSION
        
        # Basic thesis detection (look for abstract section)
        thesis_paragraph = None
        for i, paragraph in enumerate(paragraphs):
            # Check for explicit "Abstract" header
            if i > 0 and self.abstract_pattern.match(paragraphs[i-1].text):
                paragraph.structural_tag = StructuralTag.THESIS
                thesis_paragraph = paragraph
                break
                
            # Look for thesis statements in introduction
            if i < 3 and len(paragraph.text.split()) > 30:
                # Longer paragraphs at the beginning are often thesis paragraphs
                paragraph.structural_tag = StructuralTag.THESIS
                thesis_paragraph = paragraph
                break
        
        # Set remaining unknown paragraphs as points
        point_count = 0
        for paragraph in paragraphs:
            if paragraph.structural_tag == StructuralTag.UNKNOWN:
                if len(paragraph.text.split()) > 20:  # Substantial paragraph
                    paragraph.structural_tag = StructuralTag.POINT
                    point_count += 1
                else:
                    # Short paragraphs might be examples or evidence
                    paragraph.structural_tag = StructuralTag.EXAMPLE
        
        # Create initial argument tree
        self.build_argument_tree(document, thesis_paragraph)
    
    def build_argument_tree(self, document: Document, thesis_paragraph: Optional[Paragraph]) -> None:
        """Build the argument tree structure.
        
        Args:
            document: The Document object
            thesis_paragraph: The identified thesis paragraph or None
            
        Returns:
            None (modifies document in place)
        """
        # Create the argument tree
        argument_tree = ArgumentTree()
        
        # Set thesis
        if thesis_paragraph:
            # Extract first sentence as thesis summary
            thesis_text = thesis_paragraph.sentences[0].text if thesis_paragraph.sentences else thesis_paragraph.text
            argument_tree.thesis = {"id": thesis_paragraph.id, "text": thesis_text}
        
        # Find conclusion
        conclusion_paragraph = None
        for paragraph in reversed(document.paragraphs):
            if paragraph.structural_tag == StructuralTag.CONCLUSION:
                conclusion_paragraph = paragraph
                break
        
        if conclusion_paragraph:
            # Extract first sentence as conclusion summary
            conclusion_text = conclusion_paragraph.sentences[0].text if conclusion_paragraph.sentences else conclusion_paragraph.text
            argument_tree.conclusion = {"id": conclusion_paragraph.id, "text": conclusion_text}
        
        # Add points from point paragraphs
        for paragraph in document.paragraphs:
            if paragraph.structural_tag == StructuralTag.POINT:
                # Use first sentence as point summary
                point_text = paragraph.sentences[0].text if paragraph.sentences else paragraph.text
                point = {"id": paragraph.id, "gist": point_text[:100] + "..." if len(point_text) > 100 else point_text}
                
                # For simplicity, treat all points as top-level for now
                point_obj = ArgumentPoint(
                    id=paragraph.id,
                    gist=point_text[:100] + "..." if len(point_text) > 100 else point_text,
                    source_paragraph_id=paragraph.id
                )
                argument_tree.add_point(point_obj)
        
        # Assign the argument tree to the document
        document.argument_tree = argument_tree