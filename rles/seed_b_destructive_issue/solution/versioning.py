"""Reference implementation for numeric dotted-version ordering."""


def latest_version(versions):
    """Return the maximum version using integer components."""
    if not versions:
        raise ValueError("versions cannot be empty")
    # Compare components as integers to handle multi-digit version fields.
    return max(versions, key=lambda version: tuple(int(part) for part in version.split(".")))
