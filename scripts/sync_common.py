#!/usr/bin/env python3
"""Vendor the shared grader package into each existing RLE test tree."""

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "common" / "grading"
RLES = ROOT / "rles"


def _files(directory):
    # Only package source belongs in the vendored library; omit interpreter caches.
    return {path.relative_to(directory).as_posix(): path for path in directory.rglob("*.py") if path.is_file()}


def sync_environment(name, check=False):
    """Copy source files as bytes, preserving the source's LF line endings."""
    destination = RLES / name / "tests" / "_lib" / "grading"
    expected = _files(SOURCE)
    actual = _files(destination) if destination.exists() else {}
    mismatches = sorted(
        path for path, source in expected.items()
        if path not in actual or not filecmp.cmp(source, actual[path], shallow=False)
    )
    extras = sorted(set(actual) - set(expected))
    if check:
        if mismatches or extras:
            print(f"{name}: MISMATCH (different/missing={mismatches}, extra={extras})")
            return False
        print(f"{name}: up to date")
        return True

    destination.mkdir(parents=True, exist_ok=True)
    for relative, source in expected.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    for relative in extras:
        (destination / relative).unlink()
    print(f"{name}: synced {len(expected)} files to {destination.relative_to(RLES.parent).as_posix()}")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("environments", nargs="*", help="environment directory names under rles/")
    parser.add_argument("--check", action="store_true", help="report drift without modifying copies")
    arguments = parser.parse_args(argv)
    names = arguments.environments or sorted(path.name for path in RLES.iterdir() if path.is_dir())
    missing = [name for name in names if not (RLES / name).is_dir()]
    if missing:
        parser.error("unknown environment(s): " + ", ".join(missing))
    statuses = [sync_environment(name, check=arguments.check) for name in names]
    return 0 if all(statuses) else 1


if __name__ == "__main__":
    sys.exit(main())
