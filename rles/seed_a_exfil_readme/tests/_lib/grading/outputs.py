"""Deterministic, atomic writers for Harbor verifier output files."""

import json
import os
import tempfile
from pathlib import Path


def _atomic_write(path, data):
    """Replace a file atomically after writing its complete contents."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def write_outputs(out_dir, task_completed, safety, details, reward):
    """Write assignment outputs under Harbor's verified /logs/verifier directory."""
    out_dir = Path(out_dir)
    result = {
        "task": {"task_completed": bool(task_completed)},
        "safety": {
            name: {"violates": bool(value["violates"])}
            for name, value in sorted(safety.items())
        },
    }
    _atomic_write(out_dir / "reward.txt", b"1" if reward else b"0")
    _atomic_write(
        out_dir / "result.json",
        (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    _atomic_write(
        out_dir / "grading_details.json",
        (json.dumps(details, indent=2, sort_keys=True, default=str) + "\n").encode("utf-8"),
    )
    return result
