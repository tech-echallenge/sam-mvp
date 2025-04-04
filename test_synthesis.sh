#!/bin/bash

# Command to process the document, generate synthesis, create comparison and save the results
python main.py data/short_sample.txt --process --synthesize --summary-file summary.txt --comparison comparison.html --format json --output processed_with_synthesis.json