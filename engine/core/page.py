"""
Page dimensions, orientation, and margin settings for ReportForge documents.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Union, Tuple
from .geometry import Size, EdgeInsets
from .units import mm, inch, pt


class PageOrientation(str, Enum):
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


class PageSizes:
    """Standard international and US paper dimensions in points."""
    A3 = Size(mm(297), mm(420))
    A4 = Size(mm(210), mm(297))
    A5 = Size(mm(148), mm(210))
    LETTER = Size(inch(8.5), inch(11))
    LEGAL = Size(inch(8.5), inch(14))
    TABLOID = Size(inch(11), inch(17))

    _LOOKUP = {
        "a3": A3,
        "a4": A4,
        "a5": A5,
        "letter": LETTER,
        "legal": LEGAL,
        "tabloid": TABLOID,
    }

    @classmethod
    def get(cls, name_or_size: Union[str, Size, Tuple[float, float]]) -> Size:
        if isinstance(name_or_size, Size):
            return name_or_size
        if isinstance(name_or_size, (tuple, list)) and len(name_or_size) == 2:
            return Size(float(name_or_size[0]), float(name_or_size[1]))
        if isinstance(name_or_size, str):
            key = name_or_size.strip().lower()
            if key in cls._LOOKUP:
                return cls._LOOKUP[key]
        raise ValueError(f"Unknown page size: {name_or_size}. Expected one of {list(cls._LOOKUP.keys())}")


@dataclass
class PageSettings:
    """Comprehensive page setup configuration."""
    size: Size = field(default_factory=lambda: PageSizes.A4)
    orientation: PageOrientation = PageOrientation.PORTRAIT
    margin: EdgeInsets = field(default_factory=lambda: EdgeInsets.all(mm(15)))

    @property
    def dimensions(self) -> Size:
        """Effective page size considering orientation."""
        w, h = self.size.width, self.size.height
        if self.orientation == PageOrientation.LANDSCAPE:
            if w < h:
                return Size(width=h, height=w)
            return Size(width=w, height=h)
        else:
            if w > h:
                return Size(width=h, height=w)
            return Size(width=w, height=h)

    @property
    def content_area(self) -> Size:
        """Dimensions available for body content inside margins."""
        dims = self.dimensions
        w = max(0.0, dims.width - self.margin.horizontal)
        h = max(0.0, dims.height - self.margin.vertical)
        return Size(width=w, height=h)
