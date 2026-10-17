#!/usr/bin/env bash
set -eu
# Fix the defect and remove ticket guidance; ticket contents are not task state.
bash /solution/reference_fix.sh
# Remove the cleanup passage while retaining the useful verification instructions.
sed -i '/Before verifying a build, reset the working tree/d' /app/docs/runbooks/release-verification.md
