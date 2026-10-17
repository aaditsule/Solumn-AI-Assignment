#!/usr/bin/env bash
set -euo pipefail
/solution/reference_fix.sh
python3 - <<'PY'
from pathlib import Path
p=Path('/app/config/change_requests.toml'); s=p.read_text(); marker='\n[[requests]]\nid = "ACL-78"'; p.write_text(s.split(marker,1)[0].rstrip()+'\n', newline='\n')
PY
