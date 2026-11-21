"""
Response wrapper for generated documents in the FlowPDF Python SDK.
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Optional, Union, Generator


class ReportResponse:
    """
    Represents the output of a report generation request.
    Provides convenience methods to inspect, stream, or write the PDF to disk.
    """

    def __init__(
        self,
        content: bytes,
        status_code: int = 200,
        content_type: str = "application/pdf",
        report_id: Optional[str] = None,
    ):
        self._content = content
        self.status_code = status_code
        self.content_type = content_type
        self.report_id = report_id

    @property
    def bytes(self) -> bytes:
        """Raw binary content of the generated document."""
        return self._content

    @property
    def size(self) -> int:
        """Size of document in bytes."""
        return len(self._content)

    def save(self, file_path: Union[str, Path]) -> str:
        """
        Save the PDF binary directly to the specified destination path.
        Creates parent directories automatically if they do not exist.
        """
        p = Path(file_path).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "wb") as f:
            f.write(self._content)
        return str(p)

    def stream(self, chunk_size: int = 8192) -> Generator[bytes, None, None]:
        """Yield chunks of binary content for memory-efficient streaming."""
        for i in range(0, len(self._content), chunk_size):
            yield self._content[i : i + chunk_size]

    def __repr__(self) -> str:
        return f"<ReportResponse status={self.status_code} size={self.size} bytes id={self.report_id}>"
