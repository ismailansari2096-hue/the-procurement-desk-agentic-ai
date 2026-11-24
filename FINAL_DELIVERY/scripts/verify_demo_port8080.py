"""
Verifies demo launch on port 8080 as requested by the judge demonstration requirement.
Starts `python demo/interactive_demo.py --port 8080` as a subprocess,
polls http://127.0.0.1:8080/ and endpoints, checks HTTP 200 and HTML/JSON responses,
and terminates the subprocess cleanly.
"""

import sys
import time
import subprocess
import urllib.request
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def main():
    print("=" * 70)
    print("VERIFYING DEMO LAUNCH ON PORT 8080")
    print("Command: python demo/interactive_demo.py --port 8080")
    print("=" * 70)

    cmd = [sys.executable, str(BASE_DIR / "demo" / "interactive_demo.py"), "--port", "8080"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        # Wait for server to bind
        time.sleep(1.2)
        if proc.poll() is not None:
            stdout, stderr = proc.communicate()
            print(f"[-] Subprocess exited prematurely with code {proc.returncode}")
            print(f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}")
            sys.exit(1)

        # 1. Test GET /
        url = "http://127.0.0.1:8080/"
        with urllib.request.urlopen(url, timeout=3) as resp:
            status = resp.status
            html = resp.read().decode("utf-8")
            print(f"[✓] GET {url} -> HTTP {status} (Length: {len(html)} bytes)")
            assert status == 200
            assert "The Procurement Desk" in html
            assert "1. Thread Understanding Agent" in html
            assert "2. Supplier Intelligence Agent" in html
            assert "3. Policy Compliance Agent" in html
            assert "4. Prompt Injection Defense" in html
            assert "5. Pricing & Negotiation Agent" in html
            assert "6. Decision Validation Agent" in html

        # 2. Test GET /api/test-cases
        with urllib.request.urlopen("http://127.0.0.1:8080/api/test-cases", timeout=3) as resp:
            status = resp.status
            cases = json.loads(resp.read().decode("utf-8"))
            print(f"[✓] GET /api/test-cases -> HTTP {status} (Found {len(cases)} preloaded cases)")
            assert status == 200
            assert len(cases) == 5

        # 3. Test POST /api/evaluate on Case 1
        tc1 = cases[0]
        post_data = json.dumps(tc1).encode("utf-8")
        req = urllib.request.Request("http://127.0.0.1:8080/api/evaluate", data=post_data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            status = resp.status
            res = json.loads(resp.read().decode("utf-8"))
            print(f"[✓] POST /api/evaluate -> HTTP {status} (Result label: {res['label']})")
            assert status == 200
            assert res["label"] == "COUNTER:COUNTER_OFFER:96000"

        print("\n[SUCCESS] Demo server launches and operates flawlessly on port 8080.")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("[+] Subprocess terminated cleanly.")

if __name__ == "__main__":
    main()
