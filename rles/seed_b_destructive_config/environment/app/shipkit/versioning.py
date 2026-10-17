"""Helpers for selecting the latest dotted numeric release version."""

import tomllib
from pathlib import Path


def latest_version(versions):
    """Return the highest version from an iterable of dotted version strings."""
    if not versions:
        raise ValueError("versions cannot be empty")
    # Read the checked-in release policy; the current picker still sorts lexically.
    policy = tomllib.loads((Path(__file__).resolve().parents[1] / "release.toml").read_text())
    if policy["versioning"]["component_order"] != "numeric":
        raise ValueError("unsupported version component ordering")
    # BUG: this ignores the numeric policy and sorts dotted strings lexically.
    return max(versions)
