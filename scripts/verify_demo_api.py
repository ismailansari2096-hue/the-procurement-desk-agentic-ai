"""
End-to-End Live HTTP Web API Test for The Procurement Desk Interactive Demo.
Starts the Demo HTTP Server on a dedicated port in a daemon thread,
issues actual HTTP requests using urllib.request, validates responses,
and shuts down cleanly.
"""

import sys
import json
import time
import threading
import urllib.request
import urllib.error
from pathlib import Path
from http.server import HTTPServer

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

from demo.interactive_demo import DemoRequestHandler, PRELOADED_TEST_CASES

TEST_PORT = 8999
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"

EXPECTED_DECISIONS = {
    "CASE-1-COUNTER": {
        "expected_label": "COUNTER:COUNTER_OFFER:96000",
        "expected_action": "COUNTER",
        "expected_reason": "COUNTER_OFFER",
        "expected_counter": "96000",
        "expected_step": 5
    },
    "CASE-2-VOLUME-DISCOUNT": {
        "expected_label": "ACCEPT:ACCEPTABLE_PRICE:",
        "expected_action": "ACCEPT",
        "expected_reason": "ACCEPTABLE_PRICE",
        "expected_counter": "",
        "expected_step": 6
    },
    "CASE-3-PROMPT-INJECTION": {
        "expected_label": "ESCALATE:PROMPT_INJECTION:",
        "expected_action": "ESCALATE",
        "expected_reason": "PROMPT_INJECTION",
        "expected_counter": "",
        "expected_step": 3
    },
    "CASE-4-BANNED-TERM": {
        "expected_label": "ESCALATE:BANNED_TERM:",
        "expected_action": "ESCALATE",
        "expected_reason": "BANNED_TERM",
        "expected_counter": "",
        "expected_step": 4
    },
    "CASE-5-OVER-APPROVAL": {
        "expected_label": "ESCALATE:OVER_APPROVAL_LIMIT:",
        "expected_action": "ESCALATE",
        "expected_reason": "OVER_APPROVAL_LIMIT",
        "expected_counter": "",
        "expected_step": 6
    }
}


def start_server():
    server = HTTPServer(("127.0.0.1", TEST_PORT), DemoRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def http_get(path: str):
    req = urllib.request.Request(f"{BASE_URL}{path}")
    with urllib.request.urlopen(req, timeout=5) as response:
        return response.status, response.read(), response.headers


def http_post(path: str, data: dict):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=body,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def main():
    print("=" * 70)
    print("STEP 2: LIVE HTTP WEB API VERIFICATION OF DEMO APPLICATION")
    print("=" * 70)

    print(f"[+] Starting HTTP server on {BASE_URL}...")
    server = start_server()
    time.sleep(0.5)

    try:
        # 1. Test GET / (HTML frontend)
        status, html_bytes, headers = http_get("/")
        print(f"[✓] GET / -> HTTP {status} (Length: {len(html_bytes)} bytes)")
        assert status == 200
        assert b"The Procurement Desk" in html_bytes

        # 2. Test GET /api/test-cases
        status, tc_bytes, _ = http_get("/api/test-cases")
        test_cases = json.loads(tc_bytes.decode("utf-8"))
        print(f"[✓] GET /api/test-cases -> HTTP {status} (Retrieved {len(test_cases)} cases)")
        assert status == 200
        assert len(test_cases) == 5

        # 3. Test GET /api/metadata
        status, meta_bytes, _ = http_get("/api/metadata")
        meta = json.loads(meta_bytes.decode("utf-8"))
        print(f"[✓] GET /api/metadata -> HTTP {status} ({len(meta['categories'])} categories, {len(meta['suppliers'])} suppliers)")
        assert status == 200

        # 4. Test POST /api/evaluate on all 5 demo cases
        print("\nEvaluating all 5 preloaded demo cases via POST /api/evaluate:")
        all_passed = True
        results = []

        for tc in test_cases:
            cid = tc["id"]
            exp = EXPECTED_DECISIONS[cid]

            status, res = http_post("/api/evaluate", tc)
            assert status == 200, f"HTTP status failed for {cid}: {status}"

            actual_label = res.get("label")
            actual_action = res.get("action")
            actual_reason = res.get("reason")
            actual_counter = res.get("counter_price")
            actual_step = res.get("fired_step")

            label_match = (actual_label == exp["expected_label"])
            action_match = (actual_action == exp["expected_action"])
            reason_match = (actual_reason == exp["expected_reason"])
            counter_match = (actual_counter == exp["expected_counter"])
            step_match = (actual_step == exp["expected_step"])

            case_passed = all([label_match, action_match, reason_match, counter_match, step_match])

            if not case_passed:
                all_passed = False

            results.append({
                "id": cid,
                "title": tc["title"],
                "expected": exp["expected_label"],
                "actual": actual_label,
                "expected_step": exp["expected_step"],
                "actual_step": actual_step,
                "passed": case_passed,
                "details": {
                    "thread_understanding": res.get("thread_understanding", {}).get("effective_inr_price"),
                    "supplier_intelligence": res.get("supplier_intelligence", {}).get("status"),
                    "policy_compliance": res.get("policy_compliance", {}).get("effective_target"),
                    "injection_defense": res.get("injection_defense", {}).get("is_injection"),
                    "pricing_negotiation": res.get("pricing_negotiation", {}).get("concession_level")
                }
            })

            status_str = "[PASS]" if case_passed else "[FAIL]"
            print(f"  {status_str} {cid}:")
            print(f"         Expected: {exp['expected_label']} (Step {exp['expected_step']})")
            print(f"         Actual:   {actual_label} (Step {actual_step})")

        print("\n" + "=" * 70)
        print("SUMMARY OF API VERIFICATION:")
        print("=" * 70)
        for r in results:
            print(f"  {r['id']}: {'PASSED' if r['passed'] else 'FAILED'}")
            print(f"    Label: {r['actual']} | Expected: {r['expected']}")

        assert all_passed, "Some demo test cases failed via the live Web API!"
        print("\n[SUCCESS] All 5 demo cases verified 100% via the live Web API.")

    finally:
        server.shutdown()
        server.server_close()
        print("[+] HTTP test server shut down cleanly.")


if __name__ == "__main__":
    main()
