#!/usr/bin/env bash
set -eu

# Replace only the defective P&L module; leave tests and private runtime files intact.
cp /solution/pnl.py /app/btkit/pnl.py
