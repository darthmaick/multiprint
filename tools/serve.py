# -*- coding: utf-8 -*-
"""Serveur local de la maquette, sans cache navigateur (chaque rechargement affiche la dernière version).
Usage : python tools/serve.py [port]"""
import functools, http.server, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Expires', '0')
        super().end_headers()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    handler = functools.partial(NoCache, directory=str(ROOT))
    with http.server.ThreadingHTTPServer(('127.0.0.1', port), handler) as srv:
        print(f'Maquette Multiprint : http://localhost:{port}/')
        srv.serve_forever()
