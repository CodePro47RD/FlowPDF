"""
Text component for ReportForge.
Supports word-wrapping, multi-line measurement, text alignment,
typography presets, rich spans, and vertical pagination splitting.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union
from reportlab.pdfbase import pdfmetrics
from ..core.element import Component
from ..core.geometry import (
    Size,
    Rect,
    Point,
    HorizontalAlignment,
)
from ..core.constraints import BoxConstraints
from ..core.colors import Color
from ..core.typography import TextStyle, Typography
from ..core.context import LayoutContext, DrawContext


@dataclass
class TextSpan:
    """Individual span of styled text within a rich text block."""
    text: str
    style: Optional[TextStyle] = None


class Text(Component):
    """
    Renders styled text with automatic word wrapping and line breaking.
    """

    def __init__(
        self,
        text_or_spans: Union[str, List[TextSpan]],
        style: Optional[TextStyle] = None,
        alignment: HorizontalAlignment = HorizontalAlignment.LEFT,
        max_lines: Optional[int] = None,
    ):
        if isinstance(text_or_spans, str):
            self.spans = [TextSpan(text=text_or_spans)]
        else:
            self.spans = text_or_spans

        self.style = style if style is not None else Typography.BODY
        self.alignment = alignment
        self.max_lines = max_lines

    @property
    def plain_text(self) -> str:
        return "".join(s.text for s in self.spans)

    def _wrap_lines(self, max_width: float) -> List[str]:
        """Wrap plain text into lines that fit within max_width."""
        font_name = self.style.resolved_font_name()
        font_size = self.style.font_size
        full_text = self.plain_text

        # If width is unconstrained or very large, split on explicit newlines only
        if max_width <= 0 or max_width == float("inf"):
            return full_text.splitlines() or [""]

        wrapped_lines: List[str] = []
        paragraphs = full_text.split("\n")

        for para in paragraphs:
            if not para.strip():
                wrapped_lines.append("")
                continue

            words = para.split(" ")
            current_line = ""

            for word in words:
                candidate = f"{current_line} {word}" if current_line else word
                try:
                    w = pdfmetrics.stringWidth(candidate, font_name, font_size)
                except Exception:
                    # Fallback if font name lookup fails
                    w = len(candidate) * (font_size * 0.5)

                if w <= max_width:
                    current_line = candidate
                else:
                    if current_line:
                        wrapped_lines.append(current_line)
                        current_line = word
                    else:
                        # Single word wider than available line: force break
                        wrapped_lines.append(word)
                        current_line = ""

            if current_line:
                wrapped_lines.append(current_line)

        if self.max_lines is not None and len(wrapped_lines) > self.max_lines:
            wrapped_lines = wrapped_lines[: self.max_lines]

        return wrapped_lines if wrapped_lines else [""]

    def measure(self, constraints: BoxConstraints, context: LayoutContext) -> Size:
        max_w = constraints.max_width
        lines = self._wrap_lines(max_w)
        font_name = self.style.resolved_font_name()
        font_size = self.style.font_size
        line_height = self.style.leading

        measured_max_w = 0.0
        for line in lines:
            try:
                w = pdfmetrics.stringWidth(line, font_name, font_size)
            except Exception:
                w = len(line) * (font_size * 0.5)
            if w > measured_max_w:
                measured_max_w = w

        total_height = len(lines) * line_height
        target_size = Size(width=measured_max_w, height=total_height)
        return constraints.constrain(target_size)

    def draw(self, rect: Rect, context: DrawContext) -> None:
        lines = self._wrap_lines(rect.width)
        font_name = self.style.resolved_font_name()
        font_size = self.style.font_size
        line_height = self.style.leading

        context.save_state()
        context.canvas.setFont(font_name, font_size)
        context.canvas.setFillColor(self.style.color.to_reportlab())

        # Baseline offset: approximately font_size * 0.8 from line top
        baseline_offset = font_size * 0.85
        curr_y = rect.y

        for line in lines:
            if curr_y + line_height > rect.bottom + 0.1:
                break

            try:
                line_w = pdfmetrics.stringWidth(line, font_name, font_size)
            except Exception:
                line_w = len(line) * (font_size * 0.5)

            # Horizontal alignment calculation
            if self.alignment == HorizontalAlignment.CENTER:
                draw_x = rect.x + (rect.width - line_w) / 2.0
            elif self.alignment == HorizontalAlignment.RIGHT:
                draw_x = rect.x + rect.width - line_w
            else:
                draw_x = rect.x

            # ReportLab canvas Y (origin at bottom)
            draw_y = context.to_canvas_y(curr_y + baseline_offset)
            context.canvas.drawString(draw_x, draw_y, line)

            # Underline decoration
            if self.style.underline:
                underline_y = curr_y + baseline_offset + 1.5
                context.draw_line(
                    Point(draw_x, underline_y),
                    Point(draw_x + line_w, underline_y),
                    self.style.color,
                    width=max(0.75, font_size * 0.06),
                )

            # Strikethrough decoration
            if self.style.strike:
                strike_y = curr_y + (baseline_offset * 0.6)
                context.draw_line(
                    Point(draw_x, strike_y),
                    Point(draw_x + line_w, strike_y),
                    self.style.color,
                    width=max(0.75, font_size * 0.06),
                )

            curr_y += line_height

        context.restore_state()

    def can_split(self) -> bool:
        # Multi-line text can be split across pages
        return True

    def split(
        self, available_height: float, context: LayoutContext
    ) -> Tuple[Optional[Component], Optional[Component]]:
        line_height = self.style.leading
        if available_height < line_height:
            return None, self

        lines = self._wrap_lines(context.page_settings.content_area.width)
        max_lines_fit = int(available_height // line_height)

        if max_lines_fit <= 0:
            return None, self
        if max_lines_fit >= len(lines):
            return self, None

        first_text = "\n".join(lines[:max_lines_fit])
        second_text = "\n".join(lines[max_lines_fit:])

        first_part = Text(first_text, style=self.style, alignment=self.alignment)
        second_part = Text(second_text, style=self.style, alignment=self.alignment)

        return first_part, second_part
