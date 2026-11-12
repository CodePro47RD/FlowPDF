"""
Color primitives and standard palettes for ReportForge.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Union, Tuple
from reportlab.lib import colors as rl_colors


@dataclass(frozen=True)
class Color:
    red: float    # 0.0 to 1.0
    green: float  # 0.0 to 1.0
    blue: float   # 0.0 to 1.0
    alpha: float = 1.0  # 0.0 to 1.0

    @classmethod
    def rgb(cls, r: int, g: int, b: int) -> Color:
        return cls(r / 255.0, g / 255.0, b / 255.0, 1.0)

    @classmethod
    def rgba(cls, r: int, g: int, b: int, a: float) -> Color:
        return cls(r / 255.0, g / 255.0, b / 255.0, max(0.0, min(1.0, float(a))))

    @classmethod
    def hex(cls, hex_str: str) -> Color:
        """Parse hex string such as #RRGGBB, #RGB, or #RRGGBBAA."""
        s = hex_str.strip().lstrip("#")
        if len(s) == 3:
            r = int(s[0] * 2, 16)
            g = int(s[1] * 2, 16)
            b = int(s[2] * 2, 16)
            return cls.rgb(r, g, b)
        elif len(s) == 6:
            r = int(s[0:2], 16)
            g = int(s[2:4], 16)
            b = int(s[4:6], 16)
            return cls.rgb(r, g, b)
        elif len(s) == 8:
            r = int(s[0:2], 16)
            g = int(s[2:4], 16)
            b = int(s[4:6], 16)
            a = int(s[6:8], 16) / 255.0
            return cls.rgba(r, g, b, a)
        else:
            raise ValueError(f"Invalid hex color: {hex_str}")

    @classmethod
    def from_any(cls, value: Union[str, Color, Tuple[int, int, int]]) -> Color:
        if isinstance(value, Color):
            return value
        if isinstance(value, str):
            if value.startswith("#"):
                return cls.hex(value)
            # Named color lookup
            val_lower = value.lower()
            if hasattr(Colors, val_lower.upper()):
                return getattr(Colors, val_lower.upper())
            return cls.hex(value)
        if isinstance(value, (tuple, list)):
            if len(value) == 3:
                return cls.rgb(value[0], value[1], value[2])
            elif len(value) == 4:
                return cls.rgba(value[0], value[1], value[2], value[3])
        raise ValueError(f"Cannot parse color from {value}")

    def to_reportlab(self) -> rl_colors.Color:
        """Convert to a ReportLab Color object."""
        return rl_colors.Color(self.red, self.green, self.blue, alpha=self.alpha)

    def to_hex(self) -> str:
        r = int(round(self.red * 255))
        g = int(round(self.green * 255))
        b = int(round(self.blue * 255))
        if self.alpha < 1.0:
            a = int(round(self.alpha * 255))
            return f"#{r:02x}{g:02x}{b:02x}{a:02x}"
        return f"#{r:02x}{g:02x}{b:02x}"

    def with_alpha(self, alpha: float) -> Color:
        return Color(self.red, self.green, self.blue, max(0.0, min(1.0, float(alpha))))


class Colors:
    """Standard professional palette for ReportForge documents."""
    TRANSPARENT = Color(0.0, 0.0, 0.0, 0.0)
    BLACK = Color(0.0, 0.0, 0.0, 1.0)
    WHITE = Color(1.0, 1.0, 1.0, 1.0)

    # Grays (Slate/Zinc palette)
    GRAY_50 = Color.hex("#F8FAFC")
    GRAY_100 = Color.hex("#F1F5F9")
    GRAY_200 = Color.hex("#E2E8F0")
    GRAY_300 = Color.hex("#CBD5E1")
    GRAY_400 = Color.hex("#94A3B8")
    GRAY_500 = Color.hex("#64748B")
    GRAY_600 = Color.hex("#475569")
    GRAY_700 = Color.hex("#334155")
    GRAY_800 = Color.hex("#1E293B")
    GRAY_900 = Color.hex("#0F172A")

    # Primary Blues
    PRIMARY = Color.hex("#1E40AF")      # Deep blue
    PRIMARY_LIGHT = Color.hex("#3B82F6")
    PRIMARY_DARK = Color.hex("#1E3A8A")

    # Accents & Semantics
    SUCCESS = Color.hex("#059669")
    SUCCESS_LIGHT = Color.hex("#D1FAE5")
    WARNING = Color.hex("#D97706")
    WARNING_LIGHT = Color.hex("#FEF3C7")
    DANGER = Color.hex("#DC2626")
    DANGER_LIGHT = Color.hex("#FEE2E2")
    INFO = Color.hex("#0284C7")
    INFO_LIGHT = Color.hex("#E0F2FE")

    # Muted text & backgrounds
    TEXT_MAIN = Color.hex("#0F172A")
    TEXT_MUTED = Color.hex("#64748B")
    BORDER_LIGHT = Color.hex("#E2E8F0")
    BG_ZEBRA = Color.hex("#F8FAFC")
