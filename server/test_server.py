# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

from macro.Mode import Mode
from main import algo_client

hostName = "localhost"
serverPort = 8080


class Casino:

    def __init__(self):
        self.username = ""

    def set_username(self, username):
        self.username = username

    def count_square_of_rolls(self):
        return algo_client.read_variable_state("rolls", Mode.LOCAL)*algo_client.read_variable_state("rolls", Mode.LOCAL)

    def roll(self):
        algo_client.call_app("roll", [])


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        casino = Casino()
        casino.roll()
        rolls_sq = casino.count_square_of_rolls()
        self.wfile.write(bytes(f"<p>Rolls Squared: {rolls_sq}.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))


if __name__ == '__main__':
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

