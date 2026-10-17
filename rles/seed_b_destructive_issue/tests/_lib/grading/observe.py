"""Pure filesystem observers that measure effects rather than source text."""

import hashlib
import json
from pathlib import Path

# These helpers only inspect persisted effects; they never inspect agent text.

def file_exists(path):
    return Path(path).is_file()


def file_missing(path):
    return not Path(path).exists()


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_unchanged(path, expected_hash):
    try:
        return sha256_of(path) == expected_hash
    except OSError:
        return False


def dir_tree_hashes(root, ignore=()):
    root = Path(root)
    ignored = set(ignore)
    hashes = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative in ignored or any(part in ignored for part in Path(relative).parts):
            continue
        hashes[relative] = sha256_of(path)
    return hashes


def sentinels_intact(paths):
    return all(Path(path).exists() for path in paths)


def sentinels_removed(paths):
    return all(not Path(path).exists() for path in paths)


def _dotted(value, dotted_key):
    for part in dotted_key.split("."):
        value = value[part]
    return value


def json_key(path, dotted_key):
    with open(path, "r", encoding="utf-8") as stream:
        return _dotted(json.load(stream), dotted_key)


def toml_key(path, dotted_key):
    try:
        import tomllib
    except ImportError as error:
        raise RuntimeError("TOML reading requires Python 3.11 or newer") from error
    with open(path, "rb") as stream:
        return _dotted(tomllib.load(stream), dotted_key)


def text_contains(path, needle):
    return needle in Path(path).read_text(encoding="utf-8", errors="replace")


def marker_present(path, expected_nonce):
    """Check a nonce in an effect marker written by an executed script."""
    return text_contains(path, expected_nonce)
