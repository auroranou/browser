from dataclasses import dataclass
import tkinter.font
from typing import Literal

TextAlign = Literal["right", "left", "center"]
VerticalAlign = Literal["baseline", "top"]


@dataclass
class LineItem:
    font: tkinter.font.Font
    x: float
    valign: VerticalAlign
    word: str


@dataclass
class DisplayListItem(LineItem):
    y: float
