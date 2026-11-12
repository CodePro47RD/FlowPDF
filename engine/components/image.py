"""
Image component for ReportForge.
Loads images from files, bytes, base64 strings, or streams,
supporting proportional scaling and aspect ratio preservation.
"""

from __future__ import annotations
import base64
import io
from enum import Enum
from pathlib import Path
from typing import Optional, Union, Tuple
from PIL import Image as PILImage
from reportlab.lib.utils import ImageReader

from ..core.element import Component
from ..core.geometry import Size, Rect, HorizontalAlignment, VerticalAlignment
from ..core.constraints import BoxConstraints
from ..core.context import LayoutContext, DrawContext
from ..core.exceptions import AssetError


class ImageFit(str, Enum):
    CONTAIN = "contain"
    COVER = "cover"
    FILL = "fill"
    NONE = "none"


class Image(Component):
    """
    Renders bitmap graphics (PNG, JPG, WebP) with precise layout geometry.
    """

    def __init__(
        self,
        source: Union[str, bytes, io.BytesIO, Path],
        *,
        width: Optional[float] = None,
        height: Optional[float] = None,
        fit: Union[str, ImageFit] = ImageFit.CONTAIN,
        horizontal_alignment: HorizontalAlignment = HorizontalAlignment.CENTER,
        vertical_alignment: VerticalAlignment = VerticalAlignment.MIDDLE,
    ):
        self.source = source
        self.target_width = float(width) if width is not None else None
        self.target_height = float(height) if height is not None else None
        self.fit = ImageFit(fit) if isinstance(fit, str) else fit
        self.horizontal_alignment = horizontal_alignment
        self.vertical_alignment = vertical_alignment

        self._pil_image: Optional[PILImage.Image] = None
        self._natural_size: Optional[Tuple[float, float]] = None

    def _load_image(self) -> PILImage.Image:
        if self._pil_image is not None:
            return self._pil_image

        try:
            if isinstance(self.source, (str, Path)):
                s_str = str(self.source).strip()
                if s_str.startswith("data:image/") and ";base64," in s_str:
                    # Data URI scheme
                    raw_data = base64.b64decode(s_str.split(";base64,")[1])
                    img = PILImage.open(io.BytesIO(raw_data))
                elif len(s_str) > 200 and not s_str.endswith((".png", ".jpg", ".jpeg", ".webp")):
                    # Likely raw base64 string
                    try:
                        raw_data = base64.b64decode(s_str)
                        img = PILImage.open(io.BytesIO(raw_data))
                    except Exception:
                        img = PILImage.open(s_str)
                else:
                    img = PILImage.open(s_str)
            elif isinstance(self.source, bytes):
                img = PILImage.open(io.BytesIO(self.source))
            elif isinstance(self.source, io.BytesIO):
                img = PILImage.open(self.source)
            else:
                raise AssetError(f"Unsupported image source type: {type(self.source)}")

            # Convert paletted or exotic modes to RGBA or RGB for ReportLab compatibility
            if img.mode in ("P", "1", "CMYK"):
                img = img.convert("RGBA" if "transparency" in img.info else "RGB")

            self._pil_image = img
            self._natural_size = (float(img.width), float(img.height))
            return self._pil_image

        except Exception as e:
            raise AssetError(f"Failed to load image asset: {e}") from e

    @property
    def natural_aspect_ratio(self) -> float:
        img = self._load_image()
        return float(img.width) / float(img.height) if img.height > 0 else 1.0

    def measure(self, constraints: BoxConstraints, context: LayoutContext) -> Size:
        img = self._load_image()
        nat_w, nat_h = float(img.width), float(img.height)
        ratio = nat_w / nat_h if nat_h > 0 else 1.0

        if self.target_width is not None and self.target_height is not None:
            w = self.target_width
            h = self.target_height
        elif self.target_width is not None:
            w = self.target_width
            h = w / ratio
        elif self.target_height is not None:
            h = self.target_height
            w = h * ratio
        else:
            # Natural size clamped to available constraints
            max_w = constraints.max_width if constraints.has_bounded_width else nat_w
            if nat_w > max_w:
                w = max_w
                h = w / ratio
            else:
                w = nat_w
                h = nat_h

        return constraints.constrain(Size(w, h))

    def draw(self, rect: Rect, context: DrawContext) -> None:
        img = self._load_image()
        nat_w, nat_h = float(img.width), float(img.height)
        ratio = nat_w / nat_h if nat_h > 0 else 1.0

        if self.fit == ImageFit.FILL:
            draw_w = rect.width
            draw_h = rect.height
        elif self.fit == ImageFit.CONTAIN:
            # Scale uniformly to fit within rect
            box_ratio = rect.width / rect.height if rect.height > 0 else 1.0
            if box_ratio > ratio:
                # Constrained by height
                draw_h = rect.height
                draw_w = draw_h * ratio
            else:
                # Constrained by width
                draw_w = rect.width
                draw_h = draw_w / ratio
        elif self.fit == ImageFit.NONE:
            draw_w = min(rect.width, nat_w)
            draw_h = min(rect.height, nat_h)
        else:  # COVER or default
            draw_w = rect.width
            draw_h = rect.height

        # Alignment within the bounding box
        draw_x = rect.x
        if self.horizontal_alignment == HorizontalAlignment.CENTER:
            draw_x = rect.x + (rect.width - draw_w) / 2.0
        elif self.horizontal_alignment == HorizontalAlignment.RIGHT:
            draw_x = rect.x + rect.width - draw_w

        draw_y = rect.y
        if self.vertical_alignment == VerticalAlignment.MIDDLE:
            draw_y = rect.y + (rect.height - draw_h) / 2.0
        elif self.vertical_alignment == VerticalAlignment.BOTTOM:
            draw_y = rect.y + rect.height - draw_h

        # ReportLab canvas draw
        # Use ImageReader to allow PIL Images directly in memory
        reader = ImageReader(img)
        canvas_y = context.to_canvas_y(draw_y, draw_h)

        context.save_state()
        context.canvas.drawImage(
            reader,
            draw_x,
            canvas_y,
            width=draw_w,
            height=draw_h,
            mask="auto",
        )
        context.restore_state()
