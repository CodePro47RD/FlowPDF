import os
from unittest.mock import patch, MagicMock
import pytest
from sdk.python.reportforge_sdk import (
    ReportForgeClient,
    ReportResponse,
    AuthenticationError,
    ValidationError,
    NotFoundError,
)


def test_sdk_response_save(tmp_path):
    out_file = tmp_path / "saved_report.pdf"
    content = b"%PDF-1.4 test binary data"
    resp = ReportResponse(content=content, status_code=200, report_id="rep-123")

    saved_path = resp.save(out_file)
    assert os.path.exists(saved_path)
    assert open(saved_path, "rb").read() == content
    assert resp.size == len(content)


def test_sdk_client_auth_header():
    client = ReportForgeClient(base_url="https://reports.test.com", api_key="rf_live_sample_key")
    assert client._session.headers.get("X-API-Key") == "rf_live_sample_key"


@patch("requests.Session.request")
def test_sdk_client_generate_success(mock_request):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b"%PDF-1.4 binary content"
    mock_resp.headers = {"Content-Type": "application/pdf"}
    mock_request.return_value = mock_resp

    client = ReportForgeClient(base_url="https://reports.test.com", api_key="rf_live_key")
    resp = client.generate(
        template="invoice",
        data={"customer": "Juan Perez", "total": 15000},
    )

    assert resp.bytes.startswith(b"%PDF-")
    assert resp.status_code == 200


@patch("requests.Session.request")
def test_sdk_client_auth_error(mock_request):
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized"
    mock_request.return_value = mock_resp

    client = ReportForgeClient(base_url="https://reports.test.com", api_key="bad_key")
    with pytest.raises(AuthenticationError):
        client.generate(template="invoice", data={})


@patch("requests.Session.request")
def test_sdk_client_validation_error(mock_request):
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = "Bad Request"
    mock_request.return_value = mock_resp

    client = ReportForgeClient(base_url="https://reports.test.com", api_key="rf_live_key")
    with pytest.raises(ValidationError):
        client.generate(template="invoice", data={})
