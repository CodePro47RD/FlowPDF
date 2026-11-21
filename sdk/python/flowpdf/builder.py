"""
Fluent Builder API for FlowPDF documents in Python.
Allows construction of complex, responsive multi-page report definitions with full type safety.
"""

from __future__ import annotations
import json
from typing import Any, Callable, Dict, List, Optional, Union


class PageConfigBuilder:
    def __init__(self):
        self._config: Dict[str, Any] = {
            "size": "A4",
            "orientation": "portrait",
            "margin": 15.0,
        }

    def size(self, size: str) -> PageConfigBuilder:
        self._config["size"] = size
        return self

    def a4(self) -> PageConfigBuilder:
        return self.size("A4")

    def letter(self) -> PageConfigBuilder:
        return self.size("Letter")

    def legal(self) -> PageConfigBuilder:
        return self.size("Legal")

    def a3(self) -> PageConfigBuilder:
        return self.size("A3")

    def a5(self) -> PageConfigBuilder:
        return self.size("A5")

    def orientation(self, orientation: str) -> PageConfigBuilder:
        self._config["orientation"] = orientation
        return self

    def portrait(self) -> PageConfigBuilder:
        return self.orientation("portrait")

    def landscape(self) -> PageConfigBuilder:
        return self.orientation("landscape")

    def margin(self, margin: float) -> PageConfigBuilder:
        self._config["margin"] = float(margin)
        return self

    def margins(self, top: float, right: float, bottom: float, left: float) -> PageConfigBuilder:
        self._config["margin_top"] = float(top)
        self._config["margin_right"] = float(right)
        self._config["margin_bottom"] = float(bottom)
        self._config["margin_left"] = float(left)
        return self

    def build(self) -> Dict[str, Any]:
        return dict(self._config)


class TextBuilder:
    def __init__(self, value: str):
        self._text: Dict[str, Any] = {
            "type": "text",
            "value": str(value),
        }

    def style(self, style: str) -> TextBuilder:
        self._text["style"] = style
        return self

    def h1(self) -> TextBuilder:
        return self.style("h1")

    def h2(self) -> TextBuilder:
        return self.style("h2")

    def h3(self) -> TextBuilder:
        return self.style("h3")

    def body(self) -> TextBuilder:
        return self.style("body")

    def caption(self) -> TextBuilder:
        return self.style("caption")

    def align(self, alignment: str) -> TextBuilder:
        self._text["alignment"] = alignment
        return self

    def left(self) -> TextBuilder:
        return self.align("left")

    def center(self) -> TextBuilder:
        return self.align("center")

    def right(self) -> TextBuilder:
        return self.align("right")

    def color(self, hex_or_name: str) -> TextBuilder:
        self._text["color"] = hex_or_name
        return self

    def font_size(self, size: float) -> TextBuilder:
        self._text["font_size"] = float(size)
        return self

    def bold(self, is_bold: bool = True) -> TextBuilder:
        self._text["bold"] = is_bold
        return self

    def italic(self, is_italic: bool = True) -> TextBuilder:
        self._text["italic"] = is_italic
        return self

    def underline(self, is_underline: bool = True) -> TextBuilder:
        self._text["underline"] = is_underline
        return self

    def font(self, font_name: str) -> TextBuilder:
        self._text["font"] = font_name
        return self

    def build(self) -> Dict[str, Any]:
        return dict(self._text)


class TableColumnBuilder:
    def __init__(self, title: str):
        self._col: Dict[str, Any] = {
            "title": str(title),
            "flex": 1.0,
            "align": "left",
        }

    def field(self, field_name: str) -> TableColumnBuilder:
        self._col["field"] = field_name
        return self

    def width(self, width: float) -> TableColumnBuilder:
        self._col["width"] = float(width)
        return self

    def flex(self, flex: float) -> TableColumnBuilder:
        self._col["flex"] = float(flex)
        return self

    def align(self, alignment: str) -> TableColumnBuilder:
        self._col["align"] = alignment
        return self

    def right(self) -> TableColumnBuilder:
        return self.align("right")

    def center(self) -> TableColumnBuilder:
        return self.align("center")

    def left(self) -> TableColumnBuilder:
        return self.align("left")

    def auto(self, enabled: bool = True) -> TableColumnBuilder:
        """Ancho según el contenido (texto más ancho de la columna, cabecera incluida). Su texto no se parte."""
        self._col["auto"] = bool(enabled)
        return self

    def format(self, fmt: str) -> TableColumnBuilder:
        """Formateador del valor: currency, number, percentage, date, uppercase, lowercase."""
        self._col["format"] = fmt
        return self

    def currency(self) -> TableColumnBuilder:
        return self.format("currency")

    def number(self) -> TableColumnBuilder:
        return self.format("number")

    def percentage(self) -> TableColumnBuilder:
        return self.format("percentage")

    def date(self) -> TableColumnBuilder:
        return self.format("date")

    def uppercase(self) -> TableColumnBuilder:
        return self.format("uppercase")

    def build(self) -> Dict[str, Any]:
        return dict(self._col)


