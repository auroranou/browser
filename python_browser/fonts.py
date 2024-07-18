import tkinter.font
from typing import Literal


FontStyle = Literal["roman", "italic"]
FontWeight = Literal["normal", "bold"]
FontCacheKey = tuple[int, FontWeight, FontStyle]

FONTS: dict[FontCacheKey, tuple[tkinter.font.Font, tkinter.Label]] = {}


def get_font(size: int, weight: FontWeight, style: FontStyle):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(size=size, weight=weight, slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]
