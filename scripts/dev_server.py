#!/usr/bin/env python3
"""Local-only static server with the deployment's security headers, for browser QA."""
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

root = Path(__file__).resolve().parents[1]
public = root / 'public'
headers = json.loads((root / 'vercel.json').read_text())['headers'][0]['headers']


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(public), **kwargs)

    def do_GET(self):
        if urlsplit(self.path).path in ('/privacy', '/terms', '/gridhq-screenshots', '/still-screenshots', '/left-screenshots'):
            self.path = urlsplit(self.path).path + '.html'
        super().do_GET()

    def end_headers(self):
        for header in headers:
            self.send_header(header['key'], header['value'])
        super().end_headers()


print('Local security QA server: http://127.0.0.1:8765', flush=True)
ThreadingHTTPServer(('127.0.0.1', 8765), Handler).serve_forever()
