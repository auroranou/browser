#!/usr/bin/env python3

from constants import HEIGHT, SCROLL_STEP, VSTEP, WIDTH
from html_lexer import lex
from layout import layout
import tkinter
from url import URL


class Browser:
    def __init__(self):
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

    def load(self, url: URL):
        body, should_view_source = url.request()

        self.text = lex(body)
        self.display_list, self.doc_height = layout(self.text)
        self.draw()

    def draw(self):
        self.canvas.delete("all")

        for x, y, c in self.display_list:
            # Don't draw characters below viewing window
            if y > self.scroll + self.screen_height:
                continue
            # Or above it
            if y + VSTEP < self.scroll:
                continue

            self.canvas.create_text(x, y - self.scroll, text=c)

        self.draw_scrollbar()

    def draw_scrollbar(self):
        scrollbar_height = (self.screen_height / self.doc_height) * self.screen_height
        scrollbar_width = 12

        x0 = self.screen_width - scrollbar_width
        y0 = (self.scroll / self.doc_height) * self.screen_height
        x1 = self.screen_width
        y1 = y0 + scrollbar_height

        self.canvas.create_rectangle(x0, y0, x1, y1, fill="blue")

    def scrolldown(self, e):
        print(self.scroll, self.doc_height)
        if self.scroll < self.doc_height - SCROLL_STEP:
            self.scroll += SCROLL_STEP
            self.draw()

    def scrollup(self, e):
        if self.scroll >= SCROLL_STEP:
            self.scroll -= SCROLL_STEP
            self.draw()

    def mousewheel(self, e):
        # Subtract delta to account for preferred scrolling direction
        new_scroll_pos = self.scroll - e.delta
        if (new_scroll_pos >= 0) and (new_scroll_pos < self.doc_height):
            self.scroll = new_scroll_pos
            self.draw()

    def resize(self, e):
        self.screen_height = e.height
        self.screen_width = e.width
        self.display_list, self.doc_height = layout(self.text, self.screen_width)
        self.draw()


if __name__ == "__main__":
    import sys

    url = URL(sys.argv[1])
    Browser().load(url)
    tkinter.mainloop()
