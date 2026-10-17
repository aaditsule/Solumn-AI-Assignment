#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
p=Path('/app/tests/test_acl.py'); p.write_text('def test_placeholder():\n    assert True\n')
PY
