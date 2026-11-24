"""
Stage reviewed files, audit staged list, commit, push to private GitHub repo, and verify visibility.
"""

import subprocess
import sys
import json

def run_cmd(cmd_list, check=True):
    print(f"Running: {' '.join(cmd_list)}")
    res = subprocess.run(cmd_list, capture_output=True, text=True)
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr and res.returncode != 0:
        print(f"STDERR: {res.stderr.strip()}")
    if check and res.returncode != 0:
        sys.exit(res.returncode)
    return res

def main():
    print("=" * 65)
    print("PHASE 3: GIT STAGE, AUDIT, COMMIT & PUSH")
    print("=" * 65)

    # 1. Stage all files
    run_cmd(["git", "add", "."])

    # 2. Audit staged files
    staged_res = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    staged = [l.strip() for l in staged_res.stdout.splitlines() if l.strip()]
    print(f"\nTotal files staged: {len(staged)}")

    forbidden = [
        f for f in staged 
        if f.endswith((".csv", ".zip", ".tar", ".gz", ".env"))
        or "secret" in f.lower() 
        or "credential" in f.lower() 
        or "temp_chrome" in f.lower() 
        or "data/raw" in f.replace("\\", "/")
        or "raw" in f.lower()
        or "outputs" in f.replace("\\", "/")
    ]

    if forbidden:
        print("CRITICAL SECURITY ERROR! Forbidden files in staging:")
        for fb in forbidden:
            print(f"  [FORBIDDEN] {fb}")
        sys.exit(1)
    else:
        print("[VERIFIED] Zero forbidden files in staging. Audit passed!")

    # 3. Create commit
    commit_msg = "feat: complete V4 autonomous procurement decision engine and Vercel serverless deployment"
    run_cmd(["git", "commit", "-m", commit_msg])

    # 4. Push to origin main
    run_cmd(["git", "push", "-u", "origin", "main"])

    # 5. Verify repository visibility is PRIVATE
    view_res = subprocess.run(["gh", "repo", "view", "the-procurement-desk-agentic-ai", "--json", "isPrivate,visibility,url,name"], capture_output=True, text=True)
    info = json.loads(view_res.stdout)
    print(f"\nRepository Name : {info.get('name')}")
    print(f"Repository URL  : {info.get('url')}")
    print(f"Visibility      : {info.get('visibility')}")
    print(f"Is Private      : {info.get('isPrivate')}")
    assert info.get("isPrivate") is True, "Repository must be PRIVATE!"
    print("\n[PASS] REPOSITORY PUSHED & CONFIRMED PRIVATE!")
    print("=" * 65)

if __name__ == "__main__":
    main()
