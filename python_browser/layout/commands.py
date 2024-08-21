from dataclasses import dataclass
import tkinter.font


@dataclass
class DrawText:
    color: str
    font: tkinter.font.Font
    left: float
    text: str
    top: float

    @property
    def bottom(self) -> float:
        return self.top + self.font.metrics().get("linespace")

    def execute(self, scroll: float, canvas: tkinter.Canvas):
        canvas.create_text(
            self.left,
            self.top - scroll,
            anchor="nw",
            fill=self.color,
            font=self.font,
            text=self.text,
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
