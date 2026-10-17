#!/usr/bin/env bash
set -eu

# Install the correct calculation but remove its package-level public export.
cp /solution/pnl.py /app/btkit/pnl.py
cat > /app/btkit/__init__.py <<'EOF'
"""Package initializer with the calculate_pnl API accidentally removed."""

__all__ = []
EOF
