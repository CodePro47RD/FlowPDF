"""
Row component for ReportForge.
Distributes components horizontally using fixed widths or relative flex weights.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Sequence
from ..core.element import Component
from ..core.geometry import Size, Rect, VerticalAlignment
from ..core.constraints import BoxConstraints
from ..core.context import LayoutContext, DrawContext


@dataclass
class RowItem:
    component: Component
    width: Optional[float] = None       # Constant width in pt
    flex: Optional[float] = None        # Relative flex weight (e.g. 1.0, 2.0)
    is_auto: bool = False               # Natural intrinsic size


class Row(Component):
    """
    Arranges child components horizontally with flex or fixed column widths.
    """

    def __init__(
        self,
        items: Optional[Sequence[Component | RowItem]] = None,
        spacing: float = 0.0,
        vertical_alignment: VerticalAlignment = VerticalAlignment.TOP,
    ):
        self.items: List[RowItem] = []
        self.spacing = float(spacing)
        self.vertical_alignment = vertical_alignment

        if items:
            for it in items:
                if isinstance(it, RowItem):
                    self.items.append(it)
                elif isinstance(it, Component):
                    # Default to flex=1.0 for plain components
                    self.items.append(RowItem(component=it, flex=1.0))

    def constant_item(self, width: float, component: Component) -> Row:
        """Add an item with fixed width in points."""
        self.items.append(RowItem(component=component, width=float(width)))
        return self

    def relative_item(self, flex: float, component: Component) -> Row:
        """Add an item with proportional flex weight."""
        self.items.append(RowItem(component=component, flex=float(flex)))
        return self

    def auto_item(self, component: Component) -> Row:
        """Add an item with intrinsic size."""
        self.items.append(RowItem(component=component, is_auto=True))
        return self

    def _resolve_widths(
        self, available_width: float, context: LayoutContext
    ) -> List[float]:
        n = len(self.items)
        if n == 0:
            return []

        total_spacing = self.spacing * (n - 1)
        width_for_items = max(0.0, available_width - total_spacing)

        resolved: List[float] = [0.0] * n
        fixed_sum = 0.0
        total_flex = 0.0

        # Pass 1: Fixed and auto items
        for i, item in enumerate(self.items):
            if item.width is not None:
                resolved[i] = item.width
                fixed_sum += item.width
            elif item.is_auto:
                size = item.component.measure(
                    BoxConstraints(min_width=0, max_width=width_for_items), context
                )
                resolved[i] = size.width
                fixed_sum += size.width
            elif item.flex is not None and item.flex > 0:
                total_flex += item.flex

        # Pass 2: Distribute remaining space to flex items
        remaining = max(0.0, width_for_items - fixed_sum)
        for i, item in enumerate(self.items):
            if item.flex is not None and total_flex > 0:
                resolved[i] = (item.flex / total_flex) * remaining

        return resolved

    def measure(self, constraints: BoxConstraints, context: LayoutContext) -> Size:
        if not self.items:
            return constraints.constrain(Size.zero())

        avail_w = constraints.max_width if constraints.has_bounded_width else constraints.min_width
        widths = self._resolve_widths(avail_w, context)

        max_h = 0.0
        for i, item in enumerate(self.items):
            item_w = widths[i]
            item_constraints = BoxConstraints(
                min_width=item_w,
                max_width=item_w,
                min_height=0.0,
                max_height=constraints.max_height,
            )
            item_size = item.component.measure(item_constraints, context)
            max_h = max(max_h, item_size.height)

        total_w = sum(widths) + (self.spacing * (len(self.items) - 1))
        return constraints.constrain(Size(total_w, max_h))

    def draw(self, rect: Rect, context: DrawContext) -> None:
        if not self.items:
            return

        layout_ctx = LayoutContext(page_settings=context.page_settings, assets=context.assets)
        widths = self._resolve_widths(rect.width, layout_ctx)

        # Measure heights for vertical alignment
        heights = []
        for i, item in enumerate(self.items):
            item_w = widths[i]
            item_size = item.component.measure(
                BoxConstraints(min_width=item_w, max_width=item_w), layout_ctx
            )
            heights.append(item_size.height)

        max_h = max(heights) if heights else 0.0
        curr_x = rect.x

        for i, item in enumerate(self.items):
            item_w = widths[i]
            item_h = heights[i]

            # Vertical alignment calculation
            curr_y = rect.y
            if self.vertical_alignment == VerticalAlignment.MIDDLE:
                curr_y += (max_h - item_h) / 2.0
            elif self.vertical_alignment == VerticalAlignment.BOTTOM:
                curr_y += max_h - item_h

            item_rect = Rect(x=curr_x, y=curr_y, width=item_w, height=item_h)
            item.component.draw(item_rect, context)

            curr_x += item_w + self.spacing
