"""
Typography system for ReportForge.
Manages font registration, styles, sizes, and font metrics.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Union
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .colors import Color, Colors


@dataclass(frozen=True)
class TextStyle:
    font_name: str = "Helvetica"
    font_size: float = 10.0
    color: Color = Colors.TEXT_MAIN
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strike: bool = False
    line_height: float = 1.3  # Multiplier relative to font_size
    letter_spacing: float = 0.0

    def resolved_font_name(self) -> str:
        """Resolve standard 14 PDF fonts to their bold/oblique variants."""
        base = self.font_name
        if base in ("Helvetica", "Arial"):
            if self.bold and self.italic:
                return "Helvetica-BoldOblique"
            elif self.bold:
                return "Helvetica-Bold"
            elif self.italic:
                return "Helvetica-Oblique"
            return "Helvetica"
        elif base in ("Times-Roman", "Times"):
            if self.bold and self.italic:
                return "Times-BoldItalic"
            elif self.bold:
                return "Times-Bold"
            elif self.italic:
                return "Times-Italic"
            return "Times-Roman"
        elif base in ("Courier",):
            if self.bold and self.italic:
                return "Courier-BoldOblique"
            elif self.bold:
                return "Courier-Bold"
            elif self.italic:
                return "Courier-Oblique"
            return "Courier"
        return base

    @property
    def leading(self) -> float:
        """Calculates line height in points."""
        return self.font_size * self.line_height

    def copy_with(
        self,
        font_name: Optional[str] = None,
        font_size: Optional[float] = None,
        color: Optional[Union[Color, str]] = None,
        bold: Optional[bool] = None,
        italic: Optional[bool] = None,
        underline: Optional[bool] = None,
        strike: Optional[bool] = None,
        line_height: Optional[float] = None,
        letter_spacing: Optional[float] = None,
    ) -> TextStyle:
        resolved_color = Color.from_any(color) if color is not None else self.color
        return TextStyle(
            font_name=font_name if font_name is not None else self.font_name,
            font_size=font_size if font_size is not None else self.font_size,
            color=resolved_color,
            bold=bold if bold is not None else self.bold,
            italic=italic if italic is not None else self.italic,
            underline=underline if underline is not None else self.underline,
            strike=strike if strike is not None else self.strike,
            line_height=line_height if line_height is not None else self.line_height,
            letter_spacing=letter_spacing if letter_spacing is not None else self.letter_spacing,
        )


class Typography:
    """Predefined typography presets for clean hierarchy."""
    H1 = TextStyle(font_name="Helvetica", font_size=24.0, bold=True, line_height=1.2, color=Colors.GRAY_900)
    H2 = TextStyle(font_name="Helvetica", font_size=18.0, bold=True, line_height=1.25, color=Colors.GRAY_900)
    H3 = TextStyle(font_name="Helvetica", font_size=14.0, bold=True, line_height=1.3, color=Colors.GRAY_800)
    H4 = TextStyle(font_name="Helvetica", font_size=12.0, bold=True, line_height=1.3, color=Colors.GRAY_800)
    BODY = TextStyle(font_name="Helvetica", font_size=10.0, line_height=1.35, color=Colors.TEXT_MAIN)
    BODY_BOLD = TextStyle(font_name="Helvetica", font_size=10.0, bold=True, line_height=1.35, color=Colors.TEXT_MAIN)
    BODY_MUTED = TextStyle(font_name="Helvetica", font_size=10.0, line_height=1.35, color=Colors.TEXT_MUTED)
    CAPTION = TextStyle(font_name="Helvetica", font_size=8.5, line_height=1.3, color=Colors.TEXT_MUTED)
    CAPTION_BOLD = TextStyle(font_name="Helvetica", font_size=8.5, bold=True, line_height=1.3, color=Colors.TEXT_MUTED)
    CODE = TextStyle(font_name="Courier", font_size=9.0, line_height=1.3, color=Colors.GRAY_800)

    @staticmethod
    def register_font(family_name: str, file_path: str) -> None:
        """Register a custom TrueType (.ttf) font file with ReportLab."""
        pdfmetrics.registerFont(TTFont(family_name, file_path))
