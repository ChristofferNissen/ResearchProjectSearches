#!/usr/bin/python
from http.server import BaseHTTPRequestHandler,HTTPServer
import subprocess
import json

PORT_NUMBER = 8080

# This class will handles any incoming request from
# the browser 
class myHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        #     content_len = int(self.headers.get('Content-Length'))
        #     post_body = self.rfile.read(content_len)
            self.send_response(200)
            self.end_headers()

        #     data = json.loads(post_body)

            # Use the post data
            cmd = "./cmd.sh"
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            p_status = p.wait()
            (output, err) = p.communicate()
            print ("Command output : ", output)
            print ("Command exit status/return code : ", p_status)

            self.wfile.write((cmd + "\n").encode('utf8'))
            return


try:
        # Create a web server and define the handler to manage the
        # incoming request
        server = HTTPServer(('', PORT_NUMBER), myHandler)
        print ('Started httpserver on port ' , PORT_NUMBER)

        # Wait forever for incoming http requests
        server.handle_request()

except KeyboardInterrupt:
        print ('^C received, shutting down the web server')
        server.socket.close()