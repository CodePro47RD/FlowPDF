"""
Core Component interface and fluent modifier system.
Components can be measured, drawn, and optionally split
across page boundaries, while supporting fluent decorator chains.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union, TYPE_CHECKING
from .geometry import Size, Rect, EdgeInsets, HorizontalAlignment, VerticalAlignment
from .constraints import BoxConstraints
from .colors import Color
from .context import LayoutContext, DrawContext

if TYPE_CHECKING:
    from ..components.container import Container


class Component(ABC):
    """Abstract base class for all ReportForge renderable components."""

    @abstractmethod
    def measure(self, constraints: BoxConstraints, context: LayoutContext) -> Size:
        """Calculate and return the size required by this component."""
        pass

    @abstractmethod
    def draw(self, rect: Rect, context: DrawContext) -> None:
        """Render this component inside the specified bounding box."""
        pass

    def can_split(self) -> bool:
        """Whether this component can be split vertically across page breaks."""
        return False

    def split(
        self, available_height: float, context: LayoutContext
    ) -> Tuple[Optional[Component], Optional[Component]]:
        """
        Split this component into (fitted_part, remaining_part) based on available height.
        Default implementation returns (self, None) if it fits, or (None, self) if it does not.
        """
        size = self.measure(BoxConstraints(max_height=available_height), context)
        if size.height <= available_height:
            return self, None
        return None, self

    # =========================================================================
    # Fluent Decorators / Modifiers (declarative style)
    # =========================================================================

    def padding(
        self,
        all: Optional[float] = None,
        horizontal: Optional[float] = None,
        vertical: Optional[float] = None,
        top: Optional[float] = None,
        right: Optional[float] = None,
        bottom: Optional[float] = None,
        left: Optional[float] = None,
    ) -> Container:
        from ..components.container import Container
        if all is not None:
            insets = EdgeInsets.all(all)
        else:
            insets = EdgeInsets(
                top=float(top or vertical or 0.0),
                right=float(right or horizontal or 0.0),
                bottom=float(bottom or vertical or 0.0),
                left=float(left or horizontal or 0.0),
            )
        return Container(child=self, padding=insets)

    def margin(
        self,
        all: Optional[float] = None,
        horizontal: Optional[float] = None,
        vertical: Optional[float] = None,
        top: Optional[float] = None,
        right: Optional[float] = None,
        bottom: Optional[float] = None,
        left: Optional[float] = None,
    ) -> Container:
        from ..components.container import Container
        if all is not None:
            insets = EdgeInsets.all(all)
        else:
            insets = EdgeInsets(
                top=float(top or vertical or 0.0),
                right=float(right or horizontal or 0.0),
                bottom=float(bottom or vertical or 0.0),
                left=float(left or horizontal or 0.0),
            )
        return Container(child=self, margin=insets)

    def background(self, color: Union[Color, str]) -> Container:
        from ..components.container import Container
        return Container(child=self, background_color=Color.from_any(color))

    def border(
        self,
        color: Union[Color, str] = "#E2E8F0",
        width: float = 1.0,
        radius: float = 0.0,
    ) -> Container:
        from ..components.container import Container
        return Container(
            child=self,
            border_color=Color.from_any(color),
            border_width=width,
            border_radius=radius,
        )

    def width(self, value: float) -> Container:
        from ..components.container import Container
        return Container(child=self, width=float(value))

    def height(self, value: float) -> Container:
        from ..components.container import Container
        return Container(child=self, height=float(value))

    def min_height(self, value: float) -> Container:
        from ..components.container import Container
        return Container(child=self, min_height=float(value))

    def align_left(self) -> Container:
        from ..components.container import Container
        return Container(child=self, horizontal_alignment=HorizontalAlignment.LEFT)

    def align_center(self) -> Container:
        from ..components.container import Container
        return Container(child=self, horizontal_alignment=HorizontalAlignment.CENTER)

    def align_right(self) -> Container:
        from ..components.container import Container
        return Container(child=self, horizontal_alignment=HorizontalAlignment.RIGHT)

    def align_top(self) -> Container:
        from ..components.container import Container
        return Container(child=self, vertical_alignment=VerticalAlignment.TOP)

    def align_middle(self) -> Container:
        from ..components.container import Container
        return Container(child=self, vertical_alignment=VerticalAlignment.MIDDLE)

    def align_bottom(self) -> Container:
        from ..components.container import Container
        return Container(child=self, vertical_alignment=VerticalAlignment.BOTTOM)
