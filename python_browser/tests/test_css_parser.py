import unittest

from css.parser import CSSParser


class TestCSSParser(unittest.TestCase):
    def test_inline_style(self):
        styles = "background-color: red; color: yellow;"
        parser = CSSParser(text=styles)
        rules = parser.body()
        self.assertEqual(len(rules.keys()), 2)
        self.assertEqual(rules.get("background-color"), "red")
        self.assertEqual(rules.get("color"), "yellow")

    def test_inline_style_with_multiword_value(self):
        styles = "border: 1px solid black;"
        parser = CSSParser(text=styles)
        rules = parser.body()
        self.assertEqual(len(rules.keys()), 1)
        self.assertEqual(rules.get("border"), "1px solid black")

    def test_inline_style_with_extra_whitespace(self):
        styles = " color:    red  ; "
        parser = CSSParser(text=styles)
        rules = parser.body()
        self.assertEqual(len(rules.keys()), 1)
        self.assertEqual(rules.get("color"), "red")

    def test_inline_style_with_extra_chars(self):
        styles = "color: red;;"
        parser = CSSParser(text=styles)
        rules = parser.body()
        self.assertEqual(len(rules.keys()), 1)
        self.assertEqual(rules.get("color"), "red")

    def test_inline_style_with_invalid_char(self):
        styles = "color@: red;"
        parser = CSSParser(text=styles)
        rules = parser.body()
        self.assertEqual(len(rules.keys()), 0)
