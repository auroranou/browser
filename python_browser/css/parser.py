from css.selectors import CSSRule, DescendantSelector, SelectorRule, TagSelector
from parser import Element, Node

INHERITED_PROPERTIES: CSSRule = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black",
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
            if self.curr_char.isalnum() or self.curr_char in "#-.%":
                self.i += 1
            else:
                break

        if not (self.i > start):
            raise Exception(f"Parsing error: {self.i} is not greater than {start}")

        return self.text[start : self.i]

    def consume_literal(self, literal: str):
        if not (self.more_to_parse() and self.curr_char == literal):
            raise Exception(f"Parsing error: {literal} not matched")

        self.i += 1

    def pair(self) -> tuple[str, str]:
        prop = self.consume_word()
        self.consume_whitespace()
        self.consume_literal(":")
        self.consume_whitespace()

        val = ""
        while self.curr_char != ";":
            val += self.consume_word()

            if self.curr_char.isspace():
                self.consume_whitespace()
                val += " "

        return prop.casefold(), val

    def body(self) -> dict[str, str]:
        pairs: dict[str, str] = {}
        while self.more_to_parse() and self.curr_char != "}":
            try:
                prop, val = self.pair()
                pairs[prop.casefold()] = val
                self.consume_whitespace()
                self.consume_literal(";")
                self.consume_whitespace()
            except Exception:
                why = self.ignore_until([";", "}"])
                if why == ";":
                    self.consume_literal(";")
                    self.consume_whitespace()
                elif why == "}":
                    self.consume_literal("}")
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

    def selector(self) -> TagSelector | DescendantSelector:
        out = TagSelector(self.consume_word().casefold())
        self.consume_whitespace()

        while self.more_to_parse() and self.curr_char != "{":
            tag = self.consume_word()
            descendant = TagSelector(tag.casefold())
            out = DescendantSelector(out, descendant)
            self.consume_whitespace()

        return out

    def parse(self) -> list[SelectorRule]:
        rules = []

        while self.more_to_parse():
            self.consume_whitespace()
            selector = self.selector()
            self.consume_literal("{")
            self.consume_whitespace()
            body = self.body()
            self.consume_literal("}")
            rules.append((selector, body))

        return rules


DEFAULT_STYLE_SHEET = CSSParser(open("browser.css").read()).parse()


def style(node: Node, rules: list[SelectorRule]):
    # Apply any inherited styles
    for property, default_value in INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[property] = node.parent.style[property]
        else:
            node.style[property] = default_value

    # Handle stylesheets
    for selector, body in rules:
        if not selector.matches(node):
            continue
        for property, value in body.items():
            node.style[property] = value

    # Handle inline styles, which override stylesheet CSS rules
    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).body()
        for prop, val in pairs.items():
            node.style[prop] = val

    # Resolve final font sizes
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
