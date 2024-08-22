from typing import cast
import unittest

from css.parser import CSSParser
from css.selectors import DescendantSelector, TagSelector


class TestCSSParser(unittest.TestCase):
    def test_parse_inline_style(self):
        styles = "background-color: red; color: yellow;"
        parser = CSSParser(text=styles)
        rules = parser.parse_declaration_block()
        self.assertEqual(len(rules.keys()), 2)
        self.assertEqual(rules.get("background-color"), "red")
        self.assertEqual(rules.get("color"), "yellow")

    def test_parse_inline_style_with_multiword_value(self):
        styles = "border: 1px solid black;"
        parser = CSSParser(text=styles)
        rules = parser.parse_declaration_block()
        self.assertEqual(len(rules.keys()), 1)
        self.assertEqual(rules.get("border"), "1px solid black")

    def test_parse_inline_style_with_extra_whitespace(self):
        styles = " color:    red  ; "
        parser = CSSParser(text=styles)
        rules = parser.parse_declaration_block()
        self.assertEqual(len(rules.keys()), 1)
        self.assertEqual(rules.get("color"), "red")

    def test_parse_inline_style_with_extra_chars(self):
        styles = "color: red;;"
        parser = CSSParser(text=styles)
        rules = parser.parse_declaration_block()
        self.assertEqual(len(rules.keys()), 1)
        self.assertEqual(rules.get("color"), "red")

    def test_parse_inline_style_with_invalid_char(self):
        styles = "color@: red;"
        parser = CSSParser(text=styles)
        rules = parser.parse_declaration_block()
        self.assertEqual(len(rules.keys()), 0)

    def test_parse_stylesheet(self):
        styles = "body { font-family: sans-serif; }"
        parser = CSSParser(text=styles)
        selector_rules = parser.parse()
        self.assertEqual(len(selector_rules), 1)

        selector, rule = selector_rules[0]
        self.assertIsInstance(selector, TagSelector)
        self.assertEqual(cast(TagSelector, selector).tag, "body")
        self.assertEqual(rule.get("font-family"), "sans-serif")

    def test_parse_media_query(self):
        # For now, media queries are not supported and we expect this to render nothing
        styles = """
            @media (max-width: 1250px) {
                body {
                    font-size: 12;
                }
            }
        """
        parser = CSSParser(text=styles)
        selector_rules = parser.parse()
        self.assertEqual(len(selector_rules), 0)

    def test_parse_user_agent_stylesheet(self):
        with open("browser.css", "r") as file:
            parser = CSSParser(text=file.read())
            selector_rules = parser.parse()
            self.assertEqual(len(selector_rules), 8)

    def test_parse_descendant_selector(self):
        styles = "h1 a { color: red; }"
        parser = CSSParser(text=styles)
        selector_rules = parser.parse()
        self.assertEqual(len(selector_rules), 1)

        selector, rule = selector_rules[0]
        self.assertIsInstance(selector, DescendantSelector)
        self.assertEqual(rule.get("color"), "red")

        ancestor = cast(DescendantSelector, selector).ancestor
        descendant = cast(DescendantSelector, selector).descendant
        self.assertEqual(cast(TagSelector, ancestor).tag, "h1")
        self.assertEqual(cast(TagSelector, descendant).tag, "a")
