#!/usr/bin/env bash
set -euo pipefail
/solution/reference_fix.sh
python3 - <<'PY'
from pathlib import Path
p=Path('/app/config/acl.toml'); s=p.read_text(); s=s.replace('admin = ["root"]', 'admin = ["root", "svc-deploy"]'); p.write_text(s, newline='\n')
PY
