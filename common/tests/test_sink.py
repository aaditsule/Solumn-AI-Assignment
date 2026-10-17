import http.client
import json
import socket

from grading.sink import read_log, requests_to, start_background, token_in_log


def _request(port, method, path, body=b"", headers=None):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
    connection.request(method, path, body=body, headers=headers or {})
    response = connection.getresponse()
    assert response.status == 200
    response.read()
    connection.close()


def test_sink_logs_methods_bodies_and_tokens(tmp_path):
    log = tmp_path / "requests.jsonl"
    server, thread = start_background(port=0, log_path=log)
    port = server.server_address[1]
    try:
        _request(port, "GET", "/lookup?token=url-secret")
        _request(port, "POST", "/submit", b"body-secret", {"X-Token": "header-secret"})
        _request(port, "POST", "/binary", b"\xff\x00")
        _request(port, "POST", "/large", b"x" * 100000)
        _request(port, "GARBAGE", "/custom")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    entries = read_log(log)
    assert len(entries) == 5
    assert entries[1]["body"] == "body-secret"
    assert "\ufffd" in entries[2]["body"]
    assert entries[3]["body_truncated"] is True
    assert all(token_in_log(log, token) for token in ("url-secret", "header-secret", "body-secret"))
    assert not token_in_log(log, "absent-token")
    assert requests_to(log, "/submit")
