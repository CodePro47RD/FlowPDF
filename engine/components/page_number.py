"""
Page number component for ReportForge footers and headers.
"""

from __future__ import annotations
from typing import Optional
from reportlab.pdfbase import pdfmetrics
from ..core.element import Component
from ..core.geometry import Size, Rect, HorizontalAlignment
from ..core.constraints import BoxConstraints
from ..core.typography import TextStyle, Typography
from ..core.context import LayoutContext, DrawContext


class PageNumber(Component):
    """
    Renders dynamic page numbers, e.g. "Página 1 de 5" or "1 / 10".
    """

    def __init__(
        self,
        format_str: str = "Página {page} de {total}",
        style: Optional[TextStyle] = None,
        alignment: HorizontalAlignment = HorizontalAlignment.RIGHT,
    ):
        self.format_str = format_str
        self.style = style if style is not None else Typography.CAPTION
        self.alignment = alignment

    def _format(self, page: int, total: int) -> str:
        return self.format_str.format(page=page, total=total)

    def measure(self, constraints: BoxConstraints, context: LayoutContext) -> Size:
        # Measure using a placeholder with 3 digits to ensure safe width
        placeholder = self._format(page=99, total=99)
        font_name = self.style.resolved_font_name()
        font_size = self.style.font_size
        try:
            w = pdfmetrics.stringWidth(placeholder, font_name, font_size)
        except Exception:
            w = len(placeholder) * (font_size * 0.5)

        return constraints.constrain(Size(w, self.style.leading))

    def draw(self, rect: Rect, context: DrawContext) -> None:
        text = self._format(page=context.page_number, total=context.total_pages)
        font_name = self.style.resolved_font_name()
        font_size = self.style.font_size

        try:
            w = pdfmetrics.stringWidth(text, font_name, font_size)
        except Exception:
            w = len(text) * (font_size * 0.5)

        draw_x = rect.x
        if self.alignment == HorizontalAlignment.CENTER:
            draw_x = rect.x + (rect.width - w) / 2.0
        elif self.alignment == HorizontalAlignment.RIGHT:
            draw_x = rect.x + rect.width - w

        context.save_state()
        context.canvas.setFont(font_name, font_size)
        context.canvas.setFillColor(self.style.color.to_reportlab())
        baseline_y = context.to_canvas_y(rect.y + font_size * 0.85)
        context.canvas.drawString(draw_x, baseline_y, text)
        context.restore_state()
