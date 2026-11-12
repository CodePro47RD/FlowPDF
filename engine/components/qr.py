"""
QR Code component for ReportForge.
Generates vector or raster QR codes using the qrcode library.
"""

from __future__ import annotations
import io
from typing import Optional, Union
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
from reportlab.lib.utils import ImageReader

from ..core.element import Component
from ..core.geometry import Size, Rect, HorizontalAlignment, VerticalAlignment
from ..core.constraints import BoxConstraints
from ..core.colors import Color, Colors
from ..core.context import LayoutContext, DrawContext


class QRCode(Component):
    """
    Renders high-resolution QR codes.
    """

    _ERR_MAP = {
        "L": ERROR_CORRECT_L,
        "M": ERROR_CORRECT_M,
        "Q": ERROR_CORRECT_Q,
        "H": ERROR_CORRECT_H,
    }

    def __init__(
        self,
        data: str,
        size: float = 80.0,
        error_correction: str = "M",
        fill_color: Optional[Union[Color, str]] = None,
        back_color: Optional[Union[Color, str]] = None,
        horizontal_alignment: HorizontalAlignment = HorizontalAlignment.CENTER,
    ):
        self.data = data
        self.target_size = float(size)
        self.error_correction = self._ERR_MAP.get(error_correction.upper(), ERROR_CORRECT_M)
        self.fill_color = Color.from_any(fill_color) if fill_color is not None else Colors.BLACK
        self.back_color = Color.from_any(back_color) if back_color is not None else Colors.WHITE
        self.horizontal_alignment = horizontal_alignment

        self._image_cache: Optional[ImageReader] = None

    def _generate_qr_image(self) -> ImageReader:
        if self._image_cache is not None:
            return self._image_cache

        qr = qrcode.QRCode(
            version=None,
            error_correction=self.error_correction,
            box_size=10,
            border=1,
        )
        qr.add_data(self.data)
        qr.make(fit=True)

        pil_img = qr.make_image(
            fill_color=self.fill_color.to_hex(),
            back_color=self.back_color.to_hex(),
        ).convert("RGB")

        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        buf.seek(0)
        self._image_cache = ImageReader(buf)
        return self._image_cache

    def measure(self, constraints: BoxConstraints, context: LayoutContext) -> Size:
        s = self.target_size
        return constraints.constrain(Size(s, s))

    def draw(self, rect: Rect, context: DrawContext) -> None:
        img_reader = self._generate_qr_image()
        s = min(rect.width, rect.height, self.target_size)

        draw_x = rect.x
        if self.horizontal_alignment == HorizontalAlignment.CENTER:
            draw_x = rect.x + (rect.width - s) / 2.0
        elif self.horizontal_alignment == HorizontalAlignment.RIGHT:
            draw_x = rect.x + rect.width - s

        draw_y = rect.y + (rect.height - s) / 2.0
        canvas_y = context.to_canvas_y(draw_y, s)

        context.save_state()
        context.canvas.drawImage(img_reader, draw_x, canvas_y, width=s, height=s, mask="auto")
        context.restore_state()
