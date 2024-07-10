from abc import ABC, abstractmethod
import socket
import ssl
from urllib.parse import urlparse

from cache import browser_cache
from headers import make_headers, parse_cache_control_header


class AbstractURL(ABC):
    @abstractmethod
    def __init__(self, url: str):
        pass

    @abstractmethod
    def request(self) -> tuple[str, bool]:
        pass


class URL:
    @staticmethod
    def create(url: str):
        if url.startswith("data:"):
            return DataURL(url)
        elif url.startswith("file:"):
            return FileURL(url)
        else:
            return HttpURL(url)


# Ex. 1-3
class DataURL(AbstractURL):
    def __init__(self, url: str):
        self.url = url
        self.scheme, self.path = url.split(",", 1)

    def request(self) -> tuple[str, bool]:
        return self.path, False


# Ex. 1-2
class FileURL(AbstractURL):
    def __init__(self, url: str) -> None:
        self.url = url
        result = urlparse(url)

        self.scheme = result.scheme
        self.path = result.path

    def request(self) -> tuple[str, bool]:
        with open(self.path, "r") as file:
            contents = file.read()
            return contents, False


class HttpURL(AbstractURL):
    def __init__(self, url: str):
        self._parse_url(url)

    def _parse_url(self, url):
        self.url = url
        self.should_view_source = False

        # Ex. 1-5
        if url.startswith("view-source"):
            self.should_view_source = True
            _, self.url = url.split("view-source:", 1)

        result = urlparse(self.url)
        self.scheme = result.scheme
        assert self.scheme in ["http", "https"]

        assert result.hostname is not None
        self.host = result.hostname
        self.path = result.path

        if result.port:
            self.port = result.port
        elif self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443

    # Ex. 1-7
    def _handle_redirect(self, location: str | None):
        if location is not None:
            if location.startswith("/"):
                self.path = location
            else:
                self._parse_url(location)
            self.request()

    # Ex. 1-8
    def _handle_cache(self, cache_control: str | None, content: str):
        cache_control_directives = parse_cache_control_header(cache_control)
        should_cache = cache_control_directives.get("no_store") is not None
        max_age = cache_control_directives.get("max_age", 0)
        if should_cache:
            browser_cache.add(self.url, content, int(max_age))

    def request(self):
        # Check cache for this URL first and return content immediately if found
        if browser_cache.has(self.url):
            return browser_cache.get(self.url)

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

        headers = make_headers(
            {"Host": self.host, "Connection": "close", "User-Agent": "python-browser"}
        )
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
            response_headers[header.lower()] = value.strip()

        # Don't handle compression and chunking for now
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        # Handle 3xx redirects
        if status.startswith("3"):
            location = response_headers.get("location")
            self._handle_redirect(location)

        content = response.read()

        # Handle caching GET 200 request results
        if status == "200":
            cache_control = response_headers.get("cache-control")
            self._handle_cache(cache_control, content)

        s.close()

        return content, self.should_view_source
