#!/usr/bin/env bash
set -eu
# Apply the fix and preview cleanup candidates without deleting them.
bash /solution/reference_fix.sh
git clean -n
