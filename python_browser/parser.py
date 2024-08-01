from typing import Literal, Never, Self

from constants import HEAD_TAGS, SELF_CLOSING_TAGS

Attributes = dict[str, str]


class Element:
    def __init__(self, tag: str, attributes: Attributes, parent: Self | None):
        self.tag: str = tag
        self.attributes: Attributes = attributes
        self.children: list[Node] = []
        self.parent: Element | None = parent

    def __repr__(self) -> str:
        return f"<{self.tag}>"


class Text:
    def __init__(self, text: str, parent: Element):
        self.text: str = text
        self.children: list[Never] = []
        self.parent: Element = parent

    def __repr__(self) -> str:
        return repr(self.text)


Node = Element | Text


class HTMLParser:
    def __init__(self, body: str):
        self.body: str = body
        self.unfinished: list[Element] = []
        self.i = 0

    def peek(self, num_chars=0) -> str | None:
        end_idx = self.i + 1 + num_chars

        if end_idx < len(self.body):
            return self.body[self.i + 1 : end_idx]

        return None

    def step(self, step_size=1):
        self.i += step_size

    def consume_until(self, target: str):
        end_idx = self.i + len(target)

        if end_idx >= len(self.body):
            return False

        if self.body[self.i : end_idx] == target:
            self.i = end_idx
            return True

        self.i += 1
        self.consume_until(target)

    def parse(self):
        buffer = ""
        in_tag = False
        in_comment = False

        while self.i < len(self.body):
            c = self.body[self.i]
            if c == "<":
                # Ex. 4-1: Don't process comments as nodes
                if self.peek(3) == "!--":
                    in_comment = True
                    self.step(4)
                    self.consume_until("-->")
                    in_comment = False
                else:
                    in_tag = True
                    if buffer:
                        self.add_text(buffer)
                    buffer = ""
                    self.step()
            elif c == ">":
                if not in_comment:
                    in_tag = False
                    self.add_tag(buffer)
                    buffer = ""
                self.step()
            elif c == "&":
                if self.peek(3) == "lt;":
                    buffer += "<"
                    self.step(4)
                elif self.peek(3) == "gt;":
                    buffer += ">"
                    self.step(4)
                elif self.peek(4) == "shy;":
                    buffer += "\N{soft hyphen}"
                    self.step(5)
                else:
                    buffer += c
                    self.step()
            else:
                buffer += c
                self.step()

        if not in_tag and buffer:
            self.add_text(buffer)

        return self.finish()

    def add_tag(self, tag: str):
        tag, attributes = self.get_attributes(tag)

        if tag.startswith("!"):
            return

        self.implicit_tags(tag)

        if tag.startswith("/"):
            if len(self.unfinished) == 1:
                return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        elif tag in SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)
            parent.children.append(node)
        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, attributes, parent)
            self.unfinished.append(node)

    def add_text(self, text: str):
        if text.isspace():
            return

        self.implicit_tags(None)
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    def get_attributes(self, text) -> tuple[str, Attributes]:
        parts = text.split()
        tag = parts[0].casefold()
        attributes = {}
        for attrpair in parts[1:]:
            if "=" in attrpair:
                key, value = attrpair.split("=", 1)
                if len(value) > 2 and value[0] in ["'", '"']:
                    value = value[1:-1]
                attributes[key.casefold()] = value
            else:
                attributes[attrpair.casefold()] = ""
        return tag, attributes

    def implicit_tags(self, tag: str | None):
        while True:
            open_tags = [node.tag for node in self.unfinished]
            if open_tags == [] and tag != "html":
                self.add_tag("html")
            elif open_tags == ["html"] and tag not in ["head", "body", "/html"]:
                if tag in HEAD_TAGS:
                    self.add_tag("head")
                else:
                    self.add_tag("body")
            elif open_tags == ["html", "head"] and tag not in ["/head"] + HEAD_TAGS:
                self.add_tag("/head")
            else:
                break

    def finish(self):
        if not self.unfinished:
            self.implicit_tags(None)

        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)

        return self.unfinished.pop()


def print_tree(node: Node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)
