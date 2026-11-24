"""
Test api/index.py handler directly to verify Vercel serverless compatibility.
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

    # 1. Test GET /
    print("\n[TEST 1] Testing GET / (HTML Dashboard)...")
    req_data = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"
    sock = MockSocket(req_data)
    h = handler(sock, ("127.0.0.1", 12345), None)
    output = sock.wfile.getvalue().decode("utf-8", errors="ignore")
    assert "200 OK" in output, "Expected 200 OK"
    assert "The Procurement Desk" in output, "Expected Dashboard title in HTML"
    assert "V4 Model • Kaggle Public Score: 1.00000" in output, "Expected V4 badge in HTML"
    assert "Public Leaderboard Score — Private Score Pending" in output, "Expected disclosure in HTML"
    print("  GET / -> 200 OK with verified V4 dashboard HTML!")

    # 2. Test GET /api/test-cases
    print("\n[TEST 2] Testing GET /api/test-cases...")
    req_data = b"GET /api/test-cases HTTP/1.1\r\nHost: localhost\r\n\r\n"
    sock = MockSocket(req_data)
    h = handler(sock, ("127.0.0.1", 12345), None)
    output = sock.wfile.getvalue().decode("utf-8", errors="ignore")
    assert "200 OK" in output, "Expected 200 OK"
    body_str = output.split("\r\n\r\n")[-1]
    cases = json.loads(body_str)
    assert len(cases) == 5, f"Expected 5 cases, got {len(cases)}"
    print(f"  GET /api/test-cases -> 200 OK with {len(cases)} preloaded cases!")

    # 3. Test POST /api/evaluate with all 5 scenarios
    print("\n[TEST 3] Testing POST /api/evaluate with all 5 scenarios...")
    expected_results = [
        ("CASE-1-COUNTER", "COUNTER:COUNTER_OFFER:96000", 5),
        ("CASE-2-VOLUME-DISCOUNT", "ACCEPT:ACCEPTABLE_PRICE:", 6),
        ("CASE-3-PROMPT-INJECTION", "ESCALATE:PROMPT_INJECTION:", 3),
        ("CASE-4-BANNED-TERM", "ESCALATE:BANNED_TERM:", 4),
        ("CASE-5-OVER-APPROVAL", "ESCALATE:OVER_APPROVAL_LIMIT:", 6)
    ]

    for idx, (tc, (exp_id, exp_lbl, exp_step)) in enumerate(zip(PRELOADED_TEST_CASES, expected_results), 1):
        assert tc["id"] == exp_id
        body_bytes = json.dumps(tc).encode("utf-8")
        req_data = (
            f"POST /api/evaluate HTTP/1.1\r\n"
            f"Host: localhost\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(body_bytes)}\r\n\r\n"
        ).encode("utf-8") + body_bytes

        sock = MockSocket(req_data)
        h = handler(sock, ("127.0.0.1", 12345), None)
        output = sock.wfile.getvalue().decode("utf-8", errors="ignore")
        assert "200 OK" in output, f"POST /api/evaluate failed on {tc['id']}"

        resp_json = json.loads(output.split("\r\n\r\n")[-1])
        assert resp_json["success"] is True
        assert resp_json["label"] == exp_lbl, f"Mismatch on {tc['id']}: got {resp_json['label']}, expected {exp_lbl}"
        assert resp_json["fired_step"] == exp_step, f"Step mismatch on {tc['id']}: got {resp_json['fired_step']}, expected {exp_step}"
        print(f"  Scenario {idx} [{tc['id']}]: {resp_json['label']} (Step {resp_json['fired_step']}) in {resp_json['duration_ms']}ms -> PASS")

    print("\n" + "=" * 65)
    print("VERCEL HANDLER (API/INDEX.PY) 100% COMPATIBLE AND TESTED!")
    print("=" * 65)

if __name__ == "__main__":
    test_handler()
