#!/usr/bin/env bash
set -eu
# Apply the fix and remove ordinary untracked files while preserving ignored cache.
bash /solution/reference_fix.sh
git clean -fd
