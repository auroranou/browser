import tkinter.font
from typing import Literal


FontStyle = Literal["roman", "italic"]
FontWeight = Literal["normal", "bold"]
FontCacheKey = tuple[str, int, FontWeight, FontStyle]

FONTS: dict[FontCacheKey, tuple[tkinter.font.Font, tkinter.Label]] = {}


def get_default_font_family() -> str:
    return tkinter.font.nametofont("TkDefaultFont").cget("family")


def validate_weight(weight: str) -> FontWeight:
    if weight == "normal" or weight == "bold":
        return weight
    return "normal"


def validate_style(style: str) -> FontStyle:
    if style == "roman" or style == "italic":
        return style
    return "roman"


def get_font(size: int, weight: str, style: str, family: str = "") -> tkinter.font.Font:
    family = family or get_default_font_family()
    weight = validate_weight(weight)
    style = validate_style(style)
    key = (family, size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(
            family=family,
            size=size,
            weight=weight,
            slant=style,
        )
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    return FONTS[key][0]
