from typing import cast
import unittest

from browser import Browser
from constants import HSTEP, VSTEP, WIDTH
from layout.commands import DrawRect, DrawText
from tests.utils import socket
from url import URL


def get_text(cmd: DrawText | DrawRect):
    assert isinstance(cmd, DrawText)
    return cmd.text


def get_font(cmd: DrawText | DrawRect):
    assert isinstance(cmd, DrawText)
    return cmd.font


def get_font_metric(cmd: DrawText | DrawRect, metric_name: str):
    font = get_font(cmd)
    return font.metrics()[metric_name]


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

        cmd1, cmd2 = browser.display_list[:2]
        self.assertEqual(cmd1.left, HSTEP)
        self.assertEqual(get_text(cmd1), "abc")
        self.assertGreater(cmd2.left, cmd1.left)
        self.assertEqual(get_text(cmd2), "def")

    def test_rtl(self):
        browser = self._init_browser("abc def", rtl=True)
        self.assertEqual(len(browser.display_list), 2)

        cmd1 = browser.display_list[0]
        self.assertGreater(cmd1.left, HSTEP)
        self.assertEqual(get_text(cmd1), "abc")

    def test_center_title(self):
        browser = self._init_browser('<h1 class="title">abc</h1><div>def</div>')
        self.assertEqual((len(browser.display_list)), 2)

        cmd1, cmd2 = browser.display_list[:2]
        # First word should be centered, so x coord is greater than default
        self.assertGreater(cmd1.left, HSTEP)
        # Second word should be on a new line
        self.assertGreater(cmd2.top, cmd1.top)

    def test_superscript(self):
        browser = self._init_browser("<div>abc <sup>def</sup></div>")
        self.assertEqual(len(browser.display_list), 2)

        cmd1, cmd2 = browser.display_list[:2]
        self.assertEqual(cmd1.top, cmd2.top)

        ascent1 = get_font_metric(cmd1, "ascent")
        ascent2 = get_font_metric(cmd2, "ascent")
        self.assertGreater(ascent1, ascent2)

    def test_abbr(self):
        browser = self._init_browser("<abbr>Hello World 123</abbr>")
        self.assertEqual(len(browser.display_list), 13)

        normal_char, abbr_char = browser.display_list[:2]
        self.assertGreater(
            get_font_metric(normal_char, "ascent"),
            get_font_metric(abbr_char, "ascent"),
        )

        for char in browser.display_list:
            if isinstance(char, DrawText) and char.text.isalpha():
                self.assertTrue(char.text.isupper())

    def test_pre(self):
        browser = self._init_browser("<pre>abc\n\n<b>d  ef</b></pre>")
        self.assertEqual(len(browser.display_list), 4)

        for item in browser.display_list:
            if isinstance(item, DrawText):
                self.assertEqual(get_font(item)["family"], "Courier New")
            else:
                self.assertIsInstance(item, DrawRect)

        _, abc, d, ef = browser.display_list
        self.assertEqual(get_font(abc)["weight"], "normal")
        self.assertEqual(get_font(d)["weight"], "bold")
        self.assertEqual(get_font(ef)["weight"], "bold")

        # 2 newlines should be preserved between 'abc' and 'd'
        self.assertGreaterEqual(d.top - abc.top, VSTEP * 2)

        # 2 spaces should be preserved between 'd' and 'ef'
        self.assertGreaterEqual(ef.left - d.left, get_font(d).measure(" ") * 2)
