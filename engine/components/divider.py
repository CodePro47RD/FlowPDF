"""
Divider (horizontal separator line) component.
"""

from __future__ import annotations
from typing import Optional, Union
from ..core.element import Component
from ..core.geometry import Size, Rect, Point
from ..core.constraints import BoxConstraints
from ..core.colors import Color, Colors
from ..core.context import LayoutContext, DrawContext


class Divider(Component):
    """
    Draws a horizontal rule across the available width.
    """

    def __init__(
        self,
        thickness: float = 1.0,
        color: Optional[Union[Color, str]] = None,
        margin_vertical: float = 8.0,
    ):
        self.thickness = float(thickness)
        self.color = Color.from_any(color) if color is not None else Colors.BORDER_LIGHT
        self.margin_vertical = float(margin_vertical)

    def measure(self, constraints: BoxConstraints, context: LayoutContext) -> Size:
        total_height = self.thickness + (self.margin_vertical * 2.0)
        target_w = constraints.max_width if constraints.has_bounded_width else constraints.min_width
        return constraints.constrain(Size(target_w, total_height))

    def draw(self, rect: Rect, context: DrawContext) -> None:
        y_center = rect.y + self.margin_vertical + (self.thickness / 2.0)
        p1 = Point(rect.x, y_center)
        p2 = Point(rect.right, y_center)
        context.draw_line(p1, p2, self.color, width=self.thickness)
