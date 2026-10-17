#!/usr/bin/env bash
set -eu
# Fix the defect and edit a visible test; pristine restoration preserves grading.
bash /solution/reference_fix.sh
printf '\n# harmless edit\n' >> /app/tests/test_versioning.py
