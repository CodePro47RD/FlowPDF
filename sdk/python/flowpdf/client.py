"""
Client implementation for the FlowPDF Python SDK.
"""

from __future__ import annotations
import time
from typing import Any, Dict, Optional, Union
import requests

from .exceptions import (
    FlowPdfSDKError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    ServerError,
    TimeoutError,
)
from .response import ReportResponse


class FlowPdfClient:
    """
    Official Python Client for the FlowPDF Document Generation API.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = float(timeout)
        self.max_retries = max(1, int(max_retries))

        self._session = requests.Session()
        if self.api_key:
            self._session.headers.update({"X-API-Key": self.api_key})
        self._session.headers.update({"User-Agent": "FlowPDF-Python-SDK/1.0.0"})

    def _url(self, path: str) -> str:
        return f"{self.base_url}/api/v1/{path.lstrip('/')}"

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = self._url(path)
        kwargs.setdefault("timeout", self.timeout)

        for attempt in range(1, self.max_retries + 1):
            try:
                res = self._session.request(method, url, **kwargs)

                if res.status_code in (401, 403):
                    raise AuthenticationError(f"Authentication failed: {res.text}")
                elif res.status_code == 404:
                    raise NotFoundError(f"Resource not found at {url}: {res.text}")
                elif res.status_code == 400:
                    raise ValidationError(f"Invalid request or template syntax: {res.text}")
                elif res.status_code >= 500:
                    if attempt < self.max_retries:
                        time.sleep(0.5 * attempt)
                        continue
                    raise ServerError(f"Server error ({res.status_code}): {res.text}")

                return res

            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    time.sleep(0.5 * attempt)
                    continue
                raise FlowPdfSDKError(f"HTTP request to {url} failed: {e}") from e

        raise FlowPdfSDKError(f"Failed after {self.max_retries} attempts.")

    def generate(
        self,
        template: Optional[str] = None,
        document: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        format: str = "pdf",
        async_mode: bool = False,
        wait: bool = False,
        poll_interval: float = 1.0,
        max_wait: float = 60.0,
    ) -> ReportResponse:
        """
        Generate a report either from a stored template name or inline JSON definition.
        """
        payload = {
            "template": template,
            "document": document,
            "data": data or {},
            "format": format,
            "async_mode": async_mode,
            "response_type": "binary" if not async_mode else "json",
        }

        res = self._request("POST", "reports/generate/", json=payload)

        # 1. Direct synchronous binary response
        if not async_mode and res.headers.get("Content-Type", "").startswith("application/pdf"):
            return ReportResponse(content=res.content, status_code=res.status_code)

        # 2. Async job response
        data_json = res.json()
        report_id = data_json.get("id")

        if async_mode and wait:
            return self.wait_for_completion(
                report_id=report_id,
                poll_interval=poll_interval,
                max_wait=max_wait,
            )

        return ReportResponse(
            content=res.content,
            status_code=res.status_code,
            content_type=res.headers.get("Content-Type", "application/json"),
            report_id=report_id,
        )

    def preview(
        self,
        document: Optional[Dict[str, Any]] = None,
        template: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> ReportResponse:
        """Instantly preview document rendering as raw PDF binary."""
        payload = {
            "template": template,
            "document": document,
            "data": data or {},
        }
        res = self._request("POST", "reports/preview/", json=payload)
        return ReportResponse(content=res.content, status_code=res.status_code)

    def get_report_status(self, report_id: str) -> Dict[str, Any]:
        """Fetch processing status and metadata for a report job."""
        res = self._request("GET", f"reports/{report_id}/")
        return res.json()

    def download_report(self, report_id: str) -> ReportResponse:
        """Download binary PDF for a completed report job."""
        res = self._request("GET", f"reports/{report_id}/download/")
        return ReportResponse(
            content=res.content,
            status_code=res.status_code,
            content_type=res.headers.get("Content-Type", "application/pdf"),
            report_id=report_id,
        )

    def wait_for_completion(
        self,
        report_id: str,
        poll_interval: float = 1.0,
        max_wait: float = 60.0,
    ) -> ReportResponse:
        """Poll report status until finished, then download the resulting document."""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            info = self.get_report_status(report_id)
            curr_status = info.get("status")

            if curr_status == "completed":
                return self.download_report(report_id)
            elif curr_status == "failed":
                raise ServerError(f"Report generation job failed: {info.get('error_message')}")

            time.sleep(poll_interval)

        raise TimeoutError(f"Report job {report_id} did not finish within {max_wait}s.")

    def list_templates(self) -> Dict[str, Any]:
        """List templates belonging to the authenticated tenant."""
        res = self._request("GET", "templates/")
        return res.json()

    def create_template(
        self,
        name: str,
        definition: Dict[str, Any],
        version: str = "1.0",
        description: str = "",
    ) -> Dict[str, Any]:
        """Upload and store a reusable document template."""
        payload = {
            "name": name,
            "version": version,
            "description": description,
            "definition": definition,
        }
        res = self._request("POST", "templates/", json=payload)
        return res.json()
