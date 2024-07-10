import unittest
from unittest.mock import mock_open, patch

from python_browser.url import URL, DataURL, FileURL, HttpURL


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
        result = url.request()
        self.assertEqual(result, "Hello world!")

    def test_request_file_url(self):
        with patch("builtins.open", mock_open(read_data="data")):
            url = FileURL("file:///Users/test/file.pdf")
            result = url.request()
            self.assertEqual(result, "data")

    # def test_request_http_url(self):

    # def test_request_https_url(self):

    # def test_request_redirect(self):


if __name__ == "__main__":
    unittest.main()
