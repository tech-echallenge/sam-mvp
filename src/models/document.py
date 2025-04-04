"""Data models for the document structure."""

from enum import Enum
from typing import Dict, List, Optional, Any
import uuid


class StructuralTag(str, Enum):
    """Structural tags for paragraphs."""
    
    THESIS = "thesis"
    INTRODUCTION = "introduction"
    POINT = "point"
    EXAMPLE = "example"
    EVIDENCE = "evidence"
    COUNTERPOINT = "counterpoint"
    CONCLUSION = "conclusion"
    UNKNOWN = "unknown"


class ArgumentRole(str, Enum):
    """Argument roles for paragraphs."""
    
    SUPPORTING = "supporting"
    COUNTERPOINT = "counterpoint"
    ELABORATION = "elaboration"
    EVIDENCE = "evidence"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


class Sentence:
    """Represents a single sentence with its analysis."""
    
    def __init__(
        self,
        text: str,
        gist: Optional[str] = None,
        image_tag: Optional[str] = None,
        id: Optional[str] = None
    ):
        """Initialize a Sentence object.
        
        Args:
            text: The original sentence text
            gist: Simplified essence of the sentence
            image_tag: A visual concept tag for the sentence
            id: Unique identifier for the sentence
        """
        self.id = id or str(uuid.uuid4())
        self.text = text
        self.gist = gist
        self.image_tag = image_tag
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "text": self.text,
            "gist": self.gist,
            "image_tag": self.image_tag
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Sentence':
        """Create a Sentence from a dictionary."""
        return cls(
            text=data["text"],
            gist=data.get("gist"),
            image_tag=data.get("image_tag"),
            id=data.get("id")
        )


class Paragraph:
    """Represents a paragraph with its structural classification."""
    
    def __init__(
        self,
        text: str,
        structural_tag: StructuralTag = StructuralTag.UNKNOWN,
        argument_role: ArgumentRole = ArgumentRole.UNKNOWN,
        sentences: Optional[List[Sentence]] = None,
        id: Optional[str] = None
    ):
        """Initialize a Paragraph object.
        
        Args:
            text: The paragraph text
            structural_tag: Classification of paragraph in document structure
            argument_role: Role of paragraph in the argument
            sentences: List of sentences in the paragraph
            id: Unique identifier for the paragraph
        """
        self.id = id or str(uuid.uuid4())
        self.text = text
        self.structural_tag = structural_tag
        self.argument_role = argument_role
        self.sentences = sentences or []
    
    def add_sentence(self, sentence: Sentence) -> None:
        """Add a sentence to the paragraph."""
        self.sentences.append(sentence)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "text": self.text,
            "structural_tag": self.structural_tag.value,
            "argument_role": self.argument_role.value,
            "sentences": [s.to_dict() for s in self.sentences]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Paragraph':
        """Create a Paragraph from a dictionary."""
        paragraph = cls(
            text=data["text"],
            structural_tag=StructuralTag(data.get("structural_tag", StructuralTag.UNKNOWN.value)),
            argument_role=ArgumentRole(data.get("argument_role", ArgumentRole.UNKNOWN.value)),
            id=data.get("id")
        )
        
        for sentence_data in data.get("sentences", []):
            paragraph.add_sentence(Sentence.from_dict(sentence_data))
        
        return paragraph


class ArgumentPoint:
    """Represents a point in the argument tree."""
    
    def __init__(
        self,
        id: str,
        gist: str,
        supporting_points: Optional[List['ArgumentPoint']] = None,
        counter_points: Optional[List['ArgumentPoint']] = None,
        source_paragraph_id: Optional[str] = None
    ):
        """Initialize an ArgumentPoint object.
        
        Args:
            id: Unique identifier for the point
            gist: Simplified essence of the point
            supporting_points: List of supporting points
            counter_points: List of counterpoints
            source_paragraph_id: ID of the source paragraph
        """
        self.id = id
        self.gist = gist
        self.supporting_points = supporting_points or []
        self.counter_points = counter_points or []
        self.source_paragraph_id = source_paragraph_id
    
    def add_supporting_point(self, point: 'ArgumentPoint') -> None:
        """Add a supporting point."""
        self.supporting_points.append(point)
    
    def add_counter_point(self, point: 'ArgumentPoint') -> None:
        """Add a counter point."""
        self.counter_points.append(point)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "gist": self.gist,
            "supporting_points": [p.to_dict() for p in self.supporting_points],
            "counter_points": [p.to_dict() for p in self.counter_points],
            "source_paragraph_id": self.source_paragraph_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArgumentPoint':
        """Create an ArgumentPoint from a dictionary."""
        point = cls(
            id=data["id"],
            gist=data["gist"],
            source_paragraph_id=data.get("source_paragraph_id")
        )
        
        for sp_data in data.get("supporting_points", []):
            point.add_supporting_point(ArgumentPoint.from_dict(sp_data))
        
        for cp_data in data.get("counter_points", []):
            point.add_counter_point(ArgumentPoint.from_dict(cp_data))
        
        return point


class ArgumentTree:
    """Represents the hierarchical argument structure of a document."""
    
    def __init__(
        self,
        thesis: Optional[Dict[str, str]] = None,
        points: Optional[List[ArgumentPoint]] = None,
        conclusion: Optional[Dict[str, str]] = None
    ):
        """Initialize an ArgumentTree object.
        
        Args:
            thesis: The main thesis (argument/position)
            points: Key supporting points
            conclusion: The conclusion
        """
        self.thesis = thesis or {"id": str(uuid.uuid4()), "text": ""}
        self.points = points or []
        self.conclusion = conclusion or {"id": str(uuid.uuid4()), "text": ""}
    
    def add_point(self, point: ArgumentPoint) -> None:
        """Add a top-level point to the argument tree."""
        self.points.append(point)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "thesis": self.thesis,
            "points": [p.to_dict() for p in self.points],
            "conclusion": self.conclusion
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArgumentTree':
        """Create an ArgumentTree from a dictionary."""
        tree = cls(
            thesis=data.get("thesis"),
            conclusion=data.get("conclusion")
        )
        
        for point_data in data.get("points", []):
            tree.add_point(ArgumentPoint.from_dict(point_data))
        
        return tree


class Document:
    """Represents a full document with its structure."""
    
    def __init__(
        self,
        metadata: Dict[str, Any],
        paragraphs: Optional[List[Paragraph]] = None,
        argument_tree: Optional[ArgumentTree] = None
    ):
        """Initialize a Document object.
        
        Args:
            metadata: Document metadata
            paragraphs: List of paragraphs
            argument_tree: The argument tree structure
        """
        self.metadata = metadata
        self.paragraphs = paragraphs or []
        self.argument_tree = argument_tree or ArgumentTree()
    
    def add_paragraph(self, paragraph: Paragraph) -> None:
        """Add a paragraph to the document."""
        self.paragraphs.append(paragraph)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "metadata": self.metadata,
            "paragraphs": [p.to_dict() for p in self.paragraphs],
            "argument_tree": self.argument_tree.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create a Document from a dictionary."""
        doc = cls(metadata=data["metadata"])
        
        for paragraph_data in data.get("paragraphs", []):
            doc.add_paragraph(Paragraph.from_dict(paragraph_data))
        
        if "argument_tree" in data:
            doc.argument_tree = ArgumentTree.from_dict(data["argument_tree"])
        
        return doc