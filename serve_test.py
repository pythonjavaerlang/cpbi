"""Smoke test: serve dist/ and fetch key pages + assets, assert HTTP 200."""
import http.server
import socketserver
import threading
import urllib.request
from pathlib import Path

DIST = Path(__file__).resolve().parent / "dist"
PORT = 8799

handler = lambda *a, **k: http.server.SimpleHTTPRequestHandler(*a, directory=str(DIST), **k)
httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
t = threading.Thread(target=httpd.serve_forever, daemon=True)
t.start()

paths = [
    "/", "/sitemap.xml", "/robots.txt",
    "/tlumachennia-staroho-zavitu/", "/tlumachennia-staroho-zavitu/buttia/",
    "/tlumachennia-novoho-zavitu/", "/tlumachennia-sviatoho-pysma/",
    "/history/", "/greek/", "/zhurnal/", "/novyny/",
    "/kontakty/", "/vstup/", "/pochatkova-shkola/", "/peredplata-zhurnalu/",
    "/pozhertvy/", "/video-lektsii/", "/biblioteka/",
    "/media/css/main.css", "/media/img/logo.png", "/og/index.jpg",
]
bad = []
for p in paths:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{PORT}{p}", timeout=5) as r:
            code = r.status
            ctype = r.headers.get("Content-Type", "")
    except Exception as e:
        bad.append((p, str(e)))
        continue
    if code != 200:
        bad.append((p, code))
    print(f"{code}  {p}  ({ctype})")

httpd.shutdown()
print("\n=== RESULT ===")
if bad:
    print("FAILURES:", bad)
    raise SystemExit(1)
print(f"ALL {len(paths)} REQUESTS 200 OK")
