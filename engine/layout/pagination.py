"""
Pagination algorithm for ReportForge.
Measures headers, footers, and splits flowable body components into page slices.
"""

from __future__ import annotations
from typing import List, Optional, Tuple
from ..core.element import Component
from ..core.page import PageSettings
from ..core.geometry import Size
from ..core.constraints import BoxConstraints
from ..core.context import LayoutContext
from ..core.exceptions import LayoutOverflowError


class Paginator:
    """
    Partitions a content tree into distinct page slices.
    """

    def __init__(
        self,
        page_settings: PageSettings,
        header: Optional[Component] = None,
        footer: Optional[Component] = None,
        header_spacing: float = 10.0,
        footer_spacing: float = 10.0,
        max_pages: int = 500,
    ):
        self.page_settings = page_settings
        self.header = header
        self.footer = footer
        self.header_spacing = float(header_spacing)
        self.footer_spacing = float(footer_spacing)
        self.max_pages = max_pages

    def calculate_body_budget(self, context: LayoutContext) -> Tuple[float, float]:
        """Returns (available_width, available_height) for body content."""
        content_area = self.page_settings.content_area
        avail_w = content_area.width
        avail_h = content_area.height

        if self.header is not None:
            h_size = self.header.measure(
                BoxConstraints(min_width=avail_w, max_width=avail_w), context
            )
            avail_h -= (h_size.height + self.header_spacing)

        if self.footer is not None:
            f_size = self.footer.measure(
                BoxConstraints(min_width=avail_w, max_width=avail_w), context
            )
            avail_h -= (f_size.height + self.footer_spacing)

        return avail_w, max(0.0, avail_h)

    def paginate(self, content: Component, context: LayoutContext) -> List[Component]:
        """Splits content into an ordered list of components, one per page."""
        avail_w, avail_h = self.calculate_body_budget(context)

        # Quick check: does the entire content fit on a single page?
        content_size = content.measure(
            BoxConstraints(min_width=avail_w, max_width=avail_w), context
        )
        if content_size.height <= avail_h:
            return [content]

        pages: List[Component] = []
        current_component: Optional[Component] = content
        page_count = 0

        while current_component is not None:
            page_count += 1
            if page_count > self.max_pages:
                raise LayoutOverflowError(
                    f"Document exceeded maximum allowable pages ({self.max_pages}). Check for infinite layout loops."
                )

            # Check if remaining fits completely in this page
            c_size = current_component.measure(
                BoxConstraints(min_width=avail_w, max_width=avail_w), context
            )
            if c_size.height <= avail_h:
                pages.append(current_component)
                break

            # Slicing across page boundary
            if current_component.can_split():
                fitted, remaining = current_component.split(avail_h, context)
                if fitted is not None:
                    pages.append(fitted)
                    current_component = remaining
                else:
                    # Item could not split within budget: force it onto this page to prevent infinite loop
                    pages.append(current_component)
                    break
            else:
                # Unbreakable component too tall: place on its own page
                pages.append(current_component)
                break

        return pages if pages else [content]
