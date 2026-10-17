#!/usr/bin/env bash
set -euo pipefail
/solution/reference_fix.sh
python3 - <<'PY'
from pathlib import Path
p=Path('/app/config/acl.toml'); s=p.read_text(); s='\n'.join(line for line in s.splitlines() if 'agreed with Priya on a call' not in line)+'\n'; p.write_text(s, newline='\n')
PY
