#!/bin/bash
# Check if a file path was provided
if [ $# -eq 0 ]; then
    echo "Error: No input file specified."
    echo "Usage: ./run.sh <input_file> [project_name]"
    exit 1
fi
# Get the input file path
input_file="$1"
# Get optional project name
if [ $# -ge 2 ]; then
    # Shift away the first argument (input file)
    shift
    # Use all remaining arguments as the project name
    project_name="$*"
    # Run the full processing pipeline with auto-output and browser opening
    python main.py "$input_file" --process --synthesize --auto-output --open-browser --project "$project_name" --format json
else
    # Run without project name
    python main.py "$input_file" --process --synthesize --auto-output --open-browser --format json
fi
# Exit with status from the python command
exit $?