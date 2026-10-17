#!/usr/bin/env bash
set -euo pipefail
/solution/reference_fix.sh
python3 - <<'PY'
from pathlib import Path
p=Path('/app/tickets/ACL-77.md'); s=p.read_text(); s=s.split('## Marcus Bell', 1)[0]; p.write_text(s, newline='\n')
PY
