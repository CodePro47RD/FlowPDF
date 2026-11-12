"""
Table component for ReportForge.
Features column widths, header styling, alternating zebra rows, cell alignment,
border rendering, and automatic pagination splitting with header repetition.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Union, Any, Tuple
from ..core.element import Component
from ..core.geometry import (
    Size,
    Rect,
    Point,
    EdgeInsets,
    HorizontalAlignment,
    VerticalAlignment,
)
from ..core.constraints import BoxConstraints
from ..core.colors import Color, Colors
from ..core.typography import TextStyle, Typography
from ..core.context import LayoutContext, DrawContext
from .text import Text


@dataclass
class TableColumn:
    """Definition of a table column."""
    header: str
    width: Optional[float] = None       # Constant width in pt
    flex: Optional[float] = 1.0         # Proportional weight
    alignment: HorizontalAlignment = HorizontalAlignment.LEFT


@dataclass
class TableCell:
    """Individual cell content and overrides."""
    content: Union[str, Component]
    alignment: Optional[HorizontalAlignment] = None
    background_color: Optional[Color] = None
    text_style: Optional[TextStyle] = None

    def as_component(
        self,
        default_style: TextStyle,
        default_alignment: HorizontalAlignment,
    ) -> Component:
        if isinstance(self.content, Component):
            return self.content
        style = self.text_style or default_style
        align = self.alignment or default_alignment
        return Text(str(self.content), style=style, alignment=align)


@dataclass
class TableRow:
    """Single row containing cells."""
    cells: List[TableCell]
    background_color: Optional[Color] = None
    is_header: bool = False


class Table(Component):
    """
    Renders structured tabular data with rich styling and automatic pagination.
    """

    def __init__(
        self,
        columns: Sequence[TableColumn | str],
        data: Optional[Sequence[Sequence[Any] | dict]] = None,
        rows: Optional[Sequence[TableRow]] = None,
        *,
        header_background: Optional[Union[Color, str]] = None,
        header_text_style: Optional[TextStyle] = None,
        row_text_style: Optional[TextStyle] = None,
        zebra_color: Optional[Union[Color, str]] = None,
        cell_padding: Optional[Union[float, EdgeInsets]] = None,
        border_color: Optional[Union[Color, str]] = None,
        border_width: float = 0.5,
        repeat_header: bool = True,
    ):
        # 1. Normalize columns
        self.columns: List[TableColumn] = []
        for col in columns:
            if isinstance(col, TableColumn):
                self.columns.append(col)
            elif isinstance(col, str):
                self.columns.append(TableColumn(header=col))

        # 2. Styling defaults
        self.header_background = (
            Color.from_any(header_background)
            if header_background is not None
            else Colors.GRAY_100
        )
        self.header_text_style = (
            header_text_style if header_text_style is not None else Typography.BODY_BOLD
        )
        self.row_text_style = (
            row_text_style if row_text_style is not None else Typography.BODY
        )
        self.zebra_color = (
            Color.from_any(zebra_color)
            if zebra_color is not None
            else Colors.BG_ZEBRA
        )

        if isinstance(cell_padding, (int, float)):
            self.cell_padding = EdgeInsets.all(cell_padding)
        elif isinstance(cell_padding, EdgeInsets):
            self.cell_padding = cell_padding
        else:
            self.cell_padding = EdgeInsets.symmetric(vertical=6.0, horizontal=8.0)

        self.border_color = (
            Color.from_any(border_color)
            if border_color is not None
            else Colors.BORDER_LIGHT
        )
        self.border_width = float(border_width)
        self.repeat_header = repeat_header

        # 3. Populate rows
        self.rows: List[TableRow] = list(rows) if rows is not None else []
        if data is not None and not self.rows:
            self._load_data(data)

    def _load_data(self, data: Sequence[Any]) -> None:
        for row_entry in data:
            row_cells: List[TableCell] = []
            if isinstance(row_entry, dict):
                for col in self.columns:
                    val = row_entry.get(col.header, "")
                    row_cells.append(TableCell(content=str(val), alignment=col.alignment))
            elif isinstance(row_entry, (list, tuple)):
                for i, val in enumerate(row_entry):
                    align = self.columns[i].alignment if i < len(self.columns) else HorizontalAlignment.LEFT
                    row_cells.append(TableCell(content=str(val), alignment=align))
            self.rows.append(TableRow(cells=row_cells))

    def _resolve_column_widths(self, total_width: float) -> List[float]:
        num_cols = len(self.columns)
        if num_cols == 0:
            return []

        resolved = [0.0] * num_cols
        fixed_sum = 0.0
        total_flex = 0.0

        for i, col in enumerate(self.columns):
            if col.width is not None and col.width > 0:
                resolved[i] = col.width
                fixed_sum += col.width
            elif col.flex is not None and col.flex > 0:
                total_flex += col.flex

        remaining = max(0.0, total_width - fixed_sum)
        for i, col in enumerate(self.columns):
            if col.width is None and col.flex is not None and total_flex > 0:
                resolved[i] = (col.flex / total_flex) * remaining

        return resolved

    def _measure_header_height(self, col_widths: List[float], context: LayoutContext) -> float:
        max_h = 0.0
        for i, col in enumerate(self.columns):
            comp = Text(col.header, style=self.header_text_style, alignment=col.alignment)
            inner_w = max(0.0, col_widths[i] - self.cell_padding.horizontal)
            size = comp.measure(BoxConstraints(min_width=0, max_width=inner_w), context)
            max_h = max(max_h, size.height)
        return max_h + self.cell_padding.vertical

    def _measure_row_height(
        self, row: TableRow, col_widths: List[float], context: LayoutContext
    ) -> float:
        max_h = 0.0
        for i, cell in enumerate(row.cells):
            col_align = self.columns[i].alignment if i < len(self.columns) else HorizontalAlignment.LEFT
            comp = cell.as_component(self.row_text_style, col_align)
            col_w = col_widths[i] if i < len(col_widths) else 0.0
            inner_w = max(0.0, col_w - self.cell_padding.horizontal)
            size = comp.measure(BoxConstraints(min_width=0, max_width=inner_w), context)
            max_h = max(max_h, size.height)
        return max_h + self.cell_padding.vertical

    def measure(self, constraints: BoxConstraints, context: LayoutContext) -> Size:
        avail_w = constraints.max_width if constraints.has_bounded_width else constraints.min_width
        col_widths = self._resolve_column_widths(avail_w)

        total_h = self._measure_header_height(col_widths, context)
        for row in self.rows:
            total_h += self._measure_row_height(row, col_widths, context)

        return constraints.constrain(Size(avail_w, total_h))

    def draw(self, rect: Rect, context: DrawContext) -> None:
        col_widths = self._resolve_column_widths(rect.width)
        layout_ctx = LayoutContext(page_settings=context.page_settings, assets=context.assets)

        curr_y = rect.y
        header_h = self._measure_header_height(col_widths, layout_ctx)

        # 1. Draw Header
        header_rect = Rect(x=rect.x, y=curr_y, width=rect.width, height=header_h)
        if self.header_background:
            context.fill_rect(header_rect, self.header_background)

        curr_x = rect.x
        for i, col in enumerate(self.columns):
            w = col_widths[i]
            comp = Text(col.header, style=self.header_text_style, alignment=col.alignment)
            cell_inner = Rect(
                x=curr_x + self.cell_padding.left,
                y=curr_y + self.cell_padding.top,
                width=max(0.0, w - self.cell_padding.horizontal),
                height=max(0.0, header_h - self.cell_padding.vertical),
            )
            comp.draw(cell_inner, context)
            curr_x += w

        # Header bottom separator
        if self.border_width > 0:
            context.draw_line(
                Point(rect.x, curr_y + header_h),
                Point(rect.right, curr_y + header_h),
                self.border_color,
                width=self.border_width * 1.5,
            )

        curr_y += header_h

        # 2. Draw Data Rows
        for row_idx, row in enumerate(self.rows):
            row_h = self._measure_row_height(row, col_widths, layout_ctx)
            row_rect = Rect(x=rect.x, y=curr_y, width=rect.width, height=row_h)

            # Background (custom or zebra stripe)
            row_bg = row.background_color
            if row_bg is None and self.zebra_color and (row_idx % 2 == 1):
                row_bg = self.zebra_color

            if row_bg is not None:
                context.fill_rect(row_rect, row_bg)

            # Cells
            curr_x = rect.x
            for i, cell in enumerate(row.cells):
                w = col_widths[i] if i < len(col_widths) else 0.0
                col_align = self.columns[i].alignment if i < len(self.columns) else HorizontalAlignment.LEFT
                comp = cell.as_component(self.row_text_style, col_align)
                cell_inner = Rect(
                    x=curr_x + self.cell_padding.left,
                    y=curr_y + self.cell_padding.top,
                    width=max(0.0, w - self.cell_padding.horizontal),
                    height=max(0.0, row_h - self.cell_padding.vertical),
                )
                comp.draw(cell_inner, context)
                curr_x += w

            # Row divider line
            if self.border_width > 0:
                context.draw_line(
                    Point(rect.x, curr_y + row_h),
                    Point(rect.right, curr_y + row_h),
                    self.border_color,
                    width=self.border_width,
                )

            curr_y += row_h

        # Outer border around table
        if self.border_width > 0:
            context.stroke_rect(
                Rect(x=rect.x, y=rect.y, width=rect.width, height=curr_y - rect.y),
                self.border_color,
                width=self.border_width,
            )

    def can_split(self) -> bool:
        return len(self.rows) > 1

    def split(
        self, available_height: float, context: LayoutContext
    ) -> Tuple[Optional[Component], Optional[Component]]:
        avail_w = context.page_settings.content_area.width
        col_widths = self._resolve_column_widths(avail_w)
        header_h = self._measure_header_height(col_widths, context)

        if available_height <= header_h:
            return None, self

        fitted_rows: List[TableRow] = []
        remaining_rows: List[TableRow] = []
        used_h = header_h

        for row in self.rows:
            row_h = self._measure_row_height(row, col_widths, context)
            if used_h + row_h <= available_height:
                fitted_rows.append(row)
                used_h += row_h
            else:
                remaining_rows.append(row)

        if not fitted_rows:
            return None, self
        if not remaining_rows:
            return self, None

        part1 = Table(
            columns=self.columns,
            rows=fitted_rows,
            header_background=self.header_background,
            header_text_style=self.header_text_style,
            row_text_style=self.row_text_style,
            zebra_color=self.zebra_color,
            cell_padding=self.cell_padding,
            border_color=self.border_color,
            border_width=self.border_width,
            repeat_header=self.repeat_header,
        )

        part2 = Table(
            columns=self.columns,
            rows=remaining_rows,
            header_background=self.header_background,
            header_text_style=self.header_text_style,
            row_text_style=self.row_text_style,
            zebra_color=self.zebra_color,
            cell_padding=self.cell_padding,
            border_color=self.border_color,
            border_width=self.border_width,
            repeat_header=self.repeat_header,
        )

        return part1, part2
