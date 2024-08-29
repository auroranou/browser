from typing import Never, Self


Attributes = dict[str, str]


class Element:
    def __init__(self, tag: str, attributes: Attributes, parent: Self | None):
        self.tag: str = tag
        self.attributes: Attributes = attributes
        self.children: list[Node] = []
        self.parent: Element | None = parent
        self.style: dict[str, str] = {}

    def __repr__(self) -> str:
        return f"<{self.tag}>"


class Text:
    def __init__(self, text: str, parent: Element):
        self.text: str = text
        self.children: list[Never] = []
        self.parent: Element = parent
        self.style: dict[str, str] = {}

    def __repr__(self) -> str:
        return repr(self.text)


Node = Element | Text
