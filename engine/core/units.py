"""
Measurement units and conversion utilities for ReportForge.
All internal dimensions in ReportForge are measured in points (pt),
where 1 inch = 72 points = 25.4 millimeters.
"""

from typing import Union

Number = Union[int, float]

POINTS_PER_INCH = 72.0
POINTS_PER_MM = 72.0 / 25.4
POINTS_PER_CM = POINTS_PER_MM * 10.0


def pt(value: Number) -> float:
    """Return points directly."""
    return float(value)


def mm(value: Number) -> float:
    """Convert millimeters to points."""
    return float(value) * POINTS_PER_MM


def cm(value: Number) -> float:
    """Convert centimeters to points."""
    return float(value) * POINTS_PER_CM


def inch(value: Number) -> float:
    """Convert inches to points."""
    return float(value) * POINTS_PER_INCH
