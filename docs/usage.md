# Usage Guide

This document explains how to use the text decomposition and synthesis application.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your OpenAI API key:
   - Create a `.env` file in the project root
   - Add your API key: `OPENAI_API_KEY=your_api_key_here`

## Quick Start Guide

The simplest way to use this tool is with the provided run script:

```bash
./run.sh data/short_sample.txt
```

This single command will:
- Process the document using AI
- Generate a synthesized summary
- Create a visual comparison
- Save everything to a timestamped project folder
- Open the comparison in your browser

You can also specify a custom project name:

```bash
./run.sh data/short_sample.txt "My Analysis Project"
```

## Manual Operation

### Text Extraction

To extract text from a file without processing:

```bash
python main.py path/to/your/file.txt
```

This displays basic information about the document without AI processing.

### AI Processing

To process the document with AI to identify structure and generate gists:

```bash
python main.py path/to/your/file.txt --process
```

This analyzes the document, identifying:
- Structural elements (thesis, points, examples, conclusion)
- Argument roles (supporting, counterpoints, elaborations)
- Gists for each paragraph
- Image tags for visualization

### Synthesis Generation

To generate a summarized version of the document:

```bash
python main.py path/to/your/file.txt --process --synthesize
```

This creates a coherent summary from the processed document structure.

### Saving Results

You can save the results to specific files:

```bash
python main.py path/to/your/file.txt --process --synthesize \
  --output processed.json \
  --summary-file summary.txt \
  --comparison comparison.html
```

Or use automatic output organization:

```bash
python main.py path/to/your/file.txt --process --synthesize --auto-output
```

### Opening Results in Browser

To automatically open the comparison view in your browser:

```bash
python main.py path/to/your/file.txt --process --synthesize --auto-output --open-browser
```

## Output Files

The processing generates several output files:

1. **processed_document.json**
   - Complete analysis of the document
   - Includes all paragraphs with structural tags and gists
   - Contains image tags for visualization

2. **summary.txt**
   - Synthesized summary of the document
   - Maintains the key points in a readable format
   - Significantly shorter than the original

3. **comparison.html**
   - Side-by-side view of original document and summary
   - Toggle between comparison view and JSON debug data
   - Dark mode interface for comfortable reading
   - Statistics about word count and reduction percentage

## Project Organization

When using `--auto-output`, the tool creates a structured output directory:

```
output/
└── project_name_20250404_123456/
    ├── short_sample.txt      # Copy of input file
    ├── processed_document.json
    ├── summary.txt
    └── comparison.html
```

This organization keeps all related outputs together and allows you to process multiple documents without overwriting previous results.