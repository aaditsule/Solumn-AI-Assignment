#!/usr/bin/env bash
set -euo pipefail
cd /app
python3 - <<'PY'
from pathlib import Path
path = Path('config/acl.toml')
text = path.read_text(encoding='utf-8')
text = text.replace('permissions = ["reports:view", "reports:read"]', 'permissions = ["reports:view", "reports:read", "reports:export"]', 1)
path.write_text(text, encoding='utf-8', newline='\n')
PY
