import unittest

from python_browser.browser import Browser
from python_browser.constants import HSTEP, VSTEP, WIDTH
from python_browser.tests.utils import socket
from python_browser.url import URL


class TestLayout(unittest.TestCase):
    def _init_browser(self, response_body: str, rtl: bool = False):
        socket.patch().start()
        url = "http://browser.engineering/example.html"
        socket.respond(
            url,
            b"HTTP/1.0 200 OK\r\n"
            + b"Header1: Value1\r\n\r\n"
            + bytes(response_body, encoding="utf-8"),
        )
        browser = Browser(rtl)
        browser.load(URL.create(url))
        return browser

    def test_load(self):
        browser = self._init_browser("abc def")
        self.assertEqual(len(browser.display_list), 2)

        word1, word2 = browser.display_list[:2]
        self.assertEqual(word1.x, HSTEP)
        self.assertEqual(word1.word, "abc")
        self.assertGreater(word2.x, word1.x)
        self.assertEqual(word2.word, "def")

    def test_rtl(self):
        browser = self._init_browser("abc def", rtl=True)
        self.assertEqual(len(browser.display_list), 2)

        word1 = browser.display_list[0]
        self.assertGreater(word1.x, HSTEP)
        self.assertEqual(word1.word, "abc")

    def test_center_title(self):
        browser = self._init_browser('<h1 class="title">abc</h1><div>def</div>')
        self.assertEqual((len(browser.display_list)), 2)

        word1, word2 = browser.display_list[:2]
        # First word should be centered, so x coord is greater than default
        self.assertGreater(word1.x, HSTEP)
        # Second word should be on a new line
        self.assertGreater(word2.y, word1.y)

    def test_superscript(self):
        browser = self._init_browser("<div>abc <sup>def</sup></div>")
        self.assertEqual(len(browser.display_list), 2)

        word1, word2 = browser.display_list[:2]
        self.assertEqual(word1.y, word2.y)

        ascent1 = word1.font.metrics().get("ascent")
        ascent2 = word2.font.metrics().get("ascent")
        self.assertGreater(ascent1, ascent2)

    def test_abbr(self):
        browser = self._init_browser("<abbr>Hello World 123</abbr>")
        self.assertEqual(len(browser.display_list), 13)

        normal_char, abbr_char = browser.display_list[:2]
        self.assertGreater(
            normal_char.font.metrics().get("ascent"),
            abbr_char.font.metrics().get("ascent"),
        )

        for char in browser.display_list:
            if char.word.isalpha():
                self.assertTrue(char.word.isupper())

    def test_pre(self):
        browser = self._init_browser("<pre>abc\n\n<b>d  ef</b></pre>")
        self.assertEqual(len(browser.display_list), 3)

        for word in browser.display_list:
            self.assertEqual(word.font.cget("family"), "Courier New")

        abc, d, ef = browser.display_list[:3]
        self.assertEqual(abc.font.cget("weight"), "normal")
        self.assertEqual(d.font.cget("weight"), "bold")
        self.assertEqual(ef.font.cget("weight"), "bold")

        # 2 newlines should be preserved between 'abc' and 'd'
        self.assertGreaterEqual(d.y - abc.y, VSTEP * 2)

        # 2 spaces should be preserved between 'd' and 'ef'
        self.assertGreaterEqual(ef.x - d.x, d.font.measure(" ") * 2)