class TableBuilder:
    def __init__(self):
        self._table: Dict[str, Any] = {
            "type": "table",
            "columns": [],
            "zebra": True,
            "repeat_header": True,
        }

    def column(
        self,
        title: str,
        field: Optional[str] = None,
        configure: Optional[Callable[[TableColumnBuilder], None]] = None,
    ) -> TableBuilder:
        b = TableColumnBuilder(title)
        if field:
            b.field(field)
        if configure:
            configure(b)
        self._table["columns"].append(b.build())
        return self

    def source(self, expression: str) -> TableBuilder:
        self._table["source"] = expression
        return self

    def data(self, rows: List[Dict[str, Any]]) -> TableBuilder:
        self._table["data"] = rows
        return self

    def rows(self, rows: List[Dict[str, Any]]) -> TableBuilder:
        return self.data(rows)

    def header_background(self, color: str) -> TableBuilder:
        self._table["header_background"] = color
        return self

    def zebra(self, enabled: bool = True) -> TableBuilder:
        self._table["zebra"] = enabled
        return self

    def border(self, color: str, width: float = 0.5) -> TableBuilder:
        self._table["border_color"] = color
        self._table["border_width"] = float(width)
        return self

    def repeat_header(self, enabled: bool = True) -> TableBuilder:
        self._table["repeat_header"] = enabled
        return self

    def font_size(self, size: float) -> TableBuilder:
        """Tamaño de letra de las celdas (pt). Por defecto 9."""
        self._table["font_size"] = float(size)
        return self

    def padding(self, horizontal: float, vertical: float) -> TableBuilder:
        """Relleno de cada celda (pt): horizontal y vertical. Por defecto 8 y 5.5."""
        self._table["padding_x"] = float(horizontal)
        self._table["padding_y"] = float(vertical)
        return self

    def header_color(self, color: str) -> TableBuilder:
        """Color del texto de la cabecera."""
        self._table["header_color"] = color
        return self

    def text_color(self, color: str) -> TableBuilder:
        """Color del texto de las celdas."""
        self._table["text_color"] = color
        return self

    def zebra_color(self, color: str) -> TableBuilder:
        """Filas alternas con fondo de este color (activa zebra)."""
        self._table["zebra"] = True
        self._table["zebra_color"] = color
        return self

    def group_by(
        self, field: str, background: Optional[str] = None, color: Optional[str] = None
    ) -> TableBuilder:
        """Agrupa las filas por un campo: cada vez que cambia su valor se intercala un título a todo el
        ancho. Las filas deben venir ordenadas por ese campo."""
        self._table["group_by"] = field
        if background is not None:
            self._table["group_background"] = background
        if color is not None:
            self._table["group_color"] = color
        return self

    def build(self) -> Dict[str, Any]:
        return dict(self._table)


class ContainerBuilder:
    def __init__(self):
        self._container: Dict[str, Any] = {
            "type": "container",
        }

    def padding(self, padding: float) -> ContainerBuilder:
        self._container["padding"] = float(padding)
        return self

    def margin(self, margin: float) -> ContainerBuilder:
        self._container["margin"] = float(margin)
        return self

    def background(self, color: str) -> ContainerBuilder:
        self._container["background"] = color
        return self

    def border(self, color: str, width: float = 1.0, radius: float = 0.0) -> ContainerBuilder:
        self._container["border_color"] = color
        self._container["border_width"] = float(width)
        self._container["border_radius"] = float(radius)
        return self

    def child(self, component: Union[Dict[str, Any], Any]) -> ContainerBuilder:
        self._container["child"] = component.build() if hasattr(component, "build") else component
        return self

    def build(self) -> Dict[str, Any]:
        return dict(self._container)


class RowItemBuilder:
    def __init__(self, component: Any):
        self._component = component.build() if hasattr(component, "build") else component
        self._width: Optional[float] = None
        self._flex: Optional[float] = None

    def width(self, width: float) -> RowItemBuilder:
        self._width = float(width)
        return self

    def flex(self, flex: float) -> RowItemBuilder:
        self._flex = float(flex)
        return self

    def build(self) -> Dict[str, Any]:
        return {
            "width": self._width,
            "flex": self._flex,
            "item": self._component,
        }


