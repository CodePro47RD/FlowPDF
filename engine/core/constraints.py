"""
Box constraints for the ReportForge layout engine.
Defines minimum and maximum allowable dimensions for component measurement.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Union
from .geometry import Size, EdgeInsets

Number = Union[int, float]


@dataclass(frozen=True)
class BoxConstraints:
    min_width: float = 0.0
    max_width: float = float("inf")
    min_height: float = 0.0
    max_height: float = float("inf")

    def __post_init__(self):
        assert self.min_width <= self.max_width, f"min_width ({self.min_width}) > max_width ({self.max_width})"
        assert self.min_height <= self.max_height, f"min_height ({self.min_height}) > max_height ({self.max_height})"
        assert self.min_width >= 0.0, "min_width must be >= 0"
        assert self.min_height >= 0.0, "min_height must be >= 0"

    @classmethod
    def tight(cls, size: Size) -> BoxConstraints:
        """Create constraints forcing a component to an exact size."""
        return cls(
            min_width=size.width,
            max_width=size.width,
            min_height=size.height,
            max_height=size.height,
        )

    @classmethod
    def tight_for(
        cls, width: Number | None = None, height: Number | None = None
    ) -> BoxConstraints:
        return cls(
            min_width=float(width) if width is not None else 0.0,
            max_width=float(width) if width is not None else float("inf"),
            min_height=float(height) if height is not None else 0.0,
            max_height=float(height) if height is not None else float("inf"),
        )

    @classmethod
    def loose(cls, size: Size) -> BoxConstraints:
        """Create constraints with 0 minimums and given maximums."""
        return cls(
            min_width=0.0,
            max_width=size.width,
            min_height=0.0,
            max_height=size.height,
        )

    def constrain_width(self, width: float) -> float:
        return max(self.min_width, min(self.max_width, width))

    def constrain_height(self, height: float) -> float:
        return max(self.min_height, min(self.max_height, height))

    def constrain(self, size: Size) -> Size:
        return Size(
            width=self.constrain_width(size.width),
            height=self.constrain_height(size.height),
        )

    def deflate(self, insets: EdgeInsets) -> BoxConstraints:
        """Reduce constraints by insets (e.g. for padding/borders)."""
        deflated_min_w = max(0.0, self.min_width - insets.horizontal)
        deflated_max_w = (
            max(0.0, self.max_width - insets.horizontal)
            if self.max_width != float("inf")
            else float("inf")
        )
        deflated_min_h = max(0.0, self.min_height - insets.vertical)
        deflated_max_h = (
            max(0.0, self.max_height - insets.vertical)
            if self.max_height != float("inf")
            else float("inf")
        )
        return BoxConstraints(
            min_width=deflated_min_w,
            max_width=max(deflated_min_w, deflated_max_w),
            min_height=deflated_min_h,
            max_height=max(deflated_min_h, deflated_max_h),
        )

    @property
    def has_bounded_width(self) -> bool:
        return self.max_width != float("inf")

    @property
    def has_bounded_height(self) -> bool:
        return self.max_height != float("inf")
