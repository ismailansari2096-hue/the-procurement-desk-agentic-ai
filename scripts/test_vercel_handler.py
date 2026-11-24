"""
Test api/index.py handler directly to verify Vercel serverless compatibility.
Tests both direct paths and Vercel-rewritten paths (query params & headers).
"""

import sys
import json
import io
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "src"))

from api.index import handler
from demo.interactive_demo import PRELOADED_TEST_CASES


class MockSocket:
    def __init__(self, data_bytes=b""):
        self.rfile = io.BytesIO(data_bytes)
        self.wfile = io.BytesIO()

    def makefile(self, mode, *args, **kwargs):
        if "r" in mode:
            return self.rfile
        return self.wfile

    def sendall(self, b):
        self.wfile.write(b)


def test_handler():
    print("=" * 65)
    print("TESTING API/INDEX.PY VERCEL HANDLER COMPATIBILITY")
    print("=" * 65)

    # 1. Test GET / (both direct and rewritten)
    for path in ["/", "/api/index", "/api/index?path=/"]:
        print(f"\n[TEST 1] Testing GET {path} (HTML Dashboard)...")
        req_data = f"GET {path} HTTP/1.1\r\nHost: localhost\r\n\r\n".encode("utf-8")
        sock = MockSocket(req_data)
        h = handler(sock, ("127.0.0.1", 12345), None)
        output = sock.wfile.getvalue().decode("utf-8", errors="ignore")
        assert "200 OK" in output, f"Expected 200 OK for {path}, got:\n{output[:200]}"
        assert "The Procurement Desk" in output, "Expected Dashboard title in HTML"
        assert "V4 Model • Kaggle Public Score: 1.00000" in output, "Expected V4 badge in HTML"
        assert "Public Leaderboard Score — Private Score Pending" in output, "Expected disclosure in HTML"
        print(f"  GET {path} -> 200 OK with verified V4 dashboard HTML!")

    # 2. Test GET /api/test-cases (both direct and rewritten)
    for path in ["/api/test-cases", "/api/index?path=/api/test-cases"]:
        print(f"\n[TEST 2] Testing GET {path}...")
        req_data = f"GET {path} HTTP/1.1\r\nHost: localhost\r\n\r\n".encode("utf-8")
        sock = MockSocket(req_data)
        h = handler(sock, ("127.0.0.1", 12345), None)
        output = sock.wfile.getvalue().decode("utf-8", errors="ignore")
        assert "200 OK" in output, f"Expected 200 OK for {path}"
        body_str = output.split("\r\n\r\n")[-1]
        cases = json.loads(body_str)
        assert len(cases) == 5, f"Expected 5 cases, got {len(cases)}"
        print(f"  GET {path} -> 200 OK with {len(cases)} preloaded cases!")

    # 3. Test POST /api/evaluate on all 5 cases (both direct and rewritten)
    expected_labels = {
        "CASE-1-COUNTER": "COUNTER:COUNTER_OFFER:96000",
        "CASE-2-VOLUME-DISCOUNT": "ACCEPT:ACCEPTABLE_PRICE:",
        "CASE-3-PROMPT-INJECTION": "ESCALATE:PROMPT_INJECTION:",
        "CASE-4-BANNED-TERM": "ESCALATE:BANNED_TERM:",
        "CASE-5-OVER-APPROVAL": "ESCALATE:OVER_APPROVAL_LIMIT:",
    }

    for path in ["/api/evaluate", "/api/index?path=/api/evaluate"]:
        print(f"\n[TEST 3] Testing POST {path} on all 5 preloaded cases...")
        for case in PRELOADED_TEST_CASES:
            cid = case["id"]
            payload = json.dumps(case).encode("utf-8")
            req_data = (
                f"POST {path} HTTP/1.1\r\n"
                f"Host: localhost\r\n"
                f"Content-Type: application/json\r\n"
                f"Content-Length: {len(payload)}\r\n\r\n"
            ).encode("utf-8") + payload

            sock = MockSocket(req_data)
            h = handler(sock, ("127.0.0.1", 12345), None)
            output = sock.wfile.getvalue().decode("utf-8", errors="ignore")
            assert "200 OK" in output, f"POST {path} for {cid} failed with non-200:\n{output[:200]}"
            body_str = output.split("\r\n\r\n")[-1]
            data = json.loads(body_str)
            assert data["success"] is True, f"[{cid}] Execution was not successful: {data}"
            actual_label = data["label"]
            exp_label = expected_labels[cid]
            assert actual_label == exp_label, f"[{cid}] Expected {exp_label}, got {actual_label}"
            print(f"  {path} [{cid}] -> {actual_label} (MATCH)")

    print("\n" + "=" * 65)
    print("ALL VERCEL HANDLER TESTS PASSED WITH 100% ACCURACY!")
    print("=" * 65)


if __name__ == "__main__":
    test_handler()