class RowBuilder:
    def __init__(self, spacing: float = 0.0):
        self._row: Dict[str, Any] = {
            "type": "row",
            "items": [],
            "spacing": float(spacing),
        }

    def item(
        self,
        component_or_fn: Union[Any, Callable[[ColumnBuilder], None]],
        width: Optional[float] = None,
        flex: Optional[float] = None,
    ) -> RowBuilder:
        if callable(component_or_fn):
            col = ColumnBuilder()
            component_or_fn(col)
            comp = col.build()
        elif hasattr(component_or_fn, "build"):
            comp = component_or_fn.build()
        else:
            comp = component_or_fn

        self._row["items"].append({
            "width": width,
            "flex": flex,
            "item": comp,
        })
        return self

    def column(
        self,
        configure: Callable[[ColumnBuilder], None],
        width: Optional[float] = None,
        flex: Optional[float] = None,
    ) -> RowBuilder:
        col = ColumnBuilder()
        configure(col)
        return self.item(col, width=width, flex=flex)

    def build(self) -> Dict[str, Any]:
        return dict(self._row)


class ColumnBuilder:
    def __init__(self, spacing: float = 0.0):
        self._column: Dict[str, Any] = {
            "type": "column",
            "items": [],
            "spacing": float(spacing),
        }

    def text(
        self,
        value: str,
        configure: Optional[Callable[[TextBuilder], None]] = None,
    ) -> ColumnBuilder:
        b = TextBuilder(value)
        if configure:
            configure(b)
        self._column["items"].append(b.build())
        return self

    def spacer(self, height: float = 10.0) -> ColumnBuilder:
        self._column["items"].append({"type": "spacer", "height": float(height)})
        return self

    def divider(self, thickness: float = 1.0, color: Optional[str] = None, margin: float = 5.0) -> ColumnBuilder:
        div: Dict[str, Any] = {"type": "divider", "thickness": float(thickness), "margin": float(margin)}
        if color:
            div["color"] = color
        self._column["items"].append(div)
        return self

    def row(self, configure: Callable[[RowBuilder], None], spacing: float = 0.0) -> ColumnBuilder:
        b = RowBuilder(spacing)
        configure(b)
        self._column["items"].append(b.build())
        return self

    def table(self, configure: Callable[[TableBuilder], None]) -> ColumnBuilder:
        b = TableBuilder()
        configure(b)
        self._column["items"].append(b.build())
        return self

    def qr(
        self,
        value: str,
        size: float = 80.0,
        fill_color: Optional[str] = None,
        back_color: Optional[str] = None,
    ) -> ColumnBuilder:
        qr_comp: Dict[str, Any] = {"type": "qr", "value": str(value), "size": float(size)}
        if fill_color:
            qr_comp["fill_color"] = fill_color
        if back_color:
            qr_comp["back_color"] = back_color
        self._column["items"].append(qr_comp)
        return self

    def qr_code(self, value: str, size: float = 80.0, **kwargs) -> ColumnBuilder:
        return self.qr(value, size=size, **kwargs)

    def barcode(
        self,
        value: str,
        barcode_type: str = "code128",
        width: float = 150.0,
        height: float = 40.0,
        include_text: bool = True,
    ) -> ColumnBuilder:
        self._column["items"].append({
            "type": "barcode",
            "value": str(value),
            "barcode_type": barcode_type,
            "width": float(width),
            "height": float(height),
            "include_text": include_text,
        })
        return self

    def container(self, configure: Callable[[ContainerBuilder], None]) -> ColumnBuilder:
        b = ContainerBuilder()
        configure(b)
        self._column["items"].append(b.build())
        return self

    def image(
        self,
        source: str,
        width: Optional[float] = None,
        height: Optional[float] = None,
        fit: Optional[str] = None,
        alignment: Optional[str] = None,
    ) -> ColumnBuilder:
        img: Dict[str, Any] = {"type": "image", "source": source}
        if width is not None:
            img["width"] = float(width)
        if height is not None:
            img["height"] = float(height)
        if fit:
            img["fit"] = fit
        if alignment:
            img["alignment"] = alignment
        self._column["items"].append(img)
        return self

    def chart(
        self,
        chart_type: str = "bar",
        title: Optional[str] = None,
        labels: Optional[list] = None,
        values: Optional[list] = None,
        series: Optional[list] = None,
        width: float = 400.0,
        height: float = 200.0,
        colors: Optional[list] = None,
        theme: str = "light",
        donut: bool = False,
    ) -> ColumnBuilder:
        c: Dict[str, Any] = {
            "type": "chart",
            "chart_type": chart_type,
            "width": float(width),
            "height": float(height),
            "theme": theme,
            "donut": donut,
        }
        if title:
            c["title"] = title
        if labels is not None:
            c["labels"] = labels
        if values is not None:
            c["values"] = values
        if series is not None:
            c["series"] = series
        if colors is not None:
            c["colors"] = colors
        self._column["items"].append(c)
        return self

    def build(self) -> Dict[str, Any]:
        return dict(self._column)


