import sys
from pathlib import Path

# Add project root and src to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(ROOT_DIR / "src"))

from demo.interactive_demo import DemoRequestHandler


class handler(DemoRequestHandler):
    """
    Vercel Serverless Function entrypoint.
    Executes the exact production V4 Multi-Agent Decision Engine.
    """
    pass
