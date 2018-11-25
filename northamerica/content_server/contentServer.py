'''
--- Content Server ---
Serves the resources

------------------------
Author: Ibrahim Mohammad
 University of Houston
------------------------
'''

from http.server import BaseHTTPRequestHandler, HTTPServer

import sys
import os
import mimetypes
HTTP_PORT = int(sys.argv[1])


# This class handles any incoming request from the CDN server
class FileServer(BaseHTTPRequestHandler):

    # Handler for the GET requests
    def do_GET(self):

        if os.path.isfile('./' + self.path):
            # Send response code and headers
            self.send_response(200)
            #Dynamically determine mimetypes for files
            mime_type = mimetypes.MimeTypes().guess_type(self.path)[0]
            self.send_header('Content-type', mime_type)
            self.send_header('Content-length', str(os.stat('./' + self.path).st_size))
            self.end_headers()
            print("Sending FILE")
            # Send the binary file
            with open('./' + self.path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            # Send 404 (Not Found) status code for any other requests
            self.send_response(404)
        return


try:
    server = HTTPServer(('', HTTP_PORT), FileServer)
    print('Started httpserver on port', HTTP_PORT)

    # Wait forever for incoming HTTP requests
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()