"""
Categorize tracked vs ignored files for final audit.
"""

import subprocess

def main():
    dry = subprocess.run(["git", "add", "--dry-run", "."], capture_output=True, text=True)
    added = [l.split("add ")[-1].strip("'\" ") for l in dry.stdout.splitlines() if "add " in l]

    categories = {}
    for f in added:
        top = f.split("/")[0] if "/" in f else "root"
        categories[top] = categories.get(top, 0) + 1

    print(f"Total Safe Files to Track: {len(added)}")
    for cat, cnt in sorted(categories.items()):
        print(f"  {cat}: {cnt} files")

if __name__ == "__main__":
    main()
