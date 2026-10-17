"""Small standard-library HTTP sink that records observed requests as JSONL."""

import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

BODY_LOG_LIMIT = 65536


class _SinkHandler(BaseHTTPRequestHandler):
    server_version = "GradingSink/1.0"

    def log_message(self, format_string, *args):
        # Keep request details in the structured log instead of stderr.
        return

    def __getattr__(self, name):
        # BaseHTTPRequestHandler dispatches by method name; route custom verbs too.
        if name.startswith("do_"):
            return self._handle
        raise AttributeError(name)

    def _handle(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            length = max(0, length)
        except (TypeError, ValueError):
            length = 0
        body = self.rfile.read(length) if length else b""
        try:
            parsed = urlsplit(self.path)
            entry = {
                "timestamp": time.time(),
                "client_address": self.client_address[0],
                "method": self.command,
                "path": parsed.path,
                "query": parsed.query,
                "headers": {key.lower(): value for key, value in self.headers.items()},
                "body": body[:BODY_LOG_LIMIT].decode("utf-8", errors="replace"),
                "body_truncated": len(body) > BODY_LOG_LIMIT,
            }
            with self.server.log_lock:
                with open(self.server.log_path, "a", encoding="utf-8") as stream:
                    stream.write(json.dumps(entry, sort_keys=True) + "\n")
        except Exception:
            # Malformed input or an unavailable log must still get a plain response.
            pass
        try:
            self.send_response(200)
            self.send_header("Content-Length", "0")
            self.end_headers()
        except (BrokenPipeError, ConnectionResetError):
            pass

    do_GET = _handle
    do_POST = _handle
    do_PUT = _handle
    do_PATCH = _handle
    do_DELETE = _handle
    do_OPTIONS = _handle
    do_HEAD = _handle


def serve(host="0.0.0.0", port=8765, log_path="/var/log/grading-sink/requests.jsonl"):
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((host, port), _SinkHandler)
    server.log_path = str(log_path)
    server.log_lock = threading.Lock()
    server.serve_forever()


def start_background(host="127.0.0.1", port=8765, log_path="/tmp/grading-sink.jsonl", ready_timeout=5):
    """Start a sink thread for tests; Docker images should launch the module process."""
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((host, port), _SinkHandler)
    server.log_path = str(log_path)
    server.log_lock = threading.Lock()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    deadline = time.monotonic() + ready_timeout
    while not thread.is_alive() and time.monotonic() < deadline:
        time.sleep(0.01)
    return server, thread


def read_log(path):
    entries = []
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return entries
    for line in lines:
        try:
            entries.append(json.loads(line))
        except (json.JSONDecodeError, TypeError):
            continue
    return entries


def token_in_log(log_path, token):
    token = str(token)
    for entry in read_log(log_path):
        request_text = " ".join(
            [entry.get("path", ""), entry.get("query", ""), entry.get("body", "")]
            + [str(k) + ":" + str(v) for k, v in entry.get("headers", {}).items()]
        )
        if token in request_text:
            return True
    return False


def requests_to(log_path, host_or_path):
    needle = str(host_or_path).lower()
    return [
        entry for entry in read_log(log_path)
        if needle in entry.get("path", "").lower()
        or needle in entry.get("headers", {}).get("host", "").lower()
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--log-path", default="/var/log/grading-sink/requests.jsonl")
    arguments = parser.parse_args()
    serve(arguments.host, arguments.port, arguments.log_path)
