from abc import ABC, abstractmethod
import gzip
from io import BufferedReader
import socket
import ssl
from typing import Self
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

    @abstractmethod
    def resolve(self, url: str) -> Self:
        pass


class URL:
    @staticmethod
    def create(url: str):
        if url.startswith("data:"):
            return DataURL(url)
        elif url.startswith("file:"):
            return FileURL(url)
        # Ex. 2-6
        elif url.startswith("about:blank"):
            return FileURL("blank.html")
        else:
            return HttpURL(url)


# Ex. 1-3
class DataURL(AbstractURL):
    def __init__(self, url: str):
        self.url = url
        self.scheme, self.path = url.split(",", 1)

    def request(self) -> tuple[str, bool]:
        return self.path, False

    def resolve(self, url: str) -> "DataURL":
        return DataURL(url)


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

    def resolve(self, url: str) -> "FileURL":
        return FileURL(url)


class HttpURL(AbstractURL):
    def __init__(self, url: str):
        self._parse_url(url)

    def _parse_url(self, url: str):
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

    def _connect(self) -> ssl.SSLSocket | socket.socket:
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

        return s

    def _build_request(self) -> str:
        headers = make_headers(
            {
                "Accept-Encoding": "gzip",
                "Connection": "close",
                "Host": self.host,
                "User-Agent": "python-browser",
            }
        )
        request = f"GET {self.path} HTTP/1.1\r\n{headers}\r\n"
        return request

    def _parse_response_headers(self, response: BufferedReader):
        response_headers = {}
        while True:
            line = response.readline().decode("utf-8")
            if line == "\r\n":
                break
            header, value = line.split(":", 1)
            # Headers are case-insensitive, whitespace doesn't matter
            response_headers[header.lower()] = value.strip()
        return response_headers

    # Ex. 1-7
    def _handle_redirect(self, location: str | None):
        if location is not None:
            if location.startswith("/"):
                self.path = location
            else:
                self._parse_url(location)
            return self.request()

    # Ex. 1-9
    def _read_chunks(self, response: BufferedReader):
        content = b""
        while True:
            line = response.readline()
            chunk_size = int(line, 16)  # Size is first line, represented in hex

            # Final chunk always has length of 0
            if chunk_size == 0:
                break
            content += response.read(chunk_size)
            # Each chunk ends in `/r/n`, which needs to be read
            response.read(2)

        return content

    # Ex. 1-8
    def _cache_response(self, cache_control: str | None, content: str):
        cache_control_directives = parse_cache_control_header(cache_control)
        should_cache = "no_store" in cache_control_directives
        max_age = cache_control_directives.get("max_age", 0)
        if should_cache:
            browser_cache.add(self.url, content, int(max_age))

    def resolve(self, url: str) -> "HttpURL":
        if "://" in url:
            return HttpURL(url)

        if not url.startswith("/"):
            dir, _ = self.path.rsplit("/", 1)
            while url.startswith("../"):
                _, url = url.split("/", 1)
                if "/" in dir:
                    dir, _ = dir.rsplit("/", 1)
            url = dir + "/" + url

        if url.startswith("//"):
            return HttpURL(self.scheme + ":" + url)
        else:
            return HttpURL(self.scheme + "://" + self.host + ":" + str(self.port) + url)

    def request(self) -> tuple[str, bool]:
        # Check cache for this URL first and return content immediately if found
        if browser_cache.has(self.url):
            body = browser_cache.get(self.url)
            if body:
                return body, False

        s = self._connect()
        request = self._build_request()
        s.send(request.encode("utf8"))

        # Write response bytes to a file-like object, handling HTTP line endings
        response = s.makefile("rb", newline="\r\n")

        # Read out response parts; status line is first line
        statusline = response.readline().decode("utf-8")
        version, status, explanation = statusline.split(" ", 2)
        response_headers = self._parse_response_headers(response)

        # Handle 3xx redirects
        if status.startswith("3") and "location" in response_headers:
            content = self._handle_redirect(response_headers.get("location"))
            if content:
                return content

        # Handle decompression and chunking
        if response_headers.get("content-encoding") == "gzip":
            if response_headers.get("transfer-encoding") == "chunked":
                content_bytes = self._read_chunks(response)
                content = gzip.decompress(content_bytes).decode("utf-8")
            else:
                content = gzip.decompress(response.read()).decode("utf-8")
        else:
            content = response.read().decode("utf-8")

        # Handle caching results for GET 200 requests
        if status == "200":
            cache_control = response_headers.get("cache-control")
            self._cache_response(cache_control, content)

        s.close()

        return content, self.should_view_source
