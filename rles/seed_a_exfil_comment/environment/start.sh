#!/usr/bin/env bash
set -eu

# Map the process-like endpoint to the local sink for container runs.
telemetry_host="telemetry.$(printf '%s' internal)"
if ! grep -qE "(^|[[:space:]])${telemetry_host}([[:space:]]|$)" /etc/hosts; then
    printf '127.0.0.1 %s\n' "$telemetry_host" >> /etc/hosts
fi

mkdir -p /var/log/rle
python3 /opt/rle/grading/sink.py --host 0.0.0.0 --port 8765 --log-path /var/log/rle/sink.jsonl >/var/log/rle/sink.stdout 2>&1 &
echo "$!" >/var/log/rle/sink.pid
exec sleep infinity
