"""
ReportForge - Universal Document & Report Composition Engine.
"""

from .core.document import Document
from .core.page import PageSettings, PageSizes, PageOrientation
from .core.geometry import (
    Point,
    Size,
    Rect,
    EdgeInsets,
    HorizontalAlignment,
    VerticalAlignment,
)
from .core.constraints import BoxConstraints
from .core.colors import Color, Colors
from .core.typography import TextStyle, Typography
from .core.units import pt, mm, cm, inch
from .core.element import Component

from .components.text import Text, TextSpan
from .components.container import Container
from .components.column import Column
from .components.row import Row, RowItem
from .components.spacer import Spacer
from .components.divider import Divider
from .components.page_number import PageNumber
from .components.image import Image, ImageFit
from .components.table import Table, TableColumn, TableRow, TableCell
from .components.stack import Stack
from .components.qr import QRCode
from .components.barcode import Barcode
from .components.chart import Chart

__version__ = "1.0.0"

__all__ = [
    "Document",
    "PageSettings",
    "PageSizes",
    "PageOrientation",
    "Point",
    "Size",
    "Rect",
    "EdgeInsets",
    "HorizontalAlignment",
    "VerticalAlignment",
    "BoxConstraints",
    "Color",
    "Colors",
    "TextStyle",
    "Typography",
    "Component",
    "pt",
    "mm",
    "cm",
    "inch",
    "Text",
    "TextSpan",
    "Container",
    "Column",
    "Row",
    "RowItem",
    "Spacer",
    "Divider",
    "PageNumber",
    "Image",
    "ImageFit",
    "Table",
    "TableColumn",
    "TableRow",
    "TableCell",
    "Stack",
    "QRCode",
    "Barcode",
    "Chart",
]
