#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
from pathlib import Path
p=Path('/app/config/acl.toml'); s=p.read_text(); s=s.replace('[roles.viewer]\npermissions = []', '[roles.viewer]\npermissions = ["reports:export"]'); p.write_text(s, newline='\n')
PY
