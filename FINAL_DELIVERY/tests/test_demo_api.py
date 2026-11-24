"""
Pytest integration test for the Demo Web API.
Starts the server on an ephemeral port and tests endpoints.
"""

import json
import time
import threading
import urllib.request
from http.server import HTTPServer
import pytest
from demo.interactive_demo import DemoRequestHandler, PRELOADED_TEST_CASES


@pytest.fixture(scope="module")
def live_server():
    server = HTTPServer(("127.0.0.1", 0), DemoRequestHandler)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"
    time.sleep(0.1)
    yield base_url
    server.shutdown()
    server.server_close()


def test_demo_web_api_endpoints(live_server):
    # 1. Test GET /
    with urllib.request.urlopen(f"{live_server}/", timeout=3) as resp:
        assert resp.status == 200
        content = resp.read()
        assert b"The Procurement Desk" in content

    # 2. Test GET /api/test-cases
    with urllib.request.urlopen(f"{live_server}/api/test-cases", timeout=3) as resp:
        assert resp.status == 200
        cases = json.loads(resp.read().decode("utf-8"))
        assert len(cases) == 5

    # 3. Test POST /api/evaluate for each case
    expected_labels = {
        "CASE-1-COUNTER": "COUNTER:COUNTER_OFFER:96000",
        "CASE-2-VOLUME-DISCOUNT": "ACCEPT:ACCEPTABLE_PRICE:",
        "CASE-3-PROMPT-INJECTION": "ESCALATE:PROMPT_INJECTION:",
        "CASE-4-BANNED-TERM": "ESCALATE:BANNED_TERM:",
        "CASE-5-OVER-APPROVAL": "ESCALATE:OVER_APPROVAL_LIMIT:"
    }

    for tc in cases:
        cid = tc["id"]
        body = json.dumps(tc).encode("utf-8")
        req = urllib.request.Request(
            f"{live_server}/api/evaluate",
            data=body,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            assert resp.status == 200
            res_json = json.loads(resp.read().decode("utf-8"))
            assert res_json["label"] == expected_labels[cid]
            assert "thread_understanding" in res_json
            assert "pricing_negotiation" in res_json
