import sys
from pathlib import Path

# Make the repo root importable when pytest is run from any directory.
sys.path.insert(0, str(Path(__file__).parent.parent))
