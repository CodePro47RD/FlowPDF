"""
Stack component for ReportForge.
Layers child components on top of each other at identical bounding box coordinates.
"""

from __future__ import annotations
from typing import List, Sequence, Optional
from ..core.element import Component
from ..core.geometry import Size, Rect
from ..core.constraints import BoxConstraints
from ..core.context import LayoutContext, DrawContext


class Stack(Component):
    """
    Overlays child components on top of each other.
    """

    def __init__(self, children: Optional[Sequence[Component]] = None):
        self.children: List[Component] = list(children) if children is not None else []

    def add(self, child: Component) -> Stack:
        self.children.append(child)
        return self

    def measure(self, constraints: BoxConstraints, context: LayoutContext) -> Size:
        max_w = 0.0
        max_h = 0.0
        for child in self.children:
            size = child.measure(constraints, context)
            max_w = max(max_w, size.width)
            max_h = max(max_h, size.height)
        return constraints.constrain(Size(max_w, max_h))

    def draw(self, rect: Rect, context: DrawContext) -> None:
        for child in self.children:
            child.draw(rect, context)
