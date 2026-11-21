"""Prueba de humo del SDK de Python: tabla agrupada con los métodos fluidos de 1.0 (group_by, font_size,
padding, zebra_color, columnas auto/format), PDF real y extracción de texto."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "sdk", "python"))
from flowpdf import ReportDocument  # noqa: E402

rows = [
    {"categoria": "Servidores", "sku": "SRV-01", "descripcion": "Servidor 32GB RAM", "monto": 3850},
    {"categoria": "Servidores", "sku": "SRV-02", "descripcion": "Servidor 64GB RAM", "monto": 5200},
    {"categoria": "Redes", "sku": "SW-48P", "descripcion": "Switch 48 puertos PoE+", "monto": 1450},
]

doc = ReportDocument().content(lambda c: c.table(lambda t: (
    t.group_by("categoria", background="#E8F0FE", color="#1F3B8A")
    .font_size(8.5).padding(6, 4)
    .header_color("#FFFFFF").text_color("#111827").zebra_color("#F8FAFC")
    .column("Código", "sku", lambda col: col.auto())
    .column("Descripción", "descripcion", lambda col: col.flex(1))
    .column("Monto", "monto", lambda col: col.auto().currency().right())
    .data(rows)
)))

text = ReportDocument.extract_text(doc.render_pdf())
for k in ["Servidores", "Redes", "SRV-01", "$3850.00"]:
    if k not in text:
        raise SystemExit(f'Falta "{k}" en el PDF:\n{text}')
print("SDK Python: SMOKE TEST PASSED")
