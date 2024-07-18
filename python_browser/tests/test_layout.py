import unittest

from python_browser.browser import Browser
from python_browser.constants import HSTEP, WIDTH
from python_browser.tests.utils import socket
from python_browser.url import URL


class TestLayout(unittest.TestCase):
    def test_load(self):
        socket.patch().start()
        url = "http://browser.engineering/examples/example1-simple.html"
        socket.respond(
            url, b"HTTP/1.0 200 OK\r\n" + b"Header1: Value1\r\n\r\n" + b"abc"
        )
        browser = Browser()
        browser.load(URL.create(url))
        self.assertEqual(len(browser.display_list), 3)

        x, _, text = browser.display_list[0]
        self.assertEqual(x, HSTEP)
        self.assertEqual(text, "a")

    def test_rtl(self):
        socket.patch().start()
        url = "http://browser.engineering/examples/example1-simple.html"
        socket.respond(
            url, b"HTTP/1.0 200 OK\r\n" + b"Header1: Value1\r\n\r\n" + b"abc"
        )
        browser = Browser(rtl=True)
        browser.load(URL.create(url))
        self.assertEqual(len(browser.display_list), 3)

        x, _, text = browser.display_list[0]
        self.assertEqual(x, WIDTH - HSTEP)
        self.assertEqual(text, "a")
