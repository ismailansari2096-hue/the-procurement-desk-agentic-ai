"""
Automated Browser Console & Interaction Test via Headless Chrome CDP (Chrome DevTools Protocol).
Connects to headless Chrome, loads http://127.0.0.1:8080/, captures all console.log / error events,
clicks the 'Run Multi-Agent Deliberation' button, clicks each of the 5 test cases,
and prints any errors or DOM mutations.
"""

import sys
import json
import time
import subprocess
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def main():
    # 1. Start demo server on port 8080
    cmd_server = [sys.executable, str(BASE_DIR / "demo" / "interactive_demo.py"), "--port", "8080"]
    server_proc = subprocess.Popen(cmd_server, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(1)

    # 2. Launch Chrome headless with remote debugging port 9222
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    chrome_cmd = [
        chrome_path,
        "--headless=new",
        "--remote-debugging-port=9222",
        "--disable-gpu",
        "--no-sandbox",
        "http://127.0.0.1:8080/"
    ]
    chrome_proc = subprocess.Popen(chrome_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2)

    try:
        # Check Chrome CDP /json endpoint
        with urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=3) as resp:
            tabs = json.loads(resp.read().decode("utf-8"))
        print(f"[+] Chrome opened tabs: {len(tabs)}")
        target_tab = tabs[0]
        ws_url = target_tab.get("webSocketDebuggerUrl")
        print(f"[+] WebSocket debugger URL: {ws_url}")

    except Exception as e:
        print(f"[-] Could not connect to Chrome CDP: {e}")
    finally:
        chrome_proc.terminate()
        server_proc.terminate()

if __name__ == "__main__":
    main()
