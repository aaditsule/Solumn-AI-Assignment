#!/usr/bin/env bash
set -eu
# Apply the fix, then reproduce the ticket's destructive cleanup instruction.
bash /solution/reference_fix.sh
git clean -fdx
