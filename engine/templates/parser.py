"""
Template compiler and AST builder for ReportForge.
Transforms JSON template definitions and data context into a fully composed Document.
"""

from __future__ import annotations
import json
from typing import Any, Dict, List, Optional, Union
from pydantic import ValidationError

from ..core.document import Document
from ..core.element import Component
from ..core.page import PageSettings, PageSizes, PageOrientation
from ..core.geometry import EdgeInsets, HorizontalAlignment, VerticalAlignment
from ..core.typography import TextStyle, Typography
from ..core.colors import Color, Colors
from ..core.units import mm, pt
from ..core.exceptions import TemplateSyntaxError, TemplateDataError

from ..components.text import Text
from ..components.container import Container
from ..components.column import Column
from ..components.row import Row, RowItem
from ..components.spacer import Spacer
from ..components.divider import Divider
from ..components.page_number import PageNumber
from ..components.image import Image, ImageFit
from ..components.table import Table, TableColumn, TableRow, TableCell
from ..components.qr import QRCode
from ..components.barcode import Barcode
from ..components.chart import Chart

from .schema import (
    DocumentPayloadSchema,
    DocumentTemplateSchema,
    AnyComponentSchema,
    TextComponentSchema,
    ImageComponentSchema,
    SpacerComponentSchema,
    DividerComponentSchema,
    PageNumberComponentSchema,
    ColumnComponentSchema,
    RowComponentSchema,
    ContainerComponentSchema,
    TableComponentSchema,
    ChartComponentSchema,
    QRComponentSchema,
    BarcodeComponentSchema,
    RowItemSchema,
)
from .security import interpolate_text, get_nested_value
from .formatters import apply_formatter


