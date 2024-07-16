#!/usr/bin/env python3
import tkinter

from parser import HTMLParser
from constants import HEIGHT, SCROLL_STEP, VSTEP, WIDTH
from layout import Layout
from url import URL, AbstractURL


class Browser:
    def __init__(self, rtl: bool = False):
        self.rtl = rtl
        self.scroll = 0
        self.screen_height = HEIGHT
        self.screen_width = WIDTH

        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, width=self.screen_width, height=self.screen_height
        )
        self.canvas.pack(expand=True, fill="both")

        self.window.bind("<Down>", self.scrolldown)
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<MouseWheel>", self.mousewheel)
        self.window.bind("<Configure>", self.resize)

    def load(self, url: AbstractURL):
        body, _ = url.request()
        self.nodes = HTMLParser(body).parse()
        self.layout()
        self.draw()

    def layout(self):
        layout = Layout(self.nodes, self.screen_width, self.rtl)
        self.display_list = layout.display_list
        self.doc_height = layout.height

    def draw(self):
        self.canvas.delete("all")

        for item in self.display_list:
            # Don't draw characters below viewing window
            if item.y > self.scroll + self.screen_height:
                continue
            # Or above it
            if item.y + VSTEP < self.scroll:
                continue

            self.canvas.create_text(
                item.x,
                item.y - self.scroll,
                text=item.word,
                font=item.font,
                anchor="nw",
            )

        if self.doc_height > self.screen_height:
            self.draw_scrollbar()

    # Ex. 2-4
    def draw_scrollbar(self):
        scrollbar_width = 12

        x0 = self.screen_width - scrollbar_width
        y0 = self.scroll / self.doc_height * self.screen_height
        x1 = self.screen_width
        y1 = (self.scroll + self.screen_height) / self.doc_height * self.screen_height

        self.canvas.create_rectangle(x0, y0, x1, y1, fill="blue")

    def scrolldown(self, e):
        if self.scroll < self.doc_height - self.screen_height:
            self.scroll += SCROLL_STEP
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
            new_scroll_pos < self.doc_height - self.screen_height
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
