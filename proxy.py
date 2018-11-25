'''
--- Content Delivery Network ---
Proxy forwards the requests to CDN server
------------------------
Author: Ibrahim Mohammad
imohammad@uh.edu
University of Houston
------------------------
'''
import urllib.request
import time
import sys
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer

PROXY_PORT = int(sys.argv[1])
SERVER_IP = sys.argv[2]
SERVER_PORT = int(sys.argv[3])
CACHE_TYPE = sys.argv[4]

class myMainHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith(".html") or self.path.endswith(".jpg"):
                print(self.path)
                url_server = 'http://' + SERVER_IP + ':' + str(SERVER_PORT) + '' + self.path
                req = urllib.request.Request(url_server)
                req.add_header('from', 'Proxy')
                req.add_header('cacheType', CACHE_TYPE)
                before = time.monotonic()
                with urllib.request.urlopen(req) as res:
                    file = res.read()
                    print(res.info())
                after = time.monotonic()
                delay = after - before
                print("Response in %s Seconds"% int(delay))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(file)

            else:
                self.send_response(404)
        except urllib.error.HTTPError:
            self.send_response(404)
            self.end_headers()
        except http.client.HTTPException as e:
            self.send_response(404)
            self.end_headers()

try:
    server = HTTPServer(('', PROXY_PORT), myMainHandler)
    print("Server Started on port: %s" % PROXY_PORT)
    server.serve_forever()
except KeyboardInterrupt:
    print("Interrupted")
    server.socket.close()
