from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Self
from parser import Element, Node

CSSRule = dict[str, str]


class AbstractSelector(ABC):
    @abstractmethod
    def matches(self, node: Node):
        pass


@dataclass
class TagSelector(AbstractSelector):
    tag: str
    priority: int = 1

    def matches(self, node: Node):
        return isinstance(node, Element) and self.tag == node.tag


class DescendantSelector(AbstractSelector):
    def __init__(self, ancestor: TagSelector | Self, descendant: TagSelector | Self):
        self.ancestor = ancestor
        self.descendant = descendant
        self.priority: int = ancestor.priority + descendant.priority

    def matches(self, node: Node):
        if not self.descendant.matches(node):
            return False

        while node.parent:
            if self.ancestor.matches(node.parent):
                return True
            node = node.parent

        return False


SelectorRule = tuple[TagSelector | DescendantSelector, CSSRule]


def cascade_priority(rule: SelectorRule) -> int:
    selector, body = rule
    return selector.priority
