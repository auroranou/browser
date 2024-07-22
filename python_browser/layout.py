from dataclasses import dataclass
import tkinter.font
from typing import Literal

from constants import HSTEP, VSTEP, WIDTH
from fonts import FontStyle, FontWeight, get_font
from html_lexer import Tag, Text

TextAlign = Literal["right", "left", "center"]


@dataclass
class LineItem:
    x: float
    word: str
    font: tkinter.font.Font
    parent_tag: str | None


@dataclass
class DisplayListItem:
    x: float
    y: float
    word: str
    font: tkinter.font.Font


class Layout:
    def __init__(
        self, tokens: list[Tag | Text], width: float = WIDTH, rtl: bool = False
    ):
        self.rtl = rtl
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.size = 12
        self.style: FontStyle = "roman"
        self.weight: FontWeight = "normal"
        self.text_align: TextAlign = "right" if rtl else "left"

        self.parent_tag = None
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
            if not token.tag.startswith("/"):
                self.parent_tag = token.tag
                if token.tag == "i":
                    self.style = "italic"
                elif token.tag == "b":
                    self.weight = "bold"
                elif token.tag == "small":
                    self.size -= 2
                elif token.tag == "big":
                    self.size += 4
                elif token.tag == "sup":
                    self.size /= 2
                elif token.tag == "br":
                    self.flush()
                elif token.tag == 'h1 class="title"':
                    self.text_align = "center"
            else:
                self.parent_tag = None
                if token.tag == "/i":
                    self.style = "roman"
                elif token.tag == "/b":
                    self.weight = "normal"
                elif token.tag == "/small":
                    self.size += 2
                elif token.tag == "/big":
                    self.size -= 4
                elif token.tag == "/sup":
                    self.size *= 2
                elif token.tag == "/p":
                    self.flush()
                    self.cursor_y += VSTEP
                elif token.tag == "/h1":
                    self.flush()
                    self.text_align = "right" if self.rtl else "left"

        self.height = self.cursor_y
        return self.display_list

    def _handle_abbr(self, word: str):
        assert self.parent_tag == "abbr"

        # Inside an <abbr> tag, lower-case letters should be small, capitalized, and bold,
        abbr_font = get_font(int(self.size - 2), "bold", "roman")
        # while all other characters (upper case, numbers, etc.) should be drawn in the normal font
        curr_font = get_font(int(self.size), self.weight, self.style)

        # If the <abbr> word won't fit on the current line, flush first
        word_w = curr_font.measure(word)
        if self.cursor_x + word_w > WIDTH - HSTEP:
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
                        parent_tag=self.parent_tag,
                    )
                )
            else:
                char_w = abbr_font.measure(char)
                self.line.append(
                    LineItem(
                        x=self.cursor_x,
                        word=char.upper(),
                        font=abbr_font,
                        parent_tag=self.parent_tag,
                    )
                )

            self.cursor_x += char_w

        self.cursor_x += curr_font.measure(" ")

    def word(self, word: str):
        if self.parent_tag == "abbr":
            self._handle_abbr(word)
            return

        font = get_font(int(self.size), self.weight, self.style)
        w = font.measure(word)

        if self.cursor_x + w > WIDTH - HSTEP:
            self.flush()

        self.line.append(
            LineItem(x=self.cursor_x, word=word, font=font, parent_tag=self.parent_tag)
        )
        self.cursor_x += w + font.measure(" ")

    def flush(self):
        if not self.line:
            return

        metrics = [item.font.metrics() for item in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        for item in self.line:
            y = baseline - item.font.metrics("ascent")
            x = item.x

            if item.parent_tag == "sup":
                y = baseline - max_ascent

            if self.text_align == "right":
                x_offset = self.width - self.cursor_x
                x += x_offset
            elif self.text_align == "center":
                x_offset = (self.width - self.cursor_x) / 2
                x += x_offset

            self.display_list.append(
                DisplayListItem(
                    x=x,
                    y=y,
                    word=item.word,
                    font=item.font,
                )
            )

        max_descent = max([metric["descent"] for metric in metrics])
        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = HSTEP
        self.line = []
