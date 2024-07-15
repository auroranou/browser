import tkinter.font
from typing import Literal, Union

from constants import HSTEP, VSTEP, WIDTH
from fonts import get_font
from html_lexer import Tag, Text

# X position (right), word, font
LineItem = tuple[float, str, tkinter.font.Font]

# X position (right), Y position (bottom), word, font
DisplayListItem = tuple[float, float, str, tkinter.font.Font]


class Layout:
    def __init__(
        self, tokens: list[Tag | Text], width: float = WIDTH, rtl: bool = False
    ):
        self.rtl = rtl
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.size = 12
        self.style: Literal["roman", "italic"] = "roman"
        self.weight: Literal["normal", "bold"] = "normal"

        self.line: list[LineItem] = []
        self.display_list: list[DisplayListItem] = []

        self.height = self.cursor_y
        self.width = width

        for t in tokens:
            self.token(t)

        self.flush()

    def token(self, token: Tag | Text):
        if isinstance(token, Text):
            for word in token.text.split():
                self.word(word)
        elif isinstance(token, Tag):
            if token.tag == "i":
                self.style = "italic"
            elif token.tag == "/i":
                self.style = "roman"
            elif token.tag == "b":
                self.weight = "bold"
            elif token.tag == "/b":
                self.weight = "normal"
            elif token.tag == "small":
                self.size -= 2
            elif token.tag == "/small":
                self.size += 2
            elif token.tag == "big":
                self.size += 4
            elif token.tag == "/big":
                self.size -= 4
            elif token.tag == "br":
                self.flush()
            elif token.tag == "/p":
                self.flush()
                self.cursor_y += VSTEP

        self.height = self.cursor_y
        return self.display_list

    def word(self, word: str):
        font = get_font(self.size, self.weight, self.style)
        w = font.measure(word)

        if self.cursor_x + w > WIDTH - HSTEP:
            self.flush()

        self.line.append((self.cursor_x, word, font))
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line:
            return

        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = HSTEP
        self.line = []
