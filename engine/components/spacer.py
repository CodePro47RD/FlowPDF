"""
Spacer component for vertical and horizontal blank separation.
"""

from __future__ import annotations
from typing import Optional
from ..core.element import Component
from ..core.geometry import Size, Rect
from ..core.constraints import BoxConstraints
from ..core.context import LayoutContext, DrawContext


class Spacer(Component):
    """
    Inserts empty space with a specified height and/or width.
    """

    def __init__(self, height: float = 10.0, width: Optional[float] = None):
        self.height = float(height)
        self.width = float(width) if width is not None else 0.0

    def measure(self, constraints: BoxConstraints, context: LayoutContext) -> Size:
        w = self.width if self.width > 0 else constraints.min_width
        h = self.height
        return constraints.constrain(Size(w, h))

    def draw(self, rect: Rect, context: DrawContext) -> None:
        # Spacers render nothing
        pass

    def can_split(self) -> bool:
        return False
