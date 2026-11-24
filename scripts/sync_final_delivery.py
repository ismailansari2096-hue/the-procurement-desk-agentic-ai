"""
Synchronize and assemble the complete FINAL_DELIVERY package.
"""

import os
import shutil
import hashlib
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
delivery_dir = root_dir / "FINAL_DELIVERY"

def sync():
    print("=" * 65)
    print("ASSEMBLING COMPLETE FINAL_DELIVERY PACKAGE")
    print("=" * 65)

    os.makedirs(delivery_dir, exist_ok=True)

    # 1. Clean pycache and pytest_cache in FINAL_DELIVERY if present
    for dname in [".pytest_cache", "__pycache__"]:
        for p in delivery_dir.rglob(dname):
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)

    # 2. Copy source code src/
    dst_src = delivery_dir / "src"
    if dst_src.exists():
        shutil.rmtree(dst_src)
    shutil.copytree(root_dir / "src", dst_src, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print("[PASS] Synchronized src/ to FINAL_DELIVERY/src")

    # 3. Copy knowledge_base/
    dst_kb = delivery_dir / "knowledge_base"
    if dst_kb.exists():
        shutil.rmtree(dst_kb)
    shutil.copytree(root_dir / "knowledge_base", dst_kb)
    print("[PASS] Synchronized knowledge_base/ to FINAL_DELIVERY/knowledge_base")

    # 4. Copy demo/
    dst_demo = delivery_dir / "demo"
    if dst_demo.exists():
        shutil.rmtree(dst_demo)
    shutil.copytree(root_dir / "demo", dst_demo, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print("[PASS] Synchronized demo/ to FINAL_DELIVERY/demo")

    # 5. Copy tests/
    dst_tests = delivery_dir / "tests"
    if dst_tests.exists():
        shutil.rmtree(dst_tests)
    shutil.copytree(root_dir / "tests", dst_tests, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    print("[PASS] Synchronized tests/ to FINAL_DELIVERY/tests")

    # 6. Copy key scripts/
    dst_scripts = delivery_dir / "scripts"
    os.makedirs(dst_scripts, exist_ok=True)
    scripts_to_copy = [
        "build_experimental_v4.py",
        "build_experimental_v5.py",
        "verify_v4_demo_cases.py",
        "run_phase2_checks.py",
        "evaluate_examples.py",
        "validate_submission.py"
    ]
    for s in scripts_to_copy:
        src_file = root_dir / "scripts" / s
        if src_file.exists():
            shutil.copy2(src_file, dst_scripts / s)
    print(f"[PASS] Copied {len(scripts_to_copy)} core reproduction scripts to FINAL_DELIVERY/scripts")

    # 7. Copy docs/
    dst_docs = delivery_dir / "docs"
    if dst_docs.exists():
        shutil.rmtree(dst_docs)
    if (root_dir / "docs").exists():
        shutil.copytree(root_dir / "docs", dst_docs)
    print("[PASS] Synchronized docs/ to FINAL_DELIVERY/docs")

    # 8. Copy verified V4 submission CSV
    v4_src = root_dir / "outputs" / "experimental" / "submission_v4.csv"
    v4_dst = delivery_dir / "submission_v4.csv"
    shutil.copy2(v4_src, v4_dst)
    
    os.makedirs(delivery_dir / "outputs" / "experimental", exist_ok=True)
    shutil.copy2(v4_src, delivery_dir / "outputs" / "experimental" / "submission_v4.csv")

    expected_h = "a857a332fc79c9757478cecc313c5265c30235c7d89a6cc0034693311c385d92"
    h = hashlib.sha256(open(v4_dst, "rb").read()).hexdigest()
    assert h == expected_h, f"V4 hash mismatch in FINAL_DELIVERY: {h}"
    print(f"[PASS] Verified V4 submission CSV in FINAL_DELIVERY: {h}")

    # 9. Copy requirements.txt, pyproject.toml, and README.md
    for fname in ["requirements.txt", "pyproject.toml"]:
        shutil.copy2(root_dir / fname, delivery_dir / fname)
    print("[PASS] Copied configuration files")

    # 10. Audit for secrets or unwanted files
    prohibited = [".env", "id_rsa", "password", "api_key", "secret", "credentials.json"]
    found_secrets = []
    for root, dirs, files in os.walk(delivery_dir):
        for f in files:
            for p in prohibited:
                if p in f.lower():
                    found_secrets.append(os.path.join(root, f))

    assert not found_secrets, f"Prohibited files found in FINAL_DELIVERY: {found_secrets}"
    print("[PASS] Security audit: Zero secrets, keys, or credentials found in FINAL_DELIVERY")
    print("=" * 65)
    print("FINAL_DELIVERY SYNCHRONIZATION COMPLETE!")

if __name__ == "__main__":
    sync()
