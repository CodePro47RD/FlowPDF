"""
Document orchestrator and fluent API for ReportForge.
Provides an intuitive and declarative Python builder
for composing and rendering professional multi-page PDF documents.
"""

from __future__ import annotations
from typing import Optional, Union, BinaryIO, List
from .element import Component
from .geometry import EdgeInsets
from .page import PageSettings, PageSizes, PageOrientation
from .context import LayoutContext
from .units import pt, mm
from ..layout.pagination import Paginator
from ..renderers.pdf_renderer import PDFRenderer


class Document:
    """
    Primary entry point for building and generating ReportForge documents.
    """

    def __init__(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        subject: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ):
        self.title = title
        self.author = author
        self.subject = subject
        self.keywords = keywords or []

        self.page_settings = PageSettings()
        self._header: Optional[Component] = None
        self._footer: Optional[Component] = None
        self._content: Optional[Component] = None
        self._header_spacing: float = 10.0
        self._footer_spacing: float = 10.0

    def page(
        self,
        size: Union[str, PageSizes, tuple[float, float]] = "A4",
        orientation: Union[str, PageOrientation] = PageOrientation.PORTRAIT,
        margin: Optional[Union[float, EdgeInsets]] = None,
        margin_top: Optional[float] = None,
        margin_bottom: Optional[float] = None,
        margin_left: Optional[float] = None,
        margin_right: Optional[float] = None,
    ) -> Document:
        """Configure page dimensions, orientation, and margins."""
        resolved_size = PageSizes.get(size)

        if isinstance(orientation, str):
            resolved_orientation = PageOrientation(orientation.lower())
        else:
            resolved_orientation = orientation

        if isinstance(margin, EdgeInsets):
            insets = margin
        elif isinstance(margin, (int, float)):
            insets = EdgeInsets.all(float(margin))
        else:
            insets = EdgeInsets(
                top=float(margin_top or mm(15)),
                bottom=float(margin_bottom or mm(15)),
                left=float(margin_left or mm(15)),
                right=float(margin_right or mm(15)),
            )

        self.page_settings = PageSettings(
            size=resolved_size,
            orientation=resolved_orientation,
            margin=insets,
        )
        return self

    def header(self, component: Component, spacing: float = 10.0) -> Document:
        """Set repeating header component for every page."""
        self._header = component
        self._header_spacing = float(spacing)
        return self

    def footer(self, component: Component, spacing: float = 10.0) -> Document:
        """Set repeating footer component for every page."""
        self._footer = component
        self._footer_spacing = float(spacing)
        return self

    def content(self, component: Component) -> Document:
        """Set body content for the document."""
        self._content = component
        return self

    def render(self) -> bytes:
        """Render the complete document to PDF bytes in memory."""
        return self._build(output=None)

    def generate(self, output: Union[str, BinaryIO]) -> bytes:
        """Render the complete document and write to a file path or stream."""
        return self._build(output=output)

    def _build(self, output: Optional[Union[str, BinaryIO]] = None) -> bytes:
        if self._content is None:
            from ..components.text import Text
            self._content = Text("")

        layout_context = LayoutContext(page_settings=self.page_settings)
        paginator = Paginator(
            page_settings=self.page_settings,
            header=self._header,
            footer=self._footer,
            header_spacing=self._header_spacing,
            footer_spacing=self._footer_spacing,
        )

        page_slices = paginator.paginate(self._content, layout_context)

        renderer = PDFRenderer(
            title=self.title,
            author=self.author,
            subject=self.subject,
            keywords=self.keywords,
        )

        return renderer.render_pages(
            pages_content=page_slices,
            page_settings=self.page_settings,
            header=self._header,
            footer=self._footer,
            header_spacing=self._header_spacing,
            footer_spacing=self._footer_spacing,
            output=output,
        )
