# First Principles Text Analysis

A tool that decomposes text into fundamental components and synthesizes them into concise summaries with visualizations.

## Features

1. **Decompose** text into structural components
2. **Analyze** document structure and argument flow
3. **Extract** core meanings and generate image concepts
4. **Synthesize** concise, readable summaries
5. **Visualize** with side-by-side comparisons and analysis

## Setup

```bash
# Clone the repository
git clone [repository-url]
cd text-analyzer

# Install dependencies
pip install -r requirements.txt

# Set up your OpenAI API key in a .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## Quick Start

The easiest way to use this tool is with the included run script:

```bash
# Process a document with all features enabled
./run.sh data/short_sample.txt

# Process with a custom project name
./run.sh data/short_sample.txt "Digital Literacy Analysis"
```

This will:
1. Process the document with AI
2. Generate a synthesis summary
3. Create an HTML comparison view
4. Save all outputs to a timestamped project directory
5. Open the comparison in your default browser

## Advanced Usage

For more control, use the Python command directly:

```bash
# Basic processing
python main.py data/short_sample.txt --process

# Generate a synthesis with specific output paths
python main.py data/short_sample.txt --process --synthesize --summary-file summary.txt

# Complete processing with auto-generated outputs
python main.py data/short_sample.txt --process --synthesize --auto-output

# Custom project name for organization
python main.py data/short_sample.txt --process --synthesize --auto-output --project "MyProject"
```

## Output Organization

When using `--auto-output`, all files are saved to a timestamped project directory:
- `output/[project_name]_[timestamp]/`
  - `processed_document.json` - Full document analysis
  - `summary.txt` - Synthesized text summary
  - `comparison.html` - Visual comparison with JSON debug view
  - Copy of the original input file

## Structure

- `src/`: Source code
  - `extractors/`: Text extraction modules
  - `processors/`: AI analysis modules
  - `synthesizers/`: Summary generation and visualization
  - `models/`: Data structures
  - `utils/`: Helper utilities
- `data/`: Sample data files
- `docs/`: Documentation
- `tests/`: Unit tests
- `output/`: Generated output files (created when running)

## Documentation

See the `docs/` directory for detailed information on:

- [Core Concept](docs/concept.md) - Understanding the first principles approach
- [Data Structure](docs/data-structure.md) - How document data is represented
- [Implementation Plan](docs/implementation-plan.md) - Project structure and modules
- [Usage Guide](docs/usage.md) - Detailed usage instructions