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
            url, b"HTTP/1.0 200 OK\r\n" + b"Header1: Value1\r\n\r\n" + b"abc def"
        )
        browser = Browser()
        browser.load(URL.create(url))
        self.assertEqual(len(browser.display_list), 2)

        word1 = browser.display_list[0]
        self.assertEqual(word1.x, HSTEP)
        self.assertEqual(word1.word, "abc")

        word2 = browser.display_list[1]
        self.assertGreater(word2.x, word1.x)
        self.assertEqual(word2.word, "def")

    def test_rtl(self):
        socket.patch().start()
        url = "http://browser.engineering/examples/example1-simple.html"
        socket.respond(
            url, b"HTTP/1.0 200 OK\r\n" + b"Header1: Value1\r\n\r\n" + b"abc def"
        )
        browser = Browser(rtl=True)
        browser.load(URL.create(url))
        self.assertEqual(len(browser.display_list), 2)

        word1 = browser.display_list[0]
        self.assertGreater(word1.x, HSTEP)
        self.assertEqual(word1.word, "abc")

    def test_superscript(self):
        socket.patch().start()
        url = "http://browser.engineering/examples/example1-simple.html"
        socket.respond(
            url,
            b"HTTP/1.0 200 OK\r\n"
            + b"Header1: Value1\r\n\r\n"
            + b"<div>abc <sup>def</sup></div>",
        )
        browser = Browser()
        browser.load(URL.create(url))
        self.assertEqual(len(browser.display_list), 2)

        word1 = browser.display_list[0]
        word2 = browser.display_list[1]
        self.assertEqual(word1.y, word2.y)

        ascent1 = word1.font.metrics().get("ascent")
        ascent2 = word2.font.metrics().get("ascent")
        self.assertGreater(ascent1, ascent2)
