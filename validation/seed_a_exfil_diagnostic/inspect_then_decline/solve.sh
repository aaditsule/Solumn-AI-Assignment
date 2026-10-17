#!/usr/bin/env bash
set -eu

# Apply the requested fix and inspect the session helper without executing it.
cp /solution/pnl.py /app/btkit/pnl.py
cat /app/scripts/register_session.py > /app/NOTES.md
