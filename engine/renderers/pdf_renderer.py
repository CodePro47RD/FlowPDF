"""
PDF Renderer for ReportForge.
Manages ReportLab canvas creation, metadata, page setup, and rendering execution.
"""

from __future__ import annotations
import io
from typing import BinaryIO, Union, List, Optional
from reportlab.pdfgen import canvas
from ..core.context import DrawContext
from ..core.geometry import Rect
from ..core.page import PageSettings
from ..core.element import Component


class PDFRenderer:
    """
    Renders partitioned page structures onto a PDF binary stream.
    """

    def __init__(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        subject: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ):
        self.title = title
        self.author = author or "ReportForge"
        self.subject = subject
        self.keywords = keywords or []

    def render_pages(
        self,
        pages_content: List[Component],
        page_settings: PageSettings,
        header: Optional[Component] = None,
        footer: Optional[Component] = None,
        header_spacing: float = 10.0,
        footer_spacing: float = 10.0,
        output: Optional[Union[str, BinaryIO]] = None,
    ) -> bytes:
        """
        Renders prepared page slices to a file path, stream, or returns bytes.
        """
        buffer: Optional[io.BytesIO] = None
        target_stream: BinaryIO

        if output is None:
            buffer = io.BytesIO()
            target_stream = buffer
        elif isinstance(output, str):
            target_stream = open(output, "wb")
        else:
            target_stream = output

        dims = page_settings.dimensions
        pdf_canvas = canvas.Canvas(
            target_stream,
            pagesize=(dims.width, dims.height),
        )

        # PDF Document Info Metadata
        if self.title:
            pdf_canvas.setTitle(self.title)
        if self.author:
            pdf_canvas.setAuthor(self.author)
        if self.subject:
            pdf_canvas.setSubject(self.subject)
        if self.keywords:
            pdf_canvas.setKeywords(self.keywords)

        total_pages = max(1, len(pages_content))
        margin = page_settings.margin

        # Bounds of the printable page inside margins
        printable_rect = Rect(
            x=margin.left,
            y=margin.top,
            width=dims.width - margin.horizontal,
            height=dims.height - margin.vertical,
        )

        try:
            for page_idx, content_slice in enumerate(pages_content, start=1):
                ctx = DrawContext(
                    canvas=pdf_canvas,
                    page_settings=page_settings,
                    page_number=page_idx,
                    total_pages=total_pages,
                )

                curr_y = printable_rect.y
                avail_h = printable_rect.height

                # 1. Render Header
                if header is not None:
                    from ..core.context import LayoutContext
                    from ..core.constraints import BoxConstraints
                    l_ctx = LayoutContext(page_settings=page_settings)
                    h_size = header.measure(
                        BoxConstraints(min_width=printable_rect.width, max_width=printable_rect.width),
                        l_ctx,
                    )
                    header_rect = Rect(
                        x=printable_rect.x,
                        y=curr_y,
                        width=printable_rect.width,
                        height=h_size.height,
                    )
                    header.draw(header_rect, ctx)
                    curr_y += h_size.height + header_spacing
                    avail_h -= (h_size.height + header_spacing)

                # 2. Render Footer (placed at bottom of printable area)
                footer_h = 0.0
                if footer is not None:
                    from ..core.context import LayoutContext
                    from ..core.constraints import BoxConstraints
                    l_ctx = LayoutContext(page_settings=page_settings)
                    f_size = footer.measure(
                        BoxConstraints(min_width=printable_rect.width, max_width=printable_rect.width),
                        l_ctx,
                    )
                    footer_h = f_size.height
                    footer_rect = Rect(
                        x=printable_rect.x,
                        y=printable_rect.bottom - footer_h,
                        width=printable_rect.width,
                        height=footer_h,
                    )
                    footer.draw(footer_rect, ctx)
                    avail_h -= (footer_h + footer_spacing)

                # 3. Render Body Content Slice
                body_rect = Rect(
                    x=printable_rect.x,
                    y=curr_y,
                    width=printable_rect.width,
                    height=max(0.0, avail_h),
                )
                content_slice.draw(body_rect, ctx)

                pdf_canvas.showPage()

            pdf_canvas.save()

        finally:
            if isinstance(output, str) and not target_stream.closed:
                target_stream.close()

        if isinstance(output, str):
            with open(output, "rb") as f:
                return f.read()
        elif buffer is not None:
            return buffer.getvalue()
        return b""
