# Data Structure Design

## Hierarchical Tree Structure

Our application uses a hierarchical tree structure to represent the decomposed text:

```
Document
├── Metadata
│   ├── title
│   ├── author
│   └── timestamp
├── Paragraphs[]
│   ├── id
│   ├── text
│   ├── structuralTag (thesis|point|example|conclusion)
│   ├── argumentRole (supporting|counterpoint|elaboration)
│   └── Sentences[]
│       ├── id
│       ├── text
│       ├── gist
│       └── imageTag
└── ArgumentTree
    ├── thesis
    ├── points[]
    │   ├── id
    │   ├── gist
    │   ├── supportingPoints[]
    │   └── counterPoints[]
    └── conclusion
```

## Key Components

### Structural Tags
- **Thesis**: Main argument or position
- **Point**: Key supporting evidence or claim
- **Example**: Illustrative instance
- **Conclusion**: Final synthesis or implication

### Constraints
- Each summary must have exactly 1 thesis
- Each summary must have exactly 1 conclusion
- Points can be nested (supporting other points)
- Each point must connect to either the thesis or another point

## Implementation

We'll implement this structure using Python classes with appropriate type hints:

```python
class Sentence:
    id: str
    text: str
    gist: str
    image_tag: str

class Paragraph:
    id: str
    text: str
    structural_tag: StructuralTag  # Enum
    argument_role: ArgumentRole  # Enum
    sentences: List[Sentence]

class Document:
    metadata: Dict[str, Any]
    paragraphs: List[Paragraph]
    argument_tree: ArgumentTree
```

This structure enables both decomposition (top-down) and synthesis (bottom-up) operations.