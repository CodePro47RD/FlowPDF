"""
Barcode component for ReportForge.
Supports Code 128, EAN-13, Code 39, ISBN, and other standard linear barcodes.
"""

from __future__ import annotations
import io
from typing import Optional, Union
import barcode
from barcode.writer import ImageWriter
from reportlab.lib.utils import ImageReader

from ..core.element import Component
from ..core.geometry import Size, Rect, HorizontalAlignment, VerticalAlignment
from ..core.constraints import BoxConstraints
from ..core.colors import Color, Colors
from ..core.context import LayoutContext, DrawContext
from ..core.exceptions import RenderError


class Barcode(Component):
    """
    Renders linear 1D barcodes.
    """

    def __init__(
        self,
        code: str,
        barcode_type: str = "code128",
        width: float = 180.0,
        height: float = 50.0,
        include_text: bool = True,
        horizontal_alignment: HorizontalAlignment = HorizontalAlignment.CENTER,
    ):
        self.code = str(code)
        self.barcode_type = barcode_type.lower()
        self.target_width = float(width)
        self.target_height = float(height)
        self.include_text = include_text
        self.horizontal_alignment = horizontal_alignment

        self._image_cache: Optional[ImageReader] = None

    def _generate_barcode(self) -> ImageReader:
        if self._image_cache is not None:
            return self._image_cache

        try:
            barcode_cls = barcode.get_barcode_class(self.barcode_type)
        except barcode.errors.BarcodeNotFoundError:
            barcode_cls = barcode.get_barcode_class("code128")

        writer = ImageWriter()
        buf = io.BytesIO()

        # Render options for high DPI and clean text
        options = {
            "write_text": self.include_text,
            "quiet_zone": 2.0,
            "font_size": 10,
            "text_distance": 3.0,
        }

        try:
            bc_instance = barcode_cls(self.code, writer=writer)
            bc_instance.write(buf, options=options)
            buf.seek(0)
            self._image_cache = ImageReader(buf)
            return self._image_cache
        except Exception as e:
            raise RenderError(f"Failed to generate barcode ({self.barcode_type}): {e}") from e

    def measure(self, constraints: BoxConstraints, context: LayoutContext) -> Size:
        return constraints.constrain(Size(self.target_width, self.target_height))

    def draw(self, rect: Rect, context: DrawContext) -> None:
        img_reader = self._generate_barcode()
        w = min(rect.width, self.target_width)
        h = min(rect.height, self.target_height)

        draw_x = rect.x
        if self.horizontal_alignment == HorizontalAlignment.CENTER:
            draw_x = rect.x + (rect.width - w) / 2.0
        elif self.horizontal_alignment == HorizontalAlignment.RIGHT:
            draw_x = rect.x + rect.width - w

        draw_y = rect.y + (rect.height - h) / 2.0
        canvas_y = context.to_canvas_y(draw_y, h)

        context.save_state()
        context.canvas.drawImage(img_reader, draw_x, canvas_y, width=w, height=h, mask="auto")
        context.restore_state()
