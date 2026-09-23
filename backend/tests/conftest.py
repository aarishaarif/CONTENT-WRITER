# conftest.py — makes the backend/ directory importable from tests/
import sys
import os

# Add the backend directory to sys.path so `import main` works
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
