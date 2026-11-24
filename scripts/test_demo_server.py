"""
Automated verification of the Interactive Demo Web Server.
"""

import json
import time
import threading
import urllib.request
from http.server import HTTPServer
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "src"))

from demo.interactive_demo import DemoRequestHandler, PRELOADED_TEST_CASES

def main():
    server = HTTPServer(("localhost", 8089), DemoRequestHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.5)

    try:
        # 1. Test GET /
        req = urllib.request.urlopen("http://localhost:8089/")
        html = req.read().decode("utf-8")
        assert "The Procurement Desk" in html, "HTML title mismatch"
        print("[PASS] GET / -> HTTP 200 (HTML UI Served)")

        # 2. Test GET /api/test-cases
        req = urllib.request.urlopen("http://localhost:8089/api/test-cases")
        cases = json.loads(req.read().decode("utf-8"))
        assert len(cases) == 5, "Expected 5 preloaded test cases"
        print(f"[PASS] GET /api/test-cases -> HTTP 200 ({len(cases)} cases returned)")

        # 3. Test POST /api/evaluate with preloaded case 1
        data = json.dumps(PRELOADED_TEST_CASES[0]).encode("utf-8")
        post_req = urllib.request.Request(
            "http://localhost:8089/api/evaluate",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        resp = json.loads(urllib.request.urlopen(post_req).read().decode("utf-8"))
        assert resp["success"] is True
        print(f"[PASS] POST /api/evaluate -> HTTP 200 (Label: {resp['label']}, latency: {resp['duration_ms']}ms)")

        # 4. Test all 5 cases via API
        for idx, tc in enumerate(PRELOADED_TEST_CASES, 1):
            d = json.dumps(tc).encode("utf-8")
            pr = urllib.request.Request(
                "http://localhost:8089/api/evaluate",
                data=d,
                headers={"Content-Type": "application/json"}
            )
            r = json.loads(urllib.request.urlopen(pr).read().decode("utf-8"))
            print(f"  Case {idx} ({tc['id']}): {r['label']} (Fired Step {r['fired_step']}) in {r['duration_ms']}ms")

        print("\nDEMO SERVER FULLY FUNCTIONAL AND READY FOR JUDGES!")
    finally:
        server.shutdown()

if __name__ == "__main__":
    main()
