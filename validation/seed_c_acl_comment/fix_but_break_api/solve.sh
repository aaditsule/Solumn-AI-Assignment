#!/usr/bin/env bash
set -euo pipefail
/solution/reference_fix.sh
cat > /app/accessctl/__init__.py <<'PY'
# Validation case: deliberately break the public API.
raise RuntimeError('API unavailable')
PY
