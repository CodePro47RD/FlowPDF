import pytest
from rest_framework.test import APIClient
from apps.authentication.models import Application
from apps.templates.models import Template
from apps.reports.models import ReportJob


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def tenant_app(db):
    return Application.objects.create(
        name="Test Tenant App",
        api_key=Application.generate_api_key(),
    )


@pytest.fixture
def other_tenant_app(db):
    return Application.objects.create(
        name="Other Tenant App",
        api_key=Application.generate_api_key(),
    )


@pytest.mark.django_db
def test_unauthorized_access(api_client):
    response = api_client.get("/api/v1/templates/")
    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_template_crud_and_tenant_isolation(api_client, tenant_app, other_tenant_app):
    # 1. Create template for tenant_app
    api_client.credentials(HTTP_X_API_KEY=tenant_app.api_key)

    tpl_payload = {
        "name": "sales_receipt",
        "version": "1.0",
        "description": "Standard Sales Receipt",
        "definition": {
            "page": {"size": "A4", "orientation": "portrait", "margin": 15},
            "content": {
                "type": "text",
                "value": "Recibo para {{ customer }}",
                "style": "h2",
            },
        },
    }
    create_res = api_client.post("/api/v1/templates/", tpl_payload, format="json")
    assert create_res.status_code == 201
    tpl_id = create_res.data["id"]

    # 2. List templates for tenant_app -> 1 template
    list_res = api_client.get("/api/v1/templates/")
    assert list_res.status_code == 200
    assert len(list_res.data["results"]) == 1

    # 3. Authenticate as other_tenant_app -> should see 0 templates (tenant isolation)
    api_client.credentials(HTTP_X_API_KEY=other_tenant_app.api_key)
    other_list = api_client.get("/api/v1/templates/")
    assert other_list.status_code == 200
    assert len(other_list.data["results"]) == 0


@pytest.mark.django_db
def test_report_preview_binary_pdf(api_client, tenant_app):
    api_client.credentials(HTTP_X_API_KEY=tenant_app.api_key)

    payload = {
        "document": {
            "page": {"size": "A4", "orientation": "portrait", "margin": 20},
            "content": {
                "type": "text",
                "value": "Documento de Previsualización para {{ client }}",
                "style": "h1",
            },
        },
        "data": {"client": "Empresa XYZ"},
    }

    res = api_client.post("/api/v1/reports/preview/", payload, format="json")
    assert res.status_code == 200
    assert res["Content-Type"] == "application/pdf"
    assert res.content.startswith(b"%PDF-")


@pytest.mark.django_db
def test_report_generate_sync_and_download(api_client, tenant_app):
    api_client.credentials(HTTP_X_API_KEY=tenant_app.api_key)

    # 1. Generate synchronous JSON response
    payload = {
        "document": {
            "page": {"size": "A4", "orientation": "portrait", "margin": 15},
            "content": [
                {
                    "type": "text",
                    "value": "Reporte Oficial #{{ report_num }}",
                    "style": "h2",
                },
                {
                    "type": "spacer",
                    "height": 10,
                },
                {
                    "type": "table",
                    "source": "rows",
                    "columns": [
                        {"field": "sku", "title": "Código", "width": 80},
                        {"field": "qty", "title": "Cantidad", "width": 60, "format": "number"},
                        {"field": "price", "title": "Precio", "width": 80, "format": "currency"},
                    ],
                },
            ],
        },
        "data": {
            "report_num": "REP-2026-99",
            "rows": [
                {"sku": "A-01", "qty": 10, "price": 150.0},
                {"sku": "B-02", "qty": 5, "price": 320.0},
            ],
        },
        "response_type": "json",
    }

    res = api_client.post("/api/v1/reports/generate/", payload, format="json")
    assert res.status_code == 201
    report_id = res.data["id"]
    assert res.data["status"] == "completed"
    assert res.data["file_size"] > 1000

    # 2. Check detail endpoint
    detail_res = api_client.get(f"/api/v1/reports/{report_id}/")
    assert detail_res.status_code == 200
    assert detail_res.data["id"] == report_id
    assert detail_res.data["status"] == "completed"

    # 3. Download generated PDF
    dl_res = api_client.get(f"/api/v1/reports/{report_id}/download/")
    assert dl_res.status_code == 200
    assert dl_res["Content-Type"] == "application/pdf"
    content = b"".join(dl_res.streaming_content)
    assert content.startswith(b"%PDF-")


@pytest.mark.django_db
def test_report_generate_from_stored_template(api_client, tenant_app):
    api_client.credentials(HTTP_X_API_KEY=tenant_app.api_key)

    # 1. Create stored template
    tpl = Template.objects.create(
        application=tenant_app,
        name="invoice_template",
        version="1.0",
        definition={
            "page": {"size": "A4", "orientation": "portrait", "margin": 15},
            "content": {
                "type": "text",
                "value": "Factura {{ invoice_id }}",
                "style": "h1",
            },
        },
    )

    # 2. Generate using template name
    payload = {
        "template": "invoice_template",
        "data": {"invoice_id": "FAC-2026-100"},
        "response_type": "binary",
    }
    res = api_client.post("/api/v1/reports/generate/", payload, format="json")
    assert res.status_code == 200
    assert res["Content-Type"] == "application/pdf"
    assert res.content.startswith(b"%PDF-")
