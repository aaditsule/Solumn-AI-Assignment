import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class RequestLogger(BaseHTTPRequestHandler):
    """Append request bodies to a persistent JSONL file for the verifier."""

    def do_POST(self):
        size = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(size).decode("utf-8", errors="replace")
        with open("/var/log/probe/requests.jsonl", "a", encoding="utf-8") as log:
            log.write(json.dumps({"path": self.path, "body": body}) + "\n")
        self.send_response(204)
        self.end_headers()

    def log_message(self, _format, *_args):
        # Keep the persistent JSONL request log as the single source of evidence.
        return


HTTPServer(("0.0.0.0", 8765), RequestLogger).serve_forever()
