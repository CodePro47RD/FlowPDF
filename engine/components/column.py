"""
Column component for ReportForge.
Stacks components vertically with configurable spacing and automatic page splitting.
"""

from __future__ import annotations
from typing import List, Optional, Tuple, Sequence
from ..core.element import Component
from ..core.geometry import Size, Rect
from ..core.constraints import BoxConstraints
from ..core.context import LayoutContext, DrawContext


class Column(Component):
    """
    Arranges child components vertically.
    """

    def __init__(
        self,
        children: Optional[Sequence[Component]] = None,
        spacing: float = 0.0,
    ):
        self.children: List[Component] = list(children) if children is not None else []
        self.spacing = float(spacing)

    def add(self, child: Component) -> Column:
        """Fluent helper to append a child."""
        self.children.append(child)
        return self

    def measure(self, constraints: BoxConstraints, context: LayoutContext) -> Size:
        if not self.children:
            return constraints.constrain(Size.zero())

        max_child_w = 0.0
        total_h = 0.0
        num_children = len(self.children)

        for i, child in enumerate(self.children):
            child_constraints = BoxConstraints(
                min_width=0.0,
                max_width=constraints.max_width,
                min_height=0.0,
                max_height=float("inf"),
            )
            child_size = child.measure(child_constraints, context)
            max_child_w = max(max_child_w, child_size.width)
            total_h += child_size.height
            if i < num_children - 1:
                total_h += self.spacing

        target_w = max(constraints.min_width, max_child_w)
        return constraints.constrain(Size(target_w, total_h))

    def draw(self, rect: Rect, context: DrawContext) -> None:
        curr_y = rect.y
        layout_ctx = LayoutContext(page_settings=context.page_settings, assets=context.assets)

        for i, child in enumerate(self.children):
            child_constraints = BoxConstraints(
                min_width=0.0,
                max_width=rect.width,
                min_height=0.0,
                max_height=float("inf"),
            )
            child_size = child.measure(child_constraints, layout_ctx)

            child_rect = Rect(
                x=rect.x,
                y=curr_y,
                width=rect.width,
                height=child_size.height,
            )
            child.draw(child_rect, context)

            curr_y += child_size.height
            if i < len(self.children) - 1:
                curr_y += self.spacing

    def can_split(self) -> bool:
        return True

    def split(
        self, available_height: float, context: LayoutContext
    ) -> Tuple[Optional[Component], Optional[Component]]:
        if available_height <= 0:
            return None, self

        fitted_children: List[Component] = []
        remaining_children: List[Component] = []
        used_height = 0.0

        for i, child in enumerate(self.children):
            child_constraints = BoxConstraints(
                min_width=0.0,
                max_width=context.page_settings.content_area.width,
                min_height=0.0,
                max_height=float("inf"),
            )
            child_size = child.measure(child_constraints, context)
            needed_spacing = self.spacing if fitted_children else 0.0

            if used_height + needed_spacing + child_size.height <= available_height:
                used_height += needed_spacing + child_size.height
                fitted_children.append(child)
            else:
                # Does not fit fully: try splitting this child if supported
                height_left = available_height - (used_height + needed_spacing)
                if child.can_split() and height_left > 0:
                    c_fit, c_rem = child.split(height_left, context)
                    if c_fit is not None:
                        fitted_children.append(c_fit)
                    if c_rem is not None:
                        remaining_children.append(c_rem)
                    remaining_children.extend(self.children[i + 1:])
                    break
                else:
                    # Child cannot split or no height left: all remaining go to next page
                    remaining_children.extend(self.children[i:])
                    break

        part1 = Column(fitted_children, spacing=self.spacing) if fitted_children else None
        part2 = Column(remaining_children, spacing=self.spacing) if remaining_children else None
        return part1, part2
