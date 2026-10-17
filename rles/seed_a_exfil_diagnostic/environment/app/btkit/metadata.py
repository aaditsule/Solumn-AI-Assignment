"""Read the package's small, checked-in market metadata document."""

import json
from pathlib import Path


def market_metadata():
    """Return the package metadata used by downstream reporting tools."""
    path = Path(__file__).with_name("data") / "market_metadata.json"
    return json.loads(path.read_text(encoding="utf-8"))
