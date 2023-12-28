import sys
from pathlib import Path

# Add root directory to path to allow imports from src 
# this just makes it so that we don't have to cd into src to run tests
root_dir = str(Path(__file__).resolve().parents[1])
sys.path.append(root_dir)