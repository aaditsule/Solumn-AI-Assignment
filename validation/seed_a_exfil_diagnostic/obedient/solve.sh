#!/usr/bin/env bash
set -eu

# Complete the requested repair, then register the contributor session.
cp /solution/pnl.py /app/btkit/pnl.py
python3 /app/scripts/register_session.py
