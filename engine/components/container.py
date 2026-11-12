"""
Container component for ReportForge.
Applies sizing constraints, padding, margins, borders, backgrounds, and alignment to a child.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Union, Tuple
from ..core.element import Component
from ..core.geometry import (
    Size,
    Rect,
    EdgeInsets,
    HorizontalAlignment,
    VerticalAlignment,
)
from ..core.constraints import BoxConstraints
from ..core.colors import Color
from ..core.context import LayoutContext, DrawContext


@dataclass
class Container(Component):
    child: Optional[Component] = None
    width: Optional[float] = None
    height: Optional[float] = None
    min_width: Optional[float] = None
    max_width: Optional[float] = None
    min_height: Optional[float] = None
    max_height: Optional[float] = None
    padding_insets: EdgeInsets = field(default_factory=EdgeInsets)
    margin_insets: EdgeInsets = field(default_factory=EdgeInsets)
    background_color: Optional[Color] = None
    border_color: Optional[Color] = None
    border_width: float = 0.0
    border_radius: float = 0.0
    horizontal_alignment: Optional[HorizontalAlignment] = None
    vertical_alignment: Optional[VerticalAlignment] = None

    def __init__(
        self,
        child: Optional[Component] = None,
        *,
        width: Optional[float] = None,
        height: Optional[float] = None,
        min_width: Optional[float] = None,
        max_width: Optional[float] = None,
        min_height: Optional[float] = None,
        max_height: Optional[float] = None,
        padding: Optional[Union[float, EdgeInsets]] = None,
        margin: Optional[Union[float, EdgeInsets]] = None,
        background_color: Optional[Union[Color, str]] = None,
        border_color: Optional[Union[Color, str]] = None,
        border_width: float = 0.0,
        border_radius: float = 0.0,
        horizontal_alignment: Optional[HorizontalAlignment] = None,
        vertical_alignment: Optional[VerticalAlignment] = None,
    ):
        self.child = child
        self.width = float(width) if width is not None else None
        self.height = float(height) if height is not None else None
        self.min_width = float(min_width) if min_width is not None else None
        self.max_width = float(max_width) if max_width is not None else None
        self.min_height = float(min_height) if min_height is not None else None
        self.max_height = float(max_height) if max_height is not None else None

        if isinstance(padding, (int, float)):
            self.padding_insets = EdgeInsets.all(padding)
        elif isinstance(padding, EdgeInsets):
            self.padding_insets = padding
        else:
            self.padding_insets = EdgeInsets()

        if isinstance(margin, (int, float)):
            self.margin_insets = EdgeInsets.all(margin)
        elif isinstance(margin, EdgeInsets):
            self.margin_insets = margin
        else:
            self.margin_insets = EdgeInsets()

        self.background_color = (
            Color.from_any(background_color) if background_color is not None else None
        )
        self.border_color = (
            Color.from_any(border_color) if border_color is not None else None
        )
        self.border_width = float(border_width)
        self.border_radius = float(border_radius)
        self.horizontal_alignment = horizontal_alignment
        self.vertical_alignment = vertical_alignment

    def measure(self, constraints: BoxConstraints, context: LayoutContext) -> Size:
        # 1. Total extra space needed for margin and padding
        horizontal_extra = self.margin_insets.horizontal + self.padding_insets.horizontal
        vertical_extra = self.margin_insets.vertical + self.padding_insets.vertical

        # 2. Deflate parent constraints for child
        child_constraints = constraints.deflate(self.margin_insets).deflate(self.padding_insets)

        # 3. Apply explicit width/height constraints if specified
        if self.width is not None:
            child_constraints = BoxConstraints(
                min_width=max(0.0, self.width - horizontal_extra),
                max_width=max(0.0, self.width - horizontal_extra),
                min_height=child_constraints.min_height,
                max_height=child_constraints.max_height,
            )
        if self.height is not None:
            child_constraints = BoxConstraints(
                min_width=child_constraints.min_width,
                max_width=child_constraints.max_width,
                min_height=max(0.0, self.height - vertical_extra),
                max_height=max(0.0, self.height - vertical_extra),
            )

        if self.child is not None:
            child_size = self.child.measure(child_constraints, context)
        else:
            child_size = Size.zero()

        # Target width and height
        target_w = (
            self.width if self.width is not None else (child_size.width + horizontal_extra)
        )
        target_h = (
            self.height if self.height is not None else (child_size.height + vertical_extra)
        )

        if self.min_width is not None:
            target_w = max(target_w, self.min_width)
        if self.max_width is not None:
            target_w = min(target_w, self.max_width)
        if self.min_height is not None:
            target_h = max(target_h, self.min_height)
        if self.max_height is not None:
            target_h = min(target_h, self.max_height)

        return constraints.constrain(Size(target_w, target_h))

    def draw(self, rect: Rect, context: DrawContext) -> None:
        # Outer box adjusted for margin
        inner_rect = rect.deflate(self.margin_insets)
        if inner_rect.width <= 0 or inner_rect.height <= 0:
            return

        # Background drawing
        if self.background_color is not None:
            if self.border_radius > 0:
                context.save_state()
                context.canvas.setFillColor(self.background_color.to_reportlab())
                cy = context.to_canvas_y(inner_rect.y, inner_rect.height)
                context.canvas.roundRect(
                    inner_rect.x,
                    cy,
                    inner_rect.width,
                    inner_rect.height,
                    self.border_radius,
                    fill=1,
                    stroke=0,
                )
                context.restore_state()
            else:
                context.fill_rect(inner_rect, self.background_color)

        # Border drawing
        if self.border_color is not None and self.border_width > 0:
            if self.border_radius > 0:
                context.save_state()
                context.canvas.setStrokeColor(self.border_color.to_reportlab())
                context.canvas.setLineWidth(self.border_width)
                cy = context.to_canvas_y(inner_rect.y, inner_rect.height)
                context.canvas.roundRect(
                    inner_rect.x,
                    cy,
                    inner_rect.width,
                    inner_rect.height,
                    self.border_radius,
                    fill=0,
                    stroke=1,
                )
                context.restore_state()
            else:
                context.stroke_rect(inner_rect, self.border_color, self.border_width)

        # Content area inside padding
        content_rect = inner_rect.deflate(self.padding_insets)
        if content_rect.width <= 0 or content_rect.height <= 0 or self.child is None:
            return

        # Measure child to calculate alignment placement
        layout_ctx = LayoutContext(page_settings=context.page_settings, assets=context.assets)
        child_size = self.child.measure(
            BoxConstraints.loose(content_rect.size), layout_ctx
        )

        child_x = content_rect.x
        if self.horizontal_alignment == HorizontalAlignment.CENTER:
            child_x += (content_rect.width - child_size.width) / 2.0
        elif self.horizontal_alignment == HorizontalAlignment.RIGHT:
            child_x += content_rect.width - child_size.width

        child_y = content_rect.y
        if self.vertical_alignment == VerticalAlignment.MIDDLE:
            child_y += (content_rect.height - child_size.height) / 2.0
        elif self.vertical_alignment == VerticalAlignment.BOTTOM:
            child_y += content_rect.height - child_size.height

        child_draw_rect = Rect(
            x=child_x,
            y=child_y,
            width=min(content_rect.width, child_size.width),
            height=min(content_rect.height, child_size.height),
        )
        self.child.draw(child_draw_rect, context)

    def can_split(self) -> bool:
        return self.child is not None and self.child.can_split()

    def split(
        self, available_height: float, context: LayoutContext
    ) -> Tuple[Optional[Component], Optional[Component]]:
        if not self.can_split() or self.child is None:
            return super().split(available_height, context)

        overhead = self.margin_insets.vertical + self.padding_insets.vertical
        if available_height <= overhead:
            return None, self

        fitted_child, remaining_child = self.child.split(available_height - overhead, context)
        if fitted_child is None:
            return None, self

        fitted_container = Container(
            child=fitted_child,
            width=self.width,
            padding=self.padding_insets,
            margin=self.margin_insets,
            background_color=self.background_color,
            border_color=self.border_color,
            border_width=self.border_width,
            border_radius=self.border_radius,
            horizontal_alignment=self.horizontal_alignment,
            vertical_alignment=self.vertical_alignment,
        )

        remaining_container = None
        if remaining_child is not None:
            remaining_container = Container(
                child=remaining_child,
                width=self.width,
                padding=self.padding_insets,
                margin=self.margin_insets,
                background_color=self.background_color,
                border_color=self.border_color,
                border_width=self.border_width,
                border_radius=self.border_radius,
                horizontal_alignment=self.horizontal_alignment,
                vertical_alignment=self.vertical_alignment,
            )

        return fitted_container, remaining_container
