import unittest
from unittest.mock import mock_open, patch

from url import URL, DataURL, FileURL, HttpURL
from tests.utils import socket, ssl


class TestURL(unittest.TestCase):
    def test_url_creation(self):
        url = URL.create("http://browser.engineering/examples/example1-simple.html")
        self.assertEqual(url.scheme, "http")
        url = URL.create("https://browser.engineering/examples/example1-simple.html")
        self.assertEqual(url.scheme, "https")
        url = URL.create("file:///Users/test/file.pdf")
        self.assertEqual(url.scheme, "file")
        url = URL.create("data:text/html,Hello world!")
        self.assertEqual(url.scheme, "data:text/html")

    def test_parse_http_success(self):
        url = HttpURL("http://browser.engineering/examples/example1-simple.html")
        self.assertEqual(url.host, "browser.engineering")
        self.assertEqual(url.path, "/examples/example1-simple.html")
        self.assertEqual(url.port, 80)

    def test_parse_https_success(self):
        url = HttpURL("https://browser.engineering/examples/example1-simple.html")
        self.assertEqual(url.host, "browser.engineering")
        self.assertEqual(url.path, "/examples/example1-simple.html")
        self.assertEqual(url.port, 443)

    def test_parse_file_success(self):
        url = FileURL("file:///Users/test/file.pdf")
        self.assertEqual(url.scheme, "file")
        self.assertEqual(url.path, "/Users/test/file.pdf")

    def test_request_data_url(self):
        url = DataURL("data:text/html,Hello world!")
        body, _ = url.request()
        self.assertEqual(body, "Hello world!")

    def test_request_file_url(self):
        with patch("builtins.open", mock_open(read_data="data")):
            url = FileURL("file:///Users/test/file.pdf")
            body, _ = url.request()
            self.assertEqual(body, "data")

    def test_request_http_url(self):
        socket.patch().start()
        url = "http://browser.engineering/examples/example1-simple.html"
        socket.respond(
            url, b"HTTP/1.0 200 OK\r\n" + b"Header1: Value1\r\n\r\n" + b"Body text"
        )
        body, _ = HttpURL(url).request()
        assert body == "Body text"

    def test_request_https_url(self):
        socket.patch().start()
        ssl.patch().start()
        url = "https://browser.engineering/examples/example1-simple.html"
        socket.respond(
            url, b"HTTP/1.0 200 OK\r\n" + b"Header1: Value1\r\n\r\n" + b"Body text"
        )
        body, _ = HttpURL(url).request()
        assert body == "Body text"

    def test_request_redirect(self):
        socket.patch().start()
        ssl.patch().start()
        orig_url = "http://browser.engineering/redirect"
        final_url = "https://browser.engineering/http.html"
        socket.respond(
            orig_url,
            b"HTTP/1.0 301 Moved permanently\r\n"
            + b"Location:https://browser.engineering/http.html\r\n\r\n",
        )
        socket.respond(
            final_url,
            b"HTTP/1.0 200 OK\r\n" + b"Header1: Value1\r\n\r\n" + b"Body text",
        )
        body, _ = HttpURL(orig_url).request()
        assert body == "Body text"


if __name__ == "__main__":
    unittest.main()
