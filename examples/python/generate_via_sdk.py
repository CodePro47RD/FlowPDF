"""
Example: Consuming FlowPDF via the official Python SDK.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sdk/python")))

from flowpdf import FlowPdfClient


def main():
    # 1. Initialize client with credentials
    client = FlowPdfClient(
        base_url="http://localhost:8000",
        api_key="rf_live_sample_key_here",
    )

    # 2. Define document payload
    document_def = {
        "page": {"size": "A4", "orientation": "portrait", "margin": 15},
        "header": {
            "type": "text",
            "value": "ESTADO DE CUENTA - {{ customer.name }}",
            "style": "h2",
        },
        "content": [
            {
                "type": "text",
                "value": "Resumen consolidado al corte de {{ cutoff_date }}:",
                "style": "body",
            },
            {
                "type": "spacer",
                "height": 10,
            },
            {
                "type": "table",
                "source": "movements",
                "columns": [
                    {"field": "date", "title": "Fecha", "width": 80, "format": "date"},
                    {"field": "concept", "title": "Concepto", "flex": 2},
                    {"field": "amount", "title": "Monto", "width": 90, "format": "currency", "align": "right"},
                ],
                "zebra": True,
            },
        ],
        "footer": {
            "type": "page_number",
            "format": "Página {page} de {total}",
            "alignment": "right",
        },
    }

    data = {
        "customer": {"name": "Inversiones del Norte S.R.L."},
        "cutoff_date": "2026-11-12",
        "movements": [
            {"date": "2026-11-01", "concept": "Depósito en Cuenta Corriente", "amount": 250000.0},
            {"date": "2026-11-04", "concept": "Pago a Proveedores - Lote 89", "amount": -85400.0},
            {"date": "2026-11-08", "concept": "Cobro de Factura B0100234", "amount": 142000.0},
        ],
    }

    print("Enviando solicitud de generación...")
    response = client.generate(
        document=document_def,
        data=data,
        format="pdf",
    )

    output_filename = "estado_cuenta.pdf"
    response.save(output_filename)
    print(f"Documento guardado exitosamente en: {output_filename} ({response.size} bytes)")


if __name__ == "__main__":
    main()
