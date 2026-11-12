import ctypes
import json
import time

class ReportForgeResult(ctypes.Structure):
    _fields_ = [
        ("data", ctypes.POINTER(ctypes.c_uint8)),
        ("length", ctypes.c_size_t),
        ("success", ctypes.c_bool),
        ("error_message", ctypes.c_char_p),
    ]

lib = ctypes.CDLL("./target/release/libreportforge.so")
lib.reportforge_render_pdf.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
lib.reportforge_render_pdf.restype = ReportForgeResult
lib.reportforge_free_result.argtypes = [ReportForgeResult]
lib.reportforge_free_result.restype = None
lib.reportforge_version.argtypes = []
lib.reportforge_version.restype = ctypes.c_char_p

version = lib.reportforge_version().decode("utf-8")
print(f"ReportForge Native Version: {version}")

# Payload AST
doc = {
    "page": { "size": "A4", "orientation": "portrait", "margin": 20 },
    "header": {
        "type": "text",
        "value": "FACTURA COMERCIAL V2 (RUST CORE) #{{ invoice_num }}",
        "style": "h2",
        "alignment": "center",
        "color": "#1E3A8A",
        "bold": True
    },
    "content": [
        {
            "type": "row",
            "spacing": 10,
            "items": [
                {
                    "width": 300,
                    "item": {
                        "type": "column",
                        "spacing": 4,
                        "items": [
                            { "type": "text", "value": "Cliente: {{ customer_name }}", "bold": True },
                            { "type": "text", "value": "RNC / Identificación: {{ customer_tax_id }}" },
                            { "type": "text", "value": "Dirección: Santo Domingo, Rep. Dominicana" }
                        ]
                    }
                },
                {
                    "item": {
                        "type": "column",
                        "spacing": 4,
                        "items": [
                            { "type": "text", "value": "Fecha: {{ date }}", "alignment": "right" },
                            { "type": "text", "value": "Vence: {{ due_date }}", "alignment": "right" },
                            { "type": "text", "value": "Motor: Rust v2.0 (In-Process)", "style": "caption", "alignment": "right" }
                        ]
                    }
                }
            ]
        },
        { "type": "divider", "color": "#CBD5E1", "thickness": 1.0, "margin": 8.0 },
        {
            "type": "table",
            "source": "items",
            "zebra": True,
            "header_background": "#1E3A8A",
            "columns": [
                { "field": "sku", "title": "Código", "width": 80 },
                { "field": "name", "title": "Descripción del Servicio / Producto", "flex": 3.0 },
                { "field": "qty", "title": "Cant.", "width": 50, "format": "number", "align": "center" },
                { "field": "price", "title": "Precio Unit.", "width": 90, "format": "currency", "align": "right" },
                { "field": "total", "title": "Total", "width": 90, "format": "currency", "align": "right" }
            ]
        },
        { "type": "spacer", "height": 10 },
        {
            "type": "row",
            "spacing": 10,
            "items": [
                {
                    "width": 100,
                    "item": { "type": "qr", "value": "https://reportforge.dev/verify/RF-2026-RUST-01", "size": 80 }
                },
                {
                    "item": {
                        "type": "barcode",
                        "value": "RF-2026-RUST-01",
                        "barcode_type": "code128",
                        "width": 180,
                        "height": 40
                    }
                },
                {
                    "item": {
                        "type": "column",
                        "spacing": 4,
                        "items": [
                            { "type": "text", "value": "Subtotal: ${{ subtotal }}", "alignment": "right" },
                            { "type": "text", "value": "ITBIS (18%): ${{ tax }}", "alignment": "right" },
                            { "type": "text", "value": "TOTAL: ${{ grand_total }}", "style": "h2", "color": "#0F766E", "alignment": "right", "bold": True }
                        ]
                    }
                }
            ]
        }
    ],
    "footer": {
        "type": "page_number",
        "format": "Página {page} de {total}",
        "alignment": "right"
    }
}

data = {
    "invoice_num": "INV-2026-RUST-9901",
    "customer_name": "Corporación Dominicana de Innovación",
    "customer_tax_id": "1-31-88992-4",
    "date": "12/11/2026",
    "due_date": "30/11/2026",
    "items": [
        { "sku": "RS-CORE", "name": "Licencia ReportForge v2 Core Rust", "qty": 1, "price": 4500.00, "total": 4500.00 },
        { "sku": "CONS-01", "name": "Consultoría de Arquitectura de Alto Rendimiento", "qty": 10, "price": 180.00, "total": 1800.00 },
        { "sku": "SUPP-ANN", "name": "Soporte Anual Enterprise 24/7", "qty": 1, "price": 1200.00, "total": 1200.00 }
    ],
    "subtotal": "7,500.00",
    "tax": "1,350.00",
    "grand_total": "8,850.00"
}

doc_json = json.dumps(doc).encode("utf-8")
data_json = json.dumps(data).encode("utf-8")

# Benchmarking in microseconds!
t0 = time.perf_counter()
result = lib.reportforge_render_pdf(doc_json, data_json)
t1 = time.perf_counter()

elapsed_ms = (t1 - t0) * 1000

if not result.success:
    err = result.error_message.decode("utf-8") if result.error_message else "Unknown error"
    print(f"Error nativo: {err}")
    exit(1)

# Copiar bytes
buffer_type = ctypes.c_uint8 * result.length
pdf_bytes = bytes(buffer_type.from_address(ctypes.addressof(result.data.contents)))
lib.reportforge_free_result(result)

output_file = "factura_rust_core_v2.pdf"
with open(output_file, "wb") as f:
    f.write(pdf_bytes)

print(f"[✓] ÉXITO: PDF generado por el motor Rust en {elapsed_ms:.2f} ms ({len(pdf_bytes):,} bytes)")
print(f"[✓] Guardado en: {output_file}")
