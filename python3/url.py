import socket
import ssl


def make_headers(headers: dict[str, str]):
    headers_str = ""
    for key, value in headers.items():
        headers_str += f"{key}: {value}\r\n"
    return headers_str


class CustomURL:
    def __init__(self, url: str):
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["file", "http", "https"]

        if "/" not in url:
            url = f"{url}/"
        self.host, url = url.split("/", 1)

        # Ensure path is prepended with `/`
        self.path = f"/{url}"

        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    def _request_http(self):
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
            # Only send requests over secure context
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
            return contents

    def request(self):
        if self.scheme == "file":
            return self._request_file()

        return self._request_http()
