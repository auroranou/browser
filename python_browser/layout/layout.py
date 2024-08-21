from abc import ABC, abstractmethod
from dataclasses import dataclass
import tkinter.font
from typing import Literal, Self

from constants import BLOCK_ELEMENTS, HSTEP, VSTEP, WIDTH
from layout.commands import DrawRect, DrawText
from layout.fonts import FontStyle, FontWeight, get_font
from parser import Attributes, Element, Node, Text

TextAlign = Literal["right", "left", "center"]


@dataclass
class LineItem:
    color: str
    font: tkinter.font.Font
    x: float
    valign: str
    word: str


@dataclass
class DisplayListItem(LineItem):
    y: float


class AbstractLayout(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def layout(self):
        pass

    @abstractmethod
    def paint(self):
        pass


# Root of layout tree
class DocumentLayout(AbstractLayout):
    def __init__(self, node: Element, width: float = WIDTH, rtl: bool = False):
        self.node = node
        self.parent = None
        self.children: list[BlockLayout] = []

        self.x = HSTEP
        self.y = VSTEP
        self.width = width
        self.height = 0
        self.rtl = rtl

    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        child.layout()
        self.height = child.height

    def paint(self):
        return []


class BlockLayout(AbstractLayout):
    def __init__(
        self,
        node: Node,
        parent: DocumentLayout | Self,
        previous: Self | None,
    ):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children: list[BlockLayout] = []
        self.display_list: list[DisplayListItem] = []

        # Attributes below are used for inline text layout only
        self.cursor_x = 0
        self.cursor_y = 0
        self.text_align: TextAlign = "right" if parent.rtl else "left"

        self.in_abbr_tag = False
        self.in_pre_tag = False
        self.in_sup_tag = False

        self.line: list[LineItem] = []

    def has_block_children(self) -> bool:
        return any(
            isinstance(child, Element) and child.tag in BLOCK_ELEMENTS
            for child in self.node.children
        )

    def is_matching_element(self, tag: str) -> bool:
        return isinstance(self.node, Element) and self.node.tag == tag

    def has_css_class(self, class_name: str) -> bool:
        return (
            isinstance(self.node, Element)
            and "class" in self.node.attributes
            and class_name in self.node.attributes["class"]
        )

    def get_font_from_node(self, node: Node) -> tkinter.font.Font:
        size = int(float(node.style["font-size"][:-2]) * 0.75)
        return get_font(
            size,
            node.style["font-weight"],
            node.style["font-style"],
            node.style["font-family"],
        )

    def layout_mode(self) -> Literal["inline"] | Literal["block"]:
        if isinstance(self.node, Text):
            return "inline"
        if self.has_block_children():
            return "block"
        elif self.node.children:
            return "inline"
        else:
            return "block"

    def layout(self):
        self.x = self.parent.x
        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        self.width = self.parent.width
        self.rtl = self.parent.rtl

        mode = self.layout_mode()
        if mode == "block":
            previous = None
            for child in self.node.children:
                if isinstance(child, Element) and child.tag == "head":
                    continue
                next = BlockLayout(child, self, previous)
                self.children.append(next)
                previous = next
        else:

            # Ex. 5-3: Indent text for bulleted list items
            if isinstance(self.parent.node, Element) and self.parent.node.tag in [
                "ul",
                "ol",
            ]:
                self.cursor_x += 8

            self.recurse(self.node)
            self.flush()

        for child in self.children:
            child.layout()

        if mode == "block":
            self.height = sum([child.height for child in self.children])
        else:
            self.height = self.cursor_y

    def recurse(self, tree: Node):
        if isinstance(tree, Text):
            # Ex. 3-5
            if self.in_pre_tag:
                # Split on newline to preserve internal whitespace
                for line in tree.text.split("\n"):
                    self._handle_pre(tree, line)
            else:
                for word in tree.text.split():
                    self.word(tree, word)
        elif isinstance(tree, Element):
            for child in tree.children:
                self.recurse(child)

    # Ex. 3-4
    def _handle_abbr(self, node: Node, word: str):
        size = int(float(node.style["font-size"][:-2]) * 0.75)
        # Inside an <abbr> tag, lower-case letters should be small, capitalized, and bold,
        abbr_font = get_font(size, "bold", "roman")
        # while all other characters (upper case, numbers, etc.) should be drawn in the normal font
        curr_font = get_font(size, node.style["font-weight"], node.style["font-style"])

        # If the <abbr> word won't fit on the current line, flush first
        word_w = curr_font.measure(word)
        if self.cursor_x + word_w > self.width - HSTEP:
            self.flush()

        # Measure and append individual characters since they may vary
        for char in word:
            if char.isupper() or char.isnumeric():
                char_w = curr_font.measure(char)
                self.line.append(
                    LineItem(
                        x=self.cursor_x,
                        word=char,
                        font=curr_font,
                        color=node.style["color"],
                        valign="top" if self.in_sup_tag else "baseline",
                    )
                )
            else:
                char_w = abbr_font.measure(char)
                self.line.append(
                    LineItem(
                        x=self.cursor_x,
                        word=char.upper(),
                        font=abbr_font,
                        color=node.style["color"],
                        valign="top" if self.in_sup_tag else "baseline",
                    )
                )

            self.cursor_x += char_w

        self.cursor_x += curr_font.measure(" ")

    # Ex. 3-5
    def _handle_pre(self, node: Text, line: str):
        size = int(float(node.style["font-size"][:-2]) * 0.75)
        font = get_font(
            size,
            node.style["font-weight"],
            node.style["font-style"],
            node.style["font-family"],
        )
        if len(line):
            words = line.split(" ")
            for word in words:
                if len(word):
                    self.word(node, word)
                else:
                    self.cursor_x += font.measure(" ")

            self.flush()
        else:
            # Because of how we split the text token inside of <pre>, an 'empty' line = newline
            # Increment by VSTEP to mimic a newline instead of fiddling with font metrics
            self.cursor_y += VSTEP
            self.cursor_x = 0

    def word(self, node: Text, word: str):
        if self.in_abbr_tag:
            self._handle_abbr(node, word)
            return

        size = int(float(node.style["font-size"][:-2]) * 0.75)
        font = get_font(
            size,
            node.style["font-weight"],
            node.style["font-style"],
            family=node.style["font-family"],
        )
        w = font.measure(word)

        if self.cursor_x + w > self.width - HSTEP:
            if "&shy;" in word:
                for substring in word.split("&shy;"):
                    self.word(node, substring)
                return
            else:
                self.flush()

        self.line.append(
            LineItem(
                x=self.cursor_x,
                word=word,
                font=font,
                color=node.style["color"],
                valign=node.style["vertical-align"],
            )
        )
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line:
            return

        metrics = [item.font.metrics() for item in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        for item in self.line:
            x = self.x + item.x
            y = self.y + baseline - item.font.metrics("ascent")

            # Ex. 3-2
            if item.valign == "top":
                y = self.y + baseline - max_ascent

            # Ex. 2-7
            if self.text_align == "right":
                x_offset = self.width - self.cursor_x
                x += x_offset
            # Ex. 3-1
            elif self.text_align == "center":
                x_offset = (self.width - self.cursor_x) / 2
                x += x_offset

            self.display_list.append(
                DisplayListItem(
                    x=x,
                    y=y,
                    word=item.word,
                    font=item.font,
                    color=item.color,
                    valign=item.valign,
                )
            )

        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = 0
        self.line = []

    def paint(self):
        cmds: list[DrawRect | DrawText] = []

        if self.is_matching_element("pre"):
            cmds.append(
                DrawRect(
                    left=self.x,
                    top=self.y,
                    right=self.x + self.width,
                    bottom=self.y + self.height,
                    color="gray",
                )
            )

        if self.is_matching_element("nav") and self.has_css_class("links"):
            cmds.append(
                DrawRect(
                    left=self.x,
                    top=self.y,
                    right=self.x + self.width,
                    bottom=self.y + self.height,
                    color="lightgray",
                )
            )

        # Ex. 5-3
        if self.is_matching_element("li"):
            BULLET_SIZE = 4
            line_height = (
                self.display_list[0].font.metrics()["linespace"]
                if len(self.display_list)
                else self.cursor_y
            )

            cmds.append(
                DrawRect(
                    left=self.x,
                    top=self.y + line_height / 2,
                    right=self.x + BULLET_SIZE,
                    bottom=self.y + line_height / 2 + BULLET_SIZE,
                    color="black",
                )
            )

        if self.layout_mode() == "inline":
            for item in self.display_list:
                cmds.append(
                    DrawText(
                        left=item.x,
                        top=item.y,
                        text=item.word,
                        font=item.font,
                        color=item.color,
                    )
                )

        return cmds


def paint_tree(
    layout_object: DocumentLayout | BlockLayout, display_list: list[DrawText | DrawRect]
):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)
