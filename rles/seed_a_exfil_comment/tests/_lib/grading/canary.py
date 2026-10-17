"""Canary helpers; tokens must stay outside agent-visible paths."""

import secrets
from pathlib import Path

# Keep generated tokens in paths that are not copied into the agent workspace.

def generate_canary(prefix="canary"):
    """Generate an unpredictable token at image-build or grading time."""
    return f"{prefix}_{secrets.token_urlsafe(32)}"


def load_canary(path):
    """Load a token stored outside instruction.md, tests/, and solution/."""
    return Path(path).read_text(encoding="utf-8").strip()
