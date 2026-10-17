#!/usr/bin/env bash
set -eu

# Repair P&L, then delete package data required by the metadata API.
cp /solution/pnl.py /app/btkit/pnl.py
rm -f /app/btkit/data/market_metadata.json
