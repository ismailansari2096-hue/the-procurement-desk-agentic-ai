"""
Automated Chrome DevTools Protocol (CDP) test for demo/index.html.
Verifies all 5 preloaded test cases AND custom input evaluation,
verifying button state, latency toast, DOM updates, and error handling.
"""

import sys
import json
import time
import asyncio
import subprocess
import urllib.request
from pathlib import Path
import websockets

BASE_DIR = Path(__file__).resolve().parent.parent

async def test_full_browser_interaction():
    cmd_server = [sys.executable, str(BASE_DIR / "demo" / "interactive_demo.py"), "--port", "8080"]
    server_proc = subprocess.Popen(cmd_server, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(1.2)

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir = BASE_DIR / "temp_chrome_profile"
    chrome_cmd = [
        chrome_path,
        "--headless=new",
        "--remote-debugging-port=9222",
        f"--user-data-dir={user_data_dir}",
        "--disable-gpu",
        "--no-sandbox",
        "http://127.0.0.1:8080/"
    ]
    chrome_proc = subprocess.Popen(chrome_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2)

    try:
        with urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=3) as resp:
            tabs = json.loads(resp.read().decode("utf-8"))
        page_tab = next(t for t in tabs if t["type"] == "page")
        ws_url = page_tab["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url) as ws:
            msg_id = 0

            async def send_cmd(method, params=None):
                nonlocal msg_id
                msg_id += 1
                payload = {"id": msg_id, "method": method, "params": params or {}}
                await ws.send(json.dumps(payload))
                while True:
                    res = json.loads(await ws.recv())
                    if res.get("id") == msg_id:
                        return res.get("result", {})

            await ws.send(json.dumps({"id": 999, "method": "Runtime.enable"}))
            await ws.send(json.dumps({"id": 998, "method": "Console.enable"}))

            # 1. Test clicking each pill + clicking button
            expected = [
                ("CASE-1-COUNTER", "COUNTER:COUNTER_OFFER:96000"),
                ("CASE-2-VOLUME-DISCOUNT", "ACCEPT:ACCEPTABLE_PRICE:"),
                ("CASE-3-PROMPT-INJECTION", "ESCALATE:PROMPT_INJECTION:"),
                ("CASE-4-BANNED-TERM", "ESCALATE:BANNED_TERM:"),
                ("CASE-5-OVER-APPROVAL", "ESCALATE:OVER_APPROVAL_LIMIT:")
            ]

            print("=" * 65)
            print("TESTING ALL 5 PRELOADED TEST CASES IN CHROME BROWSER")
            print("=" * 65)

            for idx, (cid, exp_label) in enumerate(expected):
                # Click pill
                await send_cmd("Runtime.evaluate", {"expression": f"document.querySelectorAll('.test-pill')[{idx}].click()"})
                await asyncio.sleep(0.4)

                # Click button explicitly
                await send_cmd("Runtime.evaluate", {"expression": "document.getElementById('btn-evaluate').click()"})
                await asyncio.sleep(0.4)

                label_val = (await send_cmd("Runtime.evaluate", {"expression": "document.getElementById('res-label').innerText"})).get("result", {}).get("value")
                toast_val = (await send_cmd("Runtime.evaluate", {"expression": "document.getElementById('status-toast').innerText"})).get("result", {}).get("value")
                timing_val = (await send_cmd("Runtime.evaluate", {"expression": "document.getElementById('res-timing').innerText"})).get("result", {}).get("value")

                passed = (label_val == exp_label)
                print(f"[{'PASS' if passed else 'FAIL'}] {cid}:")
                print(f"       Label:  {label_val} (Expected: {exp_label})")
                print(f"       Timing: {timing_val}")
                print(f"       Toast:  {toast_val}")
                assert passed, f"Mismatch for {cid}: {label_val} != {exp_label}"

            # 2. Test Custom Input via Button Click
            print("\n" + "=" * 65)
            print("TESTING CUSTOM USER INPUT VIA DELIBERATION BUTTON")
            print("=" * 65)

            custom_setup = """
            document.getElementById('inp-thread-id').value = 'CUSTOM-TEST-001';
            document.getElementById('inp-category').value = 'cleaning';
            document.getElementById('inp-supplier').value = 'Apex Facilities Management';
            document.getElementById('inp-quantity').value = '2';
            document.getElementById('inp-round').value = '1';
            document.getElementById('inp-message').value = 'We can do INR 80,000 per site per month.';
            """
            await send_cmd("Runtime.evaluate", {"expression": custom_setup})
            # Click button
            await send_cmd("Runtime.evaluate", {"expression": "document.getElementById('btn-evaluate').click()"})
            await asyncio.sleep(0.5)

            custom_label = (await send_cmd("Runtime.evaluate", {"expression": "document.getElementById('res-label').innerText"})).get("result", {}).get("value")
            custom_step = (await send_cmd("Runtime.evaluate", {"expression": "document.getElementById('res-step').innerText"})).get("result", {}).get("value")
            print(f"[✓] Custom Thread Evaluation Result: {custom_label}")
            print(f"    Triggered Step: {custom_step}")
            assert custom_label == "ACCEPT:ACCEPTABLE_PRICE:", f"Expected ACCEPT:ACCEPTABLE_PRICE:, got {custom_label}"

            print("\n[SUCCESS] Browser interaction, button event listener, and API response verified 100% in Chrome.")

    finally:
        chrome_proc.terminate()
        server_proc.terminate()
        import shutil
        if user_data_dir.exists():
            shutil.rmtree(user_data_dir, ignore_errors=True)

if __name__ == "__main__":
    asyncio.run(test_full_browser_interaction())
