import socket
import ssl

class CustomURL:
    def __init__(self, url):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"]

        if "/" not in url:
            url = f'{url}/'
        self.host, url = url.split("/", 1)
        
        # Ensure path is prepended with `/`
        self.path = f'/{url}'

        if ":" in self.host:
             self.host, port = self.host.split(":", 1)
             self.port = int(port)
        elif self.scheme == "http":
             self.port = 80
        elif self.scheme == "https":
             self.port = 443
    
    def request(self):
        s = socket.socket(
            # Address family (how to find remote computer)
            family=socket.AF_INET,
            # Protocol for establishing connection, based on address family
            proto=socket.IPPROTO_TCP,
            # Stream type = each computer can send arbitrary amounts of data
            type=socket.SOCK_STREAM,
        )

        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        s.connect((self.host, self.port))

        request = (
            f'GET {self.path} HTTP/1.0\r\n'
            f'HOST: {self.host}\r\n'
            f'\r\n'
        )

        s.send(request.encode("utf8"))

        # Write response bytes to a file-like object, handling HTTP line endings
        response = s.makefile("r", encoding="utf8", newline="\r\n")

        # Read out response parts; status line is first line
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        # Don't bother checking server HTTP version against own version
        # Parse response headers
        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n":
                    break
            header, value = line.split(":", 1)
            # Headers are case-insensitive, whitespace doesn't matter
            response_headers[header.casefold()] = value.strip()

        # Don't handle compression and chunking for now
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        content = response.read()
        s.close()

        return content
