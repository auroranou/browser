from css.selectors import CSSRule, DescendantSelector, SelectorRule, TagSelector
from parser import Element, Node

INHERITED_PROPERTIES: CSSRule = {
    "color": "black",
    "font-family": "AppleUI",
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
}


class CSSParser:
    def __init__(self, text: str):
        self.text = text.strip()
        self.i = 0

    @property
    def curr_char(self) -> str:
        return self.text[self.i]

    def more_to_parse(self) -> bool:
        return self.i < len(self.text)

    def consume_whitespace(self):
        while self.more_to_parse() and self.curr_char.isspace():
            self.i += 1

    def consume_word(self) -> str:
        start = self.i

        while self.more_to_parse():
            if self.curr_char.isalnum() or self.curr_char in '#-.%"':
                self.i += 1
            else:
                break

        if not (self.i > start):
            raise Exception(f"Parsing error: {self.i} is not greater than {start}")

        return self.text[start : self.i]

    def consume_literal(self, literal: str):
        if self.more_to_parse() and self.curr_char == literal:
            self.i += 1
        else:
            raise Exception(f"Parsing error: {literal} not matched")

    def parse_declaration(self) -> tuple[str, str]:
        prop = self.consume_word()
        self.consume_whitespace()
        self.consume_literal(":")
        self.consume_whitespace()

        # CSS values may be multiple words, separated by whitespace
        val = ""
        while self.curr_char != ";":
            val += self.consume_word()

            if self.curr_char.isspace():
                self.consume_whitespace()
                val += " "

        return prop.casefold(), val.strip()

    def parse_declaration_block(self) -> dict[str, str]:
        pairs: dict[str, str] = {}

        while self.more_to_parse() and self.curr_char != "}":
            try:
                prop, val = self.parse_declaration()
                pairs[prop.casefold()] = val
                self.consume_whitespace()
                self.consume_literal(";")
                self.consume_whitespace()
            except Exception:
                why = self.ignore_until([";", "}"])
                if why == ";":
                    self.consume_literal(";")
                    self.consume_whitespace()
                else:
                    break

        return pairs

    def ignore_until(self, chars: list[str]) -> str | None:
        while self.more_to_parse():
            if self.curr_char in chars:
                return self.curr_char
            else:
                self.i += 1

        return None

    def parse_selector(self) -> TagSelector | DescendantSelector:
        out = TagSelector(self.consume_word().casefold())
        self.consume_whitespace()

        while self.more_to_parse() and self.curr_char != "{":
            tag = self.consume_word()
            descendant = TagSelector(tag.casefold())
            out = DescendantSelector(out, descendant)
            self.consume_whitespace()

        return out

    def parse(self) -> list[SelectorRule]:
        rules: list[SelectorRule] = []

        while self.more_to_parse():
            try:
                self.consume_whitespace()
                selector = self.parse_selector()
                self.consume_literal("{")
                self.consume_whitespace()
                body = self.parse_declaration_block()
                self.consume_literal("}")
                rules.append((selector, body))
            except Exception:
                why = self.ignore_until(["}"])
                if why == "}":
                    self.consume_literal("}")
                    self.consume_whitespace()
                else:
                    break

        return rules


def get_default_stylesheet() -> list[SelectorRule]:
    with open("browser.css", "r") as file:
        text = file.read()
        return CSSParser(text).parse()


def style(node: Node, rules: list[SelectorRule]):
    # Apply any inherited styles to the node first
    for property, default_value in INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[property] = node.parent.style[property]
        else:
            node.style[property] = default_value

    # Then handle custom stylesheets
    for selector, body in rules:
        if not selector.matches(node):
            continue
        if isinstance(node, Element) and node.tag in ["html", "head"]:
            continue
        for property, value in body.items():
            node.style[property] = value

    # Then handle inline styles, which override stylesheet CSS rules
    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).parse_declaration_block()
        for prop, val in pairs.items():
            node.style[prop] = val

    # HACK tkinter expects a single font-family, so grab the first one
    if node.style["font-family"]:
        font_family = node.style["font-family"].split(",")[0]
        font_family = font_family.replace('"', "").replace("'", "")
        node.style["font-family"] = font_family

    # Compute final font sizes for percentage size values
    if node.style["font-size"].endswith("%"):
        if node.parent:
            parent_font_size = node.parent.style["font-size"]
        else:
            parent_font_size = INHERITED_PROPERTIES["font-size"]

        node_pct = float(node.style["font-size"][:-1]) / 100
        parent_px = float(parent_font_size[:-2])
        node.style["font-size"] = str(node_pct * parent_px) + "px"

    for child in node.children:
        style(child, rules)
