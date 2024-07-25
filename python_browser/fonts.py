import tkinter.font
from typing import Literal


FontStyle = Literal["roman", "italic"]
FontWeight = Literal["normal", "bold"]
FontCacheKey = tuple[str, int, FontWeight, FontStyle]

FONTS: dict[FontCacheKey, tuple[tkinter.font.Font, tkinter.Label]] = {}


def get_default_font_family() -> str:
    return tkinter.font.nametofont("TkDefaultFont").cget("family")


def get_font(
    size: int, weight: FontWeight, style: FontStyle, family: str = ""
) -> tkinter.font.Font:
    family = family or get_default_font_family()
    key = (family, size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(family=family, size=size, weight=weight, slant=style)
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]
