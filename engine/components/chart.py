"""
Chart component for ReportForge.
Renders bar, line, pie, and comparative charts using high-resolution Matplotlib rendering.
"""

from __future__ import annotations
import io
from typing import List, Optional, Sequence, Union, Dict, Any
import matplotlib
# Ensure non-GUI backend
matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from reportlab.lib.utils import ImageReader

from ..core.element import Component
from ..core.geometry import Size, Rect, HorizontalAlignment, VerticalAlignment
from ..core.constraints import BoxConstraints
from ..core.colors import Color, Colors
from ..core.context import LayoutContext, DrawContext
from ..core.exceptions import RenderError


class Chart(Component):
    """
    Renders business and statistical charts with high DPI clarity.
    """

    PALETTE = [
        "#1E40AF",  # Blue
        "#059669",  # Green
        "#D97706",  # Amber
        "#DC2626",  # Red
        "#7C3AED",  # Purple
        "#0284C7",  # Sky
        "#475569",  # Slate
    ]

    def __init__(
        self,
        chart_type: str = "bar",  # "bar", "line", "pie", "area", "multi_bar"
        labels: Optional[Sequence[str]] = None,
        values: Optional[Sequence[float]] = None,
        series: Optional[Sequence[Dict[str, Any]]] = None,
        *,
        title: Optional[str] = None,
        width: float = 400.0,
        height: float = 200.0,
        colors: Optional[Sequence[str]] = None,
        horizontal_alignment: HorizontalAlignment = HorizontalAlignment.CENTER,
    ):
        self.chart_type = chart_type.lower()
        self.labels = list(labels) if labels is not None else []
        self.values = list(values) if values is not None else []
        self.series = list(series) if series is not None else []
        self.title = title
        self.target_width = float(width)
        self.target_height = float(height)
        self.colors = list(colors) if colors is not None else self.PALETTE
        self.horizontal_alignment = horizontal_alignment

        self._image_cache: Optional[ImageReader] = None

    def _render_chart_image(self) -> ImageReader:
        if self._image_cache is not None:
            return self._image_cache

        dpi = 200
        fig_w = self.target_width / 72.0
        fig_h = self.target_height / 72.0

        fig = Figure(figsize=(fig_w, fig_h), dpi=dpi)
        FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)

        # Clean typography styling
        fig.patch.set_facecolor("#FFFFFF")
        ax.set_facecolor("#FFFFFF")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#CBD5E1")
        ax.spines["bottom"].set_color("#CBD5E1")
        ax.tick_params(colors="#475569", labelsize=8)

        if self.title:
            ax.set_title(self.title, fontsize=10, fontweight="bold", color="#0F172A", pad=10)

        # Plot depending on chart type
        if self.chart_type == "pie":
            vals = self.values
            if not vals and self.series:
                vals = self.series[0].get("values", [])
            wedges, texts, autotexts = ax.pie(
                vals,
                labels=self.labels if self.labels else None,
                colors=self.colors[: len(vals)],
                autopct="%1.1f%%",
                startangle=140,
                textprops={"fontsize": 8, "color": "#1E293B"},
            )
            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontweight("bold")

        elif self.chart_type == "line":
            if self.series:
                for idx, s in enumerate(self.series):
                    c = s.get("color", self.colors[idx % len(self.colors)])
                    ax.plot(
                        self.labels,
                        s.get("values", []),
                        marker="o",
                        linewidth=2,
                        label=s.get("name", f"Series {idx+1}"),
                        color=c,
                    )
                ax.legend(frameon=False, fontsize=8)
            else:
                c = self.colors[0]
                ax.plot(self.labels, self.values, marker="o", linewidth=2, color=c)

        elif self.chart_type in ("bar", "multi_bar"):
            import numpy as np

            if self.series:
                x = np.arange(len(self.labels))
                num_series = len(self.series)
                bar_w = 0.8 / num_series
                for idx, s in enumerate(self.series):
                    c = s.get("color", self.colors[idx % len(self.colors)])
                    offset = (idx - (num_series - 1) / 2.0) * bar_w
                    ax.bar(
                        x + offset,
                        s.get("values", []),
                        width=bar_w,
                        label=s.get("name", f"Series {idx+1}"),
                        color=c,
                    )
                ax.set_xticks(x)
                ax.set_xticklabels(self.labels)
                ax.legend(frameon=False, fontsize=8)
            else:
                c = self.colors[: len(self.values)] if len(self.colors) >= len(self.values) else self.colors[0]
                ax.bar(self.labels, self.values, color=c, width=0.6)

        elif self.chart_type == "area":
            if self.series:
                for idx, s in enumerate(self.series):
                    c = s.get("color", self.colors[idx % len(self.colors)])
                    ax.fill_between(self.labels, s.get("values", []), color=c, alpha=0.3)
                    ax.plot(self.labels, s.get("values", []), color=c, linewidth=1.5, label=s.get("name"))
                ax.legend(frameon=False, fontsize=8)
            else:
                c = self.colors[0]
                ax.fill_between(self.labels, self.values, color=c, alpha=0.3)
                ax.plot(self.labels, self.values, color=c, linewidth=2)

        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="PNG", dpi=dpi, facecolor=fig.get_facecolor(), edgecolor="none")
        buf.seek(0)
        self._image_cache = ImageReader(buf)
        return self._image_cache

    def measure(self, constraints: BoxConstraints, context: LayoutContext) -> Size:
        return constraints.constrain(Size(self.target_width, self.target_height))

    def draw(self, rect: Rect, context: DrawContext) -> None:
        img_reader = self._render_chart_image()
        w = min(rect.width, self.target_width)
        h = min(rect.height, self.target_height)

        draw_x = rect.x
        if self.horizontal_alignment == HorizontalAlignment.CENTER:
            draw_x = rect.x + (rect.width - w) / 2.0
        elif self.horizontal_alignment == HorizontalAlignment.RIGHT:
            draw_x = rect.x + rect.width - w

        draw_y = rect.y + (rect.height - h) / 2.0
        canvas_y = context.to_canvas_y(draw_y, h)

        context.save_state()
        context.canvas.drawImage(img_reader, draw_x, canvas_y, width=w, height=h, mask="auto")
        context.restore_state()
