import pytest
from engine.templates import (
    TemplateCompiler,
    DocumentPayloadSchema,
    apply_formatter,
    interpolate_text,
    get_nested_value,
    validate_safe_path,
)
from engine.core.exceptions import SecurityError, TemplateSyntaxError


def test_formatters():
    assert apply_formatter(1250.5, "currency") == "$1,250.50"
    assert apply_formatter(1250.5, "currency:€") == "€1,250.50"
    assert apply_formatter(0.185, "percentage") == "18.5%"
    assert apply_formatter("2026-11-12", "date") == "12/11/2026"
    assert apply_formatter("reportforge", "uppercase") == "REPORTFORGE"


def test_nested_value_and_security():
    data = {
        "user": {"name": "Carlos Gomez", "role": "admin"},
        "items": [10, 20, 30],
    }
    assert get_nested_value(data, "user.name") == "Carlos Gomez"
    assert get_nested_value(data, "items.1") == 20
    assert get_nested_value(data, "user.nonexistent") is None

    # Forbidden attribute access
    with pytest.raises(SecurityError):
        get_nested_value(data, "__class__.__name__")


def test_path_traversal_validation():
    with pytest.raises(SecurityError):
        validate_safe_path("../../etc/passwd")


def test_text_interpolation():
    data = {
        "invoice": {"id": "INV-2026-001", "total": 4500.0},
        "customer": "Acme Corp",
    }
    text = "Factura: {{ invoice.id }} para {{ customer }} Total: {{ invoice.total | currency }}"
    interpolated = interpolate_text(text, data)
    assert interpolated == "Factura: INV-2026-001 para Acme Corp Total: $4,500.00"


def test_json_template_to_pdf_compilation():
    payload = {
        "version": "1.0",
        "document": {
            "page": {
                "size": "A4",
                "orientation": "portrait",
                "margin": 15,
            },
            "header": {
                "type": "text",
                "value": "REPORTE DE VENTAS - {{ company.name }}",
                "style": "h2",
            },
            "content": [
                {
                    "type": "text",
                    "value": "Estimado cliente {{ customer.name }}, a continuación su resumen:",
                    "style": "body",
                },
                {
                    "type": "spacer",
                    "height": 10,
                },
                {
                    "type": "table",
                    "source": "sales",
                    "columns": [
                        {"field": "invoice", "title": "Factura", "width": 80},
                        {"field": "description", "title": "Concepto", "flex": 2},
                        {"field": "total", "title": "Total", "width": 90, "format": "currency", "align": "right"},
                    ],
                    "header_background": "#1E40AF",
                    "zebra": True,
                },
                {
                    "type": "spacer",
                    "height": 15,
                },
                {
                    "type": "qr",
                    "value": "https://verify.reportforge.com/{{ invoice_hash }}",
                    "size": 70,
                },
            ],
            "footer": {
                "type": "page_number",
                "format": "Página {page} de {total}",
                "alignment": "right",
            },
        },
        "data": {
            "company": {"name": "Industrias Globales S.A."},
            "customer": {"name": "Supermercados Nacionales"},
            "invoice_hash": "a8f7c9e1",
            "sales": [
                {"invoice": "B010001", "description": "Consultoría Estratégica", "total": 15000.0},
                {"invoice": "B010002", "description": "Licencia Enterprise Anual", "total": 48000.0},
                {"invoice": "B010003", "description": "Soporte 24/7 Nivel 3", "total": 7500.0},
            ],
        },
    }

    compiler = TemplateCompiler()
    doc = compiler.compile(payload)
    pdf_bytes = doc.render()

    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF-")


def test_invalid_json_schema_rejection():
    invalid_payload = {
        "version": "1.0",
        "document": {
            "content": {
                "type": "unsupported_non_existent_type",
            }
        },
        "data": {},
    }
    compiler = TemplateCompiler()
    with pytest.raises(TemplateSyntaxError):
        compiler.compile(invalid_payload)
