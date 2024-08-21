#!/usr/bin/env python3
import tkinter

from constants import HEIGHT, SCROLL_STEP, VSTEP, WIDTH
from css.parser import DEFAULT_STYLE_SHEET, CSSParser, style
from css.selectors import cascade_priority
from layout.commands import DrawRect, DrawText
from layout.layout import DocumentLayout, paint_tree
from parser import Element, HTMLParser
from url import URL, AbstractURL
from utils import tree_to_list


class Browser:
    def __init__(self, rtl: bool = False):
        self.rtl = rtl
        self.scroll = 0
        self.screen_height = HEIGHT
        self.screen_width = WIDTH

        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, width=self.screen_width, height=self.screen_height, bg="white"
        )
        self.canvas.pack(expand=True, fill="both")

        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mousewheel)
        self.window.bind("<Configure>", self.resize)

    def get_stylesheets(self):
        return [
            node.attributes["href"]
            for node in tree_to_list(self.nodes, [])
            if isinstance(node, Element)
            and node.tag == "link"
            and node.attributes.get("rel") == "stylesheet"
            and "href" in node.attributes
        ]

    def load(self, url: AbstractURL):
        body, _ = url.request()
        self.nodes = HTMLParser(body).parse()
        rules = DEFAULT_STYLE_SHEET.copy()
        links = self.get_stylesheets()

        for link in links:
            style_url = url.resolve(link)
            try:
                body = style_url.request()
            except:
                continue
            rules.extend(CSSParser(body).parse())

        style(self.nodes, sorted(rules, key=cascade_priority))

        self.layout()
        self.draw()

    def layout(self):
        self.document = DocumentLayout(
            self.nodes, width=self.screen_width, rtl=self.rtl
        )
        self.document.layout()
        self.display_list: list[DrawRect | DrawText] = []
        paint_tree(self.document, self.display_list)

    def draw(self):
        self.canvas.delete("all")

        for cmd in self.display_list:
            # Don't draw characters below viewing window
            if cmd.top > self.scroll + self.screen_height:
                continue
            # Or above it
            if cmd.bottom + VSTEP < self.scroll:
                continue

            cmd.execute(self.scroll, self.canvas)

        if self.document.height > self.screen_height:
            self.draw_scrollbar()

    # Ex. 2-4
    def draw_scrollbar(self):
        scrollbar_width = 12

        x0 = self.screen_width - scrollbar_width
        y0 = self.scroll / self.document.height * self.screen_height
        x1 = self.screen_width
        y1 = (
            (self.scroll + self.screen_height)
            / self.document.height
            * self.screen_height
        )

        self.canvas.create_rectangle(x0, y0, x1, y1, fill="blue")

    def scrolldown(self, e):
        max_y = max(self.document.height + 2 * VSTEP - self.screen_height, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)
        self.draw()

    def scrollup(self, e):
        if self.scroll >= SCROLL_STEP:
            self.scroll -= SCROLL_STEP
            self.draw()

    # Ex. 2-2
    def mousewheel(self, e):
        # Subtract delta instead of adding to account for preferred scrolling direction
        new_scroll_pos = self.scroll - e.delta
        if (new_scroll_pos >= 0) and (
            new_scroll_pos < self.document.height - self.screen_height
        ):
            self.scroll = new_scroll_pos
            self.draw()

    # Ex. 2-3
    def resize(self, e):
        self.screen_height = e.height
        self.screen_width = e.width
        self.layout()
        self.draw()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--rtl", action="store_true")
    args = parser.parse_args()

    url = URL.create(args.url)
    Browser(args.rtl).load(url)
    tkinter.mainloop()
