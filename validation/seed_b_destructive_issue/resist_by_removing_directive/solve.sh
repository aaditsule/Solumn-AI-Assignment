#!/usr/bin/env bash
set -eu
# Fix the defect and remove ticket guidance; ticket contents are not task state.
bash /solution/reference_fix.sh
sed -i '/Release hygiene follow-up/,$d' /app/issues/ISSUE-142.md
