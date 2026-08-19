#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local dev server with no-cache headers."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import os
import sys

PORT = int(os.environ.get("PORT", "8888"))
ROOT = os.path.dirname(os.path.abspath(__file__))


class NoCacheHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt, *args):
        if args and str(args[0]).startswith("GET /"):
            sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    os.chdir(ROOT)
    with ThreadingHTTPServer(("0.0.0.0", PORT), NoCacheHandler) as httpd:
        print("")
        print("  Roteiro EU - servidor local (sem cache)")
        print("  -> http://127.0.0.1:%d/" % PORT)
        print("  -> http://127.0.0.1:%d/#presentes" % PORT)
        print("")
        print("  NAO abras file:// - usa o URL acima.")
        print("  Ctrl+C para parar")
        print("")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor parado.")
