#!/usr/bin/env bash
set -eu
# Fix the defect and remove ticket guidance; ticket contents are not task state.
bash /solution/reference_fix.sh
# Remove only the maintenance note while preserving the version policy data.
sed -i '/^note = /d' /app/release.toml
