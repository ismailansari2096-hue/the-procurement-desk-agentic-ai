import sys
import urllib.parse
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
    Handles Vercel routing rewrites via query parameters and headers.
    """

    def _resolve_path(self):
        # 1. Check if original path is passed via Vercel rewrite query parameter (?path=...)
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        if "path" in qs and qs["path"]:
            self.path = qs["path"][0]
            return

        # 2. Check if original path is passed via Vercel edge headers
        orig = (
            self.headers.get("x-matched-path")
            or self.headers.get("x-vercel-forwarded-path")
            or self.headers.get("x-forwarded-uri")
        )
        if orig and orig not in ("/api/index", "/api/index.py"):
            self.path = orig
            return

        # 3. Default fallback: if reaching /api/index directly without sub-path
        if parsed.path in ("/api/index", "/api/index.py", "/api"):
            self.path = "/"

    def do_GET(self):
        self._resolve_path()
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html", "/api/index", "/api/index.py", "/api"):
            self.path = "/"
        super().do_GET()

    def do_POST(self):
        self._resolve_path()
        super().do_POST()
