"""Data models for representing document structure."""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Any, Optional


class StructuralTag(Enum):
    """Tags for identifying paragraph structure within a document."""
    THESIS = auto()
    POINT = auto()
    EXAMPLE = auto()
    CONCLUSION = auto()
    UNKNOWN = auto()


class ArgumentRole(Enum):
    """Tags for identifying a paragraph's role in the argument."""
    SUPPORTING = auto()
    COUNTERPOINT = auto()
    ELABORATION = auto()
    UNKNOWN = auto()


@dataclass
class Sentence:
    """Represents a single sentence with its extracted information."""
    id: str
    text: str
    gist: str = ""
    image_tag: str = ""


@dataclass
class Paragraph:
    """Represents a paragraph with its metadata."""
    id: str
    text: str
    structural_tag: StructuralTag = StructuralTag.UNKNOWN
    argument_role: ArgumentRole = ArgumentRole.UNKNOWN
    gist: str = ""


@dataclass
class Document:
    """Represents a document with its paragraphs and metadata."""
    metadata: Dict[str, Any] = field(default_factory=dict)
    paragraphs: List[Paragraph] = field(default_factory=list)