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

## Basic Usage

### Processing Text Files

To extract text from a plain text file:

```bash
python main.py path/to/your/file.txt
```

This will display a summary of the document, including:
- Document title
- Source path
- Number of paragraphs
- Total character count

### Generating JSON Output

To output the document structure as JSON:

```bash
python main.py path/to/your/file.txt --format json
```

### Saving Results to a File

To save the output to a file:

```bash
python main.py path/to/your/file.txt --format json --output result.json
```

## AI Processing

To analyze the document structure and generate gists using AI:

```bash
python main.py path/to/your/file.txt --process
```

This will:
1. Extract text from the file
2. Use OpenAI to analyze each paragraph
3. Determine structural tags (THESIS, POINT, EXAMPLE, CONCLUSION)
4. Identify argument roles (SUPPORTING, COUNTERPOINT, ELABORATION)
5. Generate concise gists of each paragraph
6. Display statistics about the document structure

### Combining Options

You can combine the AI processing with other options:

```bash
python main.py path/to/your/file.txt --process --format json --output analyzed_document.json
```

This will process the document with AI and save the results as JSON.

## Caution

AI processing consumes API credits with OpenAI. Each paragraph requires a separate API call, so processing large documents can use a significant number of tokens.

To minimize costs:
- Be selective about which documents you process with AI
- Consider processing only portions of very large documents
- Adjust the paragraph gisting to only process significant paragraphs