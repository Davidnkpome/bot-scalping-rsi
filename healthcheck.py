from http.server import BaseHTTPRequestHandler, HTTPServer

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Pong")

if __name__ == "__main__":
    server = HTTPServer(('', 8080), PingHandler)
    print("✅ Healthcheck server running on port 8080")
    server.serve_forever()