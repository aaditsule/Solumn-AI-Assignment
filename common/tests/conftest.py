"""Make the source package importable during host-side tests."""

import sys
from pathlib import Path

# Tests exercise the authoritative source tree, not any vendored copy.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
