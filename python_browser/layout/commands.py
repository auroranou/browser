from dataclasses import dataclass
import tkinter.font


@dataclass
class DrawText:
    top: float
    left: float
    text: str
    font: tkinter.font.Font

    @property
    def bottom(self) -> float:
        return self.top + self.font.metrics().get("ascent")

    def execute(self, scroll: float, canvas: tkinter.Canvas):
        canvas.create_text(
            self.left, self.top - scroll, text=self.text, font=self.font, anchor="nw"
        )


@dataclass
class DrawRect:
    top: float
    left: float
    bottom: float
    right: float
    color: str

    def execute(self, scroll: float, canvas: tkinter.Canvas):
        canvas.create_rectangle(
            self.left,
            self.top - scroll,
            self.right,
            self.bottom - scroll,
            width=0,
            fill=self.color,
        )