class SingleContainerBuilder:
    def __init__(self):
        self._child: Optional[Dict[str, Any]] = None

    def set_child(self, comp: Any):
        self._child = comp.build() if hasattr(comp, "build") else comp

    def text(self, value: str, configure: Optional[Callable[[TextBuilder], None]] = None) -> SingleContainerBuilder:
        b = TextBuilder(value)
        if configure:
            configure(b)
        self.set_child(b)
        return self

    def row(self, configure: Callable[[RowBuilder], None], spacing: float = 0.0) -> SingleContainerBuilder:
        b = RowBuilder(spacing)
        configure(b)
        self.set_child(b)
        return self

    def column(self, configure: Callable[[ColumnBuilder], None], spacing: float = 0.0) -> SingleContainerBuilder:
        b = ColumnBuilder(spacing)
        configure(b)
        self.set_child(b)
        return self

    def table(self, configure: Callable[[TableBuilder], None]) -> SingleContainerBuilder:
        b = TableBuilder()
        configure(b)
        self.set_child(b)
        return self

    def qr(self, value: str, size: float = 80.0, **kwargs) -> SingleContainerBuilder:
        qr_comp: Dict[str, Any] = {"type": "qr", "value": str(value), "size": float(size), **kwargs}
        self.set_child(qr_comp)
        return self

    def qr_code(self, value: str, size: float = 80.0, **kwargs) -> SingleContainerBuilder:
        return self.qr(value, size=size, **kwargs)

    def barcode(self, value: str, **kwargs) -> SingleContainerBuilder:
        bc: Dict[str, Any] = {"type": "barcode", "value": str(value), **kwargs}
        self.set_child(bc)
        return self

    def build(self) -> Optional[Dict[str, Any]]:
        return self._child


class ReportDocument:
    """
    Root document definition builder for FlowPDF.
    """
    def __init__(self):
        self._doc: Dict[str, Any] = {
            "version": "2.0",
            "page": PageConfigBuilder().build(),
            "content": {"type": "column", "items": []},
        }

    def title(self, title: str) -> ReportDocument:
        self._doc["title"] = title
        return self

    def author(self, author: str) -> ReportDocument:
        self._doc["author"] = author
        return self

    def page(self, configure: Callable[[PageConfigBuilder], None]) -> ReportDocument:
        b = PageConfigBuilder()
        configure(b)
        self._doc["page"] = b.build()
        return self

    def header(self, configure: Callable[[SingleContainerBuilder], None]) -> ReportDocument:
        b = SingleContainerBuilder()
        configure(b)
        child = b.build()
        if child:
            self._doc["header"] = child
        return self

    def content(self, configure: Callable[[ColumnBuilder], None]) -> ReportDocument:
        b = ColumnBuilder()
        configure(b)
        self._doc["content"] = b.build()
        return self

    def footer(self, configure: Callable[[SingleContainerBuilder], None]) -> ReportDocument:
        b = SingleContainerBuilder()
        configure(b)
        child = b.build()
        if child:
            self._doc["footer"] = child
        return self

    def add_font(self, name: str, path: Optional[str] = None, data: Optional[str] = None) -> ReportDocument:
        if "fonts" not in self._doc:
            self._doc["fonts"] = []
        font_def: Dict[str, Any] = {"name": name}
        if path:
            font_def["path"] = path
        if data:
            font_def["data"] = data
        self._doc["fonts"].append(font_def)
        return self

    @staticmethod
    def register_font(name: str, font_bytes: Union[bytes, bytearray]) -> bool:
        """Registers a TrueType font globally in the native Rust core."""
        from .native import FlowPdfEngine
        return FlowPdfEngine.register_font(name, font_bytes)

    def build(self) -> Dict[str, Any]:
        return dict(self._doc)

    def to_json(self, indent: Optional[int] = 2) -> str:
        return json.dumps(self.build(), indent=indent, ensure_ascii=False)

    def render_pdf(self, data: Optional[Union[Dict[str, Any], list]] = None) -> bytes:
        """
        In-process direct native rendering using FlowPdfEngine (Rust Core).
        """
        from .native import FlowPdfEngine
        return FlowPdfEngine.render_pdf(self.build(), data)

    @staticmethod
    def extract_text(pdf_bytes: bytes) -> str:
        """Extracts text from PDF bytes using native Rust Core."""
        from .native import FlowPdfEngine
        return FlowPdfEngine.extract_text(pdf_bytes)

    @staticmethod
    def extract_document(pdf_bytes: bytes, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extracts structured document data from PDF bytes using native Rust Core."""
        from .native import FlowPdfEngine
        return FlowPdfEngine.extract_document(pdf_bytes, options)
