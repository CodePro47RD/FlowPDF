# ReportForge Python SDK v2.0.0

Universal Document Engine and Fluent Report Builder SDK for Python, powered by in-process **Rust Core v2.0** and high-throughput remote HTTP rendering.

[![PyPI](https://img.shields.io/badge/pypi-v2.0.0-blue.svg)](https://pypi.org/project/reportforge/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⚡ Key Highlights

- **Ultra-Fast In-Process Generation**: Renders complete PDF documents in **~15ms - 40ms** with zero network latency using native Rust Core v2.0.
- **Embedded Multi-Platform Runtimes**: Bundles precompiled `win-x64` (`reportforge_native.dll`) and `linux-x64` (`libreportforge_native.so`) runtimes automatically loaded via `ctypes`.
- **Full Unicode & Spanish Accents Support**: Flawlessly renders Spanish accents (`á, é, í, ó, ú, ñ, Ñ`), inverted marks (`¿, ¡`), and currency symbols (`€, $, £`) with WinAnsi hexadecimal encoding.
- **Fluent Report Builder**: Declarative, composable, type-safe API for headers, tables, barcodes, QR codes, columns, rows, and cards.
- **Hybrid Architecture**: Switch between local in-process microsecond execution or cloud HTTP worker rendering with the exact same document definition.

---

## 📦 Installation

```bash
# Install from wheel or PyPI
pip install reportforge
```

Or install locally from wheel:
```bash
pip install dist/reportforge-2.0.0-py3-none-any.whl
```

---

## 🚀 Quickstart: In-Process Native PDF Generation

```python
from reportforge import ReportDocument, ReportForgeEngine

# 1. Build document declaratively with Fluent API
doc = (
    ReportDocument()
    .title("Factura Comercial Electrónica")
    .page(lambda p: p.a4().portrait().margin(15))
    .header(lambda h: (
        h.row(lambda r: (
            r.column(lambda c: (
                c.text("REPORTFORGE ENTERPRISE").style("h2").bold().color("#1E40AF"),
                c.text("Facturación Electrónica en Español: á é í ó ú ñ Ñ ¿ ¡ €").style("caption").color("#4B5563"),
            ), flex=3),
            r.column(lambda c: (
                c.qr_code("https://reportforge.io/verify/FAC-2026-9901", size=60),
            ), flex=1),
        ))
    ))
    .content(lambda c: (
        c.spacer(10),
        c.table(lambda t: (
            t.column("Código", "sku", lambda col: col.width(70)),
            t.column("Descripción del Artículo", "description", lambda col: col.flex(3)),
            t.column("Cant.", "quantity", lambda col: col.width(50).center()),
            t.column("Precio Unitario", "price", lambda col: col.width(90).right()),
            t.column("Total", "total", lambda col: col.width(90).right()),
            t.header_background("#1E40AF"),
            t.zebra(True),
            t.data([
                {"sku": "SRV-01", "description": "Licencia Enterprise ReportForge Anual", "quantity": 1, "price": "€ 1,200.00", "total": "€ 1,200.00"},
                {"sku": "SUP-02", "description": "Soporte Técnico 24/7 y Consultoría", "quantity": 2, "price": "€ 150.00", "total": "€ 300.00"},
                {"sku": "TRN-03", "description": "Capacitación de Ingeniería Avanzada", "quantity": 1, "price": "€ 450.00", "total": "€ 450.00"},
            ])
        )),
        c.spacer(15),
        c.divider(1.0, color="#CBD5E1"),
        c.spacer(5),
        c.row(lambda r: (
            r.column(lambda col: (
                col.barcode("FAC20269901", barcode_type="code128", width=160, height=35),
            ), flex=1),
            r.column(lambda col: (
                col.text("Subtotal: € 1,950.00").align("right"),
                col.text("ITBIS / IVA (18%): € 351.00").align("right"),
                col.text("Total Facturado: € 2,301.00").style("h2").bold().color("#16A34A").align("right"),
            ), flex=1),
        )),
    ))
    .footer(lambda f: (
        f.text("Documento generado in-process con ReportForge Rust Core v2.0").style("caption").center()
    ))
)

# 2. Render directly in-process to PDF in ~30 ms!
pdf_bytes = doc.render_pdf()

with open("factura_electronica.pdf", "wb") as f:
    f.write(pdf_bytes)

print(f"✅ PDF generado exitosamente ({len(pdf_bytes)} bytes)!")
```

---

## 🌐 Remote HTTP Rendering (Cloud / Server)

```python
from reportforge import ReportForgeClient, ReportDocument

client = ReportForgeClient(base_url="http://localhost:8000", api_key="secret-api-key")

doc = (
    ReportDocument()
    .title("Reporte Remoto")
    .content(lambda c: c.text("Generado en worker asíncrono con Celery y Redis").style("h1"))
)

# Render via HTTP
response = client.render(template_data=doc.build(), format="pdf")
response.save("reporte_remoto.pdf")
```

---

## 📄 License

MIT © 2026 Edwin Abreu & ReportForge Contributors.
