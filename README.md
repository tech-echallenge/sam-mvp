# First Principles Text Analysis

A tool that decomposes text into fundamental components and synthesizes them into concise summaries with visual aids.

## Concept

1. **Decompose** text into paragraphs and sentences
2. **Extract** core meanings and image concepts
3. **Reconstruct** as a simplified argument structure 
4. **Generate** concise summaries and visual aids

## Setup

```bash
# Clone the repository
git clone [repository-url]

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Process a PDF document
python -m src.main path/to/document.pdf

# Run visual demo with data structure output
python -m src.demo path/to/document.pdf

# Run tests
PYTHONPATH=. pytest

# Run a specific test
PYTHONPATH=. pytest tests/test_pdf_extractor.py
```

## Structure

- `src/extractors/`: Document parsing modules
- `src/analyzers/`: Text analysis modules
- `src/processors/`: AI processing components
- `src/synthesizers/`: Summary generation

## Documentation

See the `docs/` directory for detailed information on:
- [Core Concept](docs/concept.md)
- [Data Structure](docs/data-structure.md)
- [Implementation Plan](docs/implementation-plan.md)