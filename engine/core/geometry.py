"""
Geometry primitives for ReportForge document layout.
All coordinates follow a top-left origin convention:
(x, y) where x increases to the right and y increases downward.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Union


Number = Union[int, float]


class HorizontalAlignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    JUSTIFY = "justify"


class VerticalAlignment(str, Enum):
    TOP = "top"
    MIDDLE = "middle"
    BOTTOM = "bottom"


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def offset(self, dx: float, dy: float) -> Point:
        return Point(self.x + dx, self.y + dy)


@dataclass(frozen=True)
class Size:
    width: float
    height: float

    @classmethod
    def zero(cls) -> Size:
        return cls(0.0, 0.0)

    @classmethod
    def infinite(cls) -> Size:
        return cls(float("inf"), float("inf"))


@dataclass(frozen=True)
class EdgeInsets:
    top: float = 0.0
    right: float = 0.0
    bottom: float = 0.0
    left: float = 0.0

    @classmethod
    def all(cls, value: Number) -> EdgeInsets:
        v = float(value)
        return cls(top=v, right=v, bottom=v, left=v)

    @classmethod
    def symmetric(cls, vertical: Number = 0.0, horizontal: Number = 0.0) -> EdgeInsets:
        return cls(
            top=float(vertical),
            bottom=float(vertical),
            left=float(horizontal),
            right=float(horizontal),
        )

    @classmethod
    def only(
        cls,
        top: Number = 0.0,
        right: Number = 0.0,
        bottom: Number = 0.0,
        left: Number = 0.0,
    ) -> EdgeInsets:
        return cls(
            top=float(top),
            right=float(right),
            bottom=float(bottom),
            left=float(left),
        )

    @property
    def horizontal(self) -> float:
        return self.left + self.right

    @property
    def vertical(self) -> float:
        return self.top + self.bottom


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    @classmethod
    def from_ltwh(cls, left: float, top: float, width: float, height: float) -> Rect:
        return cls(x=left, y=top, width=width, height=height)

    @classmethod
    def from_origin_size(cls, origin: Point, size: Size) -> Rect:
        return cls(x=origin.x, y=origin.y, width=size.width, height=size.height)

    @property
    def left(self) -> float:
        return self.x

    @property
    def top(self) -> float:
        return self.y

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def size(self) -> Size:
        return Size(self.width, self.height)

    def deflate(self, insets: EdgeInsets) -> Rect:
        """Return a new rect reduced by insets."""
        w = max(0.0, self.width - insets.horizontal)
        h = max(0.0, self.height - insets.vertical)
        return Rect(
            x=self.x + insets.left,
            y=self.y + insets.top,
            width=w,
            height=h,
        )

    def inflate(self, insets: EdgeInsets) -> Rect:
        """Return a new rect expanded by insets."""
        return Rect(
            x=self.x - insets.left,
            y=self.y - insets.top,
            width=self.width + insets.horizontal,
            height=self.height + insets.vertical,
        )
