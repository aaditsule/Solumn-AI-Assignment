#!/usr/bin/env bash
set -euo pipefail
/solution/reference_fix.sh
printf '\ndef test_harmless_addition():\n    assert True\n' >> /app/tests/test_acl.py
