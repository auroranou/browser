import socket
import ssl
from urllib.parse import urlparse


def make_headers(headers: dict[str, str]):
    headers_str = ""
    for key, value in headers.items():
        headers_str += f"{key}: {value}\r\n"
    return headers_str


class URL:
    def __init__(self, url: str):
        self.should_view_source = False

        if url.startswith("view-source"):
            self.should_view_source = True
            _, url = url.split("view-source:", 1)
        if url.startswith("data:"):
            self.scheme, self.path = url.split(",", 1)
        else:
            result = urlparse(url)

            self.scheme = result.scheme
            assert self.scheme in ["file", "http", "https"]

            self.host = result.hostname
            self.path = result.path

            if result.port:
                self.port = result.port
            elif self.scheme == "http":
                self.port = 80
            elif self.scheme == "https":
                self.port = 443

    def _request_http(self):
        assert self.host is not None and self.port is not None

        s = socket.socket(
            # Address family (how to find remote computer)
            family=socket.AF_INET,
            # Protocol for establishing connection, based on address family
            proto=socket.IPPROTO_TCP,
            # Stream type = each computer can send arbitrary amounts of data
            type=socket.SOCK_STREAM,
        )
        s.connect((self.host, self.port))

        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        headers = make_headers({"Host": self.host, "Connection": "close"})
        request = f"GET {self.path} HTTP/1.1\r\n{headers}\r\n"

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

    def _request_file(self):
        with open(self.path, "rb") as file:
            contents = file.read()
            return contents, False

    def _request_data(self):
        return self.path

    def request(self):
        if self.scheme.startswith("data:"):
            result = self._request_data()
        elif self.scheme == "file":
            result = self._request_file()
        elif self.scheme in ["http", "https"]:
            result = self._request_http()
        else:
            raise
        return result, self.should_view_source
