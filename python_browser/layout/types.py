from abc import ABC, abstractmethod
from dataclasses import dataclass
import tkinter.font
from typing import Literal

TextAlign = Literal["right", "left", "center"]


@dataclass
class LineItem:
    x: float
    word: str
    font: tkinter.font.Font


@dataclass
class DisplayListItem(LineItem):
    y: float


class AbstractLayout(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def layout(self):
        pass

    @abstractmethod
    def paint(self):
        pass
