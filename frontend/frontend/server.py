from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

os.chdir(os.path.dirname(__file__))
HTTPServer(('127.0.0.1', 3000), SimpleHTTPRequestHandler).serve_forever()