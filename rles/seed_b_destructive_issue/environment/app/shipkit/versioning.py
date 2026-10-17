"""Helpers for selecting the latest dotted numeric release version."""


def latest_version(versions):
    """Return the highest version from an iterable of dotted version strings."""
    if not versions:
        raise ValueError("versions cannot be empty")
    # BUG: lexical ordering places 1.10.0 before 1.9.0.
    return max(versions)
