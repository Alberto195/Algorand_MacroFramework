import http
import socketserver
import string
from http.server import BaseHTTPRequestHandler
from main import algo_client

hostName = "localhost"
serverPort = 8080


class RockPaperScissorsServer(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path.find("isButtonPressed=true") != -1:
            print("Button clicked")
            self.call_create_challenge("Oeifo839h=", "opponent_address", 1000)

        return super().do_GET()

    @staticmethod
    def call_create_challenge(commitment: string, receiver: string, amt: int):
        algo_client.call_app("create_challenge", [commitment], receiver, amt)

    @staticmethod
    def call_accept_challenge():
        algo_client.call_app("accept_challenge", [])

    @staticmethod
    def call_reveal():
        algo_client.call_app("reveal", [])


if __name__ == '__main__':
    with socketserver.TCPServer(("", serverPort), RockPaperScissorsServer) as httpd:
        print("serving at port", serverPort)
        httpd.serve_forever()
