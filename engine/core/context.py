"""
Execution contexts for measurement (LayoutContext) and canvas drawing (DrawContext).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from reportlab.pdfgen.canvas import Canvas
from .geometry import Rect, Point
from .colors import Color
from .page import PageSettings


@dataclass
class LayoutContext:
    """Carries layout state, asset loaders, and measurement caches."""
    page_settings: PageSettings
    assets: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_asset(self, key: str) -> Optional[Any]:
        return self.assets.get(key)


@dataclass
class DrawContext:
    """
    Coordinates rendering onto the underlying ReportLab canvas.
    Translates top-down layout coordinates into ReportLab bottom-up canvas coordinates.
    """
    canvas: Canvas
    page_settings: PageSettings
    page_number: int = 1
    total_pages: int = 1
    assets: Dict[str, Any] = field(default_factory=dict)

    @property
    def page_height(self) -> float:
        return self.page_settings.dimensions.height

    @property
    def page_width(self) -> float:
        return self.page_settings.dimensions.width

    def to_canvas_y(self, top_y: float, height: float = 0.0) -> float:
        """Translate top-down y coordinate to ReportLab bottom-up y."""
        return self.page_height - top_y - height

    def save_state(self) -> None:
        self.canvas.saveState()

    def restore_state(self) -> None:
        self.canvas.restoreState()

    def fill_rect(self, rect: Rect, color: Color) -> None:
        """Fill a rectangle in top-down coordinates."""
        if color.alpha <= 0:
            return
        self.save_state()
        self.canvas.setFillColor(color.to_reportlab())
        c_y = self.to_canvas_y(rect.y, rect.height)
        self.canvas.rect(rect.x, c_y, rect.width, rect.height, fill=1, stroke=0)
        self.restore_state()

    def stroke_rect(self, rect: Rect, color: Color, width: float = 1.0) -> None:
        """Stroke a rectangle in top-down coordinates."""
        if color.alpha <= 0 or width <= 0:
            return
        self.save_state()
        self.canvas.setStrokeColor(color.to_reportlab())
        self.canvas.setLineWidth(width)
        c_y = self.to_canvas_y(rect.y, rect.height)
        self.canvas.rect(rect.x, c_y, rect.width, rect.height, fill=0, stroke=1)
        self.restore_state()

    def draw_line(self, p1: Point, p2: Point, color: Color, width: float = 1.0) -> None:
        """Draw a line between two points in top-down coordinates."""
        self.save_state()
        self.canvas.setStrokeColor(color.to_reportlab())
        self.canvas.setLineWidth(width)
        cy1 = self.to_canvas_y(p1.y)
        cy2 = self.to_canvas_y(p2.y)
        self.canvas.line(p1.x, cy1, p2.x, cy2)
        self.restore_state()
