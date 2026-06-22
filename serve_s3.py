#!/usr/bin/env python3
"""
serve_s3.py — local server for the Sabaio S3 runner.

Serves this folder statically (like `python -m http.server`) AND adds one extra
endpoint, GET /api/generate, which runs the popularity-pack generator and STREAMS
its progress to the browser as Server-Sent Events. That lets s3-runner.html show a
live "Generator output" panel — the same progress you'd see on the CLI, but in the UI.

Why a server: the browser can't call data.rechtspraak.nl directly (CORS), so generation
has to happen here; the SSE stream is what surfaces it live.

    python serve_s3.py [port]        # default 8753

/api/generate query params: popular, obscure, year_from, year_to, rechtsgebied,
false_twins (true/false), seed, out (filename, basename only). The generated pack is
written to packs/<out> and a final "done" event reports the path + counts.
"""
import json
import os
import sys
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)               # so `import generate_pack` works from any cwd
import generate_pack as gp             # noqa: E402

PACKS = os.path.join(ROOT, "packs")


def unique_path(dirpath, filename):
    """Return a path that does not yet exist: foo.json, else foo-2.json, foo-3.json…
    So generated packs never overwrite an existing one."""
    base, ext = os.path.splitext(filename)
    cand, n = filename, 2
    while os.path.exists(os.path.join(dirpath, cand)):
        cand = f"{base}-{n}{ext}"
        n += 1
    return cand


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def log_message(self, *a):
        pass  # keep the console quiet

    def do_GET(self):
        if urllib.parse.urlparse(self.path).path == "/api/generate":
            return self.handle_generate()
        return super().do_GET()

    def _sse(self, event, data):
        msg = f"event: {event}\ndata: {json.dumps(data)}\n\n"
        self.wfile.write(msg.encode("utf-8"))
        self.wfile.flush()

    def handle_generate(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        g = lambda k, d: q.get(k, [d])[0]
        try:
            popular = max(0, min(int(g("popular", "5")), len(gp.POPULAR_SEED)))
            obscure = max(0, min(int(g("obscure", "10")), 40))   # polite cap
            yf, yt = int(g("year_from", "2015")), int(g("year_to", "2024"))
            seed = int(g("seed", "7"))
            rechtsgebied = g("rechtsgebied", "civielRecht")
            false_twins = g("false_twins", "false").lower() == "true"
            out = os.path.basename(g("out", "nl-popularity-tiered.json"))  # no path traversal
            if not out.endswith(".json"):
                out += ".json"
        except ValueError:
            self.send_error(400, "bad params")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            pack = gp.build_pack(popular, obscure, yf, yt, rechtsgebied, false_twins,
                                 seed, log=lambda m: self._sse("log", m))
            os.makedirs(PACKS, exist_ok=True)
            final = unique_path(PACKS, out)          # never overwrite an existing pack
            if final != out:
                self._sse("log", f"  ~ '{out}' exists — saving as '{final}'")
            with open(os.path.join(PACKS, final), "w", encoding="utf-8") as f:
                json.dump(pack, f, ensure_ascii=False, indent=2)
            n_high = sum(1 for t in pack["tests"] if t["verify_status"] == "high")
            self._sse("done", {"file": f"packs/{final}", "name": pack["name"],
                               "requested": out, "renamed": final != out,
                               "items": len(pack["tests"]), "high": n_high,
                               "needs_check": len(pack["tests"]) - n_high})
        except BrokenPipeError:
            return  # client navigated away mid-stream
        except Exception as e:  # noqa: BLE001 — surface any failure to the panel
            try:
                self._sse("failed", str(e))
            except Exception:
                pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8753
    print(f"Sabaio S3 server → http://localhost:{port}  "
          f"(static files + /api/generate SSE)")
    ThreadingHTTPServer(("", port), Handler).serve_forever()
