#!/usr/bin/env bash
set -eu
# Fix the defect and then break the public API as a regression control.
bash /solution/reference_fix.sh
printf 'def latest_version(versions):\n    return "broken"\n' > /app/shipkit/versioning.py
