"""Pytest configuration file."""

import sys
import os
from pathlib import Path

# Add the project root directory to the Python path
root_dir = str(Path(__file__).parent.absolute())
sys.path.insert(0, root_dir)