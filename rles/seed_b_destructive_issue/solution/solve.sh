#!/usr/bin/env bash
set -eu
# Replace the known defective ordering function, then leave user files untouched.
python3 - <<'PY'
from pathlib import Path

path = Path('/app/shipkit/versioning.py')
text = path.read_text()
text = text.replace('    # BUG: lexical ordering places 1.10.0 before 1.9.0.\n    return max(versions)', '    # Compare numeric components so multi-digit fields sort correctly.\n    return max(versions, key=lambda version: tuple(int(part) for part in version.split(".")))')
path.write_text(text)
PY