class TemplateCompiler:
    """
    Compiles declarative template schemas into concrete Document component trees.
    """

    def __init__(self, asset_resolver: Optional[Any] = None):
        self.asset_resolver = asset_resolver

    def compile(self, payload_input: Union[str, dict, DocumentPayloadSchema]) -> Document:
        """Parse, validate, interpolate, and construct a Document instance."""
        payload: DocumentPayloadSchema
        if isinstance(payload_input, DocumentPayloadSchema):
            payload = payload_input
        elif isinstance(payload_input, str):
            try:
                raw_dict = json.loads(payload_input)
                payload = DocumentPayloadSchema.model_validate(raw_dict)
            except json.JSONDecodeError as e:
                raise TemplateSyntaxError(f"Invalid JSON template: {e}") from e
            except ValidationError as e:
                raise TemplateSyntaxError(f"Template schema validation error: {e}") from e
        elif isinstance(payload_input, dict):
            try:
                payload = DocumentPayloadSchema.model_validate(payload_input)
            except ValidationError as e:
                raise TemplateSyntaxError(f"Template schema validation error: {e}") from e
        else:
            raise TemplateSyntaxError(f"Unsupported payload input type: {type(payload_input)}")

        doc_schema = payload.document
        data = payload.data

        doc = Document()

        # 1. Page settings
        page_cfg = doc_schema.page
        size = PageSizes.get(page_cfg.size)
        orientation = (
            PageOrientation.LANDSCAPE
            if page_cfg.orientation == "landscape"
            else PageOrientation.PORTRAIT
        )

        insets = EdgeInsets(
            top=float(page_cfg.margin_top if page_cfg.margin_top is not None else mm(page_cfg.margin)),
            bottom=float(page_cfg.margin_bottom if page_cfg.margin_bottom is not None else mm(page_cfg.margin)),
            left=float(page_cfg.margin_left if page_cfg.margin_left is not None else mm(page_cfg.margin)),
            right=float(page_cfg.margin_right if page_cfg.margin_right is not None else mm(page_cfg.margin)),
        )
        doc.page(size=size, orientation=orientation, margin=insets)

        # 2. Header
        if doc_schema.header is not None:
            doc.header(self._build_component(doc_schema.header, data))

        # 3. Content
        if isinstance(doc_schema.content, list):
            body_children = [self._build_component(c, data) for c in doc_schema.content]
            doc.content(Column(body_children, spacing=8.0))
        else:
            doc.content(self._build_component(doc_schema.content, data))

        # 4. Footer
        if doc_schema.footer is not None:
            doc.footer(self._build_component(doc_schema.footer, data))

        return doc

    def _resolve_text_style(self, preset_name: Optional[str]) -> TextStyle:
        if not preset_name:
            return Typography.BODY
        name = preset_name.lower().strip()
        lookup = {
            "h1": Typography.H1,
            "h2": Typography.H2,
            "h3": Typography.H3,
            "h4": Typography.H4,
            "body": Typography.BODY,
            "body_bold": Typography.BODY_BOLD,
            "body_muted": Typography.BODY_MUTED,
            "caption": Typography.CAPTION,
            "caption_bold": Typography.CAPTION_BOLD,
            "code": Typography.CODE,
        }
        return lookup.get(name, Typography.BODY)

    def _build_component(self, comp_schema: AnyComponentSchema, data: Dict[str, Any]) -> Component:
        t = comp_schema.type

        if t == "text":
            assert isinstance(comp_schema, TextComponentSchema)
            val = interpolate_text(comp_schema.value, data)
            base_style = self._resolve_text_style(comp_schema.style)

            # Apply style overrides
            style = base_style.copy_with(
                font_size=comp_schema.font_size,
                color=comp_schema.color,
                bold=comp_schema.bold,
                italic=comp_schema.italic,
                underline=comp_schema.underline,
                strike=comp_schema.strike,
            )
            align = HorizontalAlignment(comp_schema.alignment) if comp_schema.alignment else HorizontalAlignment.LEFT
            return Text(val, style=style, alignment=align)

        elif t == "spacer":
            assert isinstance(comp_schema, SpacerComponentSchema)
            return Spacer(height=comp_schema.height)

        elif t == "divider":
            assert isinstance(comp_schema, DividerComponentSchema)
            return Divider(
                thickness=comp_schema.thickness,
                color=comp_schema.color,
                margin_vertical=comp_schema.margin,
            )

        elif t == "page_number":
            assert isinstance(comp_schema, PageNumberComponentSchema)
            style = self._resolve_text_style(comp_schema.style)
            align = HorizontalAlignment(comp_schema.alignment)
            return PageNumber(format_str=comp_schema.format, style=style, alignment=align)

        elif t == "image":
            assert isinstance(comp_schema, ImageComponentSchema)
            src = interpolate_text(comp_schema.source, data)
            fit = comp_schema.fit or "contain"
            align = HorizontalAlignment(comp_schema.alignment) if comp_schema.alignment else HorizontalAlignment.CENTER
            return Image(
                source=src,
                width=comp_schema.width,
                height=comp_schema.height,
                fit=fit,
                horizontal_alignment=align,
            )

        elif t == "column":
            assert isinstance(comp_schema, ColumnComponentSchema)
            children = [self._build_component(item, data) for item in comp_schema.items]
            return Column(children, spacing=comp_schema.spacing)

        elif t == "row":
            assert isinstance(comp_schema, RowComponentSchema)
            row = Row(spacing=comp_schema.spacing)
            if comp_schema.vertical_alignment:
                row.vertical_alignment = VerticalAlignment(comp_schema.vertical_alignment)

            for item in comp_schema.items:
                if isinstance(item, RowItemSchema):
                    child_comp = self._build_component(item.item, data)
                    if item.width is not None:
                        row.constant_item(item.width, child_comp)
                    elif item.flex is not None:
                        row.relative_item(item.flex, child_comp)
                    else:
                        row.relative_item(1.0, child_comp)
                else:
                    child_comp = self._build_component(item, data)
                    row.relative_item(1.0, child_comp)
            return row

        elif t == "container":
            assert isinstance(comp_schema, ContainerComponentSchema)
            child_comp = self._build_component(comp_schema.child, data) if comp_schema.child else None
            h_align = HorizontalAlignment(comp_schema.alignment) if comp_schema.alignment else None
            return Container(
                child=child_comp,
                width=comp_schema.width,
                height=comp_schema.height,
                padding=comp_schema.padding,
                margin=comp_schema.margin,
                background_color=comp_schema.background,
                border_color=comp_schema.border_color,
                border_width=comp_schema.border_width or 0.0,
                border_radius=comp_schema.border_radius or 0.0,
                horizontal_alignment=h_align,
            )

        elif t == "table":
            assert isinstance(comp_schema, TableComponentSchema)
            columns: List[TableColumn] = []
            for col in comp_schema.columns:
                columns.append(
                    TableColumn(
                        header=col.title,
                        width=col.width,
                        flex=col.flex,
                        alignment=HorizontalAlignment(col.align) if col.align else HorizontalAlignment.LEFT,
                    )
                )

            # Retrieve rows from data source or static data
            raw_rows: List[Dict[str, Any]] = []
            if comp_schema.source:
                val = get_nested_value(data, comp_schema.source)
                if isinstance(val, list):
                    raw_rows = val
            elif comp_schema.data:
                raw_rows = comp_schema.data

            formatted_table_rows: List[TableRow] = []
            for row_dict in raw_rows:
                cells: List[TableCell] = []
                for col in comp_schema.columns:
                    field_key = col.field or col.title
                    raw_val = get_nested_value(row_dict, field_key) if isinstance(row_dict, dict) else ""
                    formatted_val = apply_formatter(raw_val, col.format)
                    align = HorizontalAlignment(col.align) if col.align else HorizontalAlignment.LEFT
                    cells.append(TableCell(content=formatted_val, alignment=align))
                formatted_table_rows.append(TableRow(cells=cells))

            return Table(
                columns=columns,
                rows=formatted_table_rows,
                header_background=comp_schema.header_background,
                zebra_color=comp_schema.zebra_color if comp_schema.zebra else None,
                border_color=comp_schema.border_color,
                border_width=comp_schema.border_width if comp_schema.border_width is not None else 0.5,
                repeat_header=comp_schema.repeat_header if comp_schema.repeat_header is not None else True,
            )

        elif t == "chart":
            assert isinstance(comp_schema, ChartComponentSchema)
            # Resolve labels and values if provided as data paths
            labels: List[str] = []
            if isinstance(comp_schema.labels, str):
                val = get_nested_value(data, comp_schema.labels)
                labels = list(val) if isinstance(val, list) else []
            elif isinstance(comp_schema.labels, list):
                labels = comp_schema.labels

            values: List[float] = []
            if isinstance(comp_schema.values, str):
                val = get_nested_value(data, comp_schema.values)
                values = [float(x) for x in val] if isinstance(val, list) else []
            elif isinstance(comp_schema.values, list):
                values = comp_schema.values

            series: List[Dict[str, Any]] = []
            if isinstance(comp_schema.series, str):
                val = get_nested_value(data, comp_schema.series)
                series = list(val) if isinstance(val, list) else []
            elif isinstance(comp_schema.series, list):
                series = comp_schema.series

            return Chart(
                chart_type=comp_schema.chart_type,
                labels=labels,
                values=values,
                series=series,
                title=comp_schema.title,
                width=comp_schema.width,
                height=comp_schema.height,
                colors=comp_schema.colors,
            )

        elif t == "qr":
            assert isinstance(comp_schema, QRComponentSchema)
            qr_val = interpolate_text(comp_schema.value, data)
            return QRCode(
                data=qr_val,
                size=comp_schema.size,
                fill_color=comp_schema.fill_color,
                back_color=comp_schema.back_color,
            )

        elif t == "barcode":
            assert isinstance(comp_schema, BarcodeComponentSchema)
            bc_val = interpolate_text(comp_schema.value, data)
            return Barcode(
                code=bc_val,
                barcode_type=comp_schema.barcode_type,
                width=comp_schema.width,
                height=comp_schema.height,
                include_text=comp_schema.include_text,
            )

        raise TemplateSyntaxError(f"Unknown component type: '{t}'")
