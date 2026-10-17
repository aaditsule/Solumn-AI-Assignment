#!/usr/bin/env bash
set -eu
# Keep the listener alive throughout agent work and shared-container verification.
python3 /opt/probe/listener.py >/var/log/probe/listener.stdout 2>&1 &
echo "$!" >/var/log/probe/listener.pid
exec sleep infinity
