"""
Example: Generating a rich business document using the ReportForge fluent Python API.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from engine import (
    Document,
    Text,
    Column,
    Row,
    Table,
    TableColumn,
    Chart,
    QRCode,
    Barcode,
    Spacer,
    Divider,
    PageNumber,
    Typography,
    Colors,
    HorizontalAlignment,
    mm,
)

def create_sales_invoice():
    doc = Document(
        title="Factura Comercial INV-2026-089",
        author="ReportForge Engine",
        subject="Factura de Venta y Servicios",
    )

    # 1. Page Configuration
    doc.page(size="A4", orientation="portrait", margin=15)

    # 2. Header
    doc.header(
        Row([
            Text("REPORTFORGE ENTERPRISE", style=Typography.H3),
            PageNumber(format_str="Página {page} de {total}", alignment=HorizontalAlignment.RIGHT),
        ])
    )

    # 3. Content Body
    sales_data = [
        {"item": "LIC-ENT-01", "desc": "Licencia ReportForge Enterprise Anual", "qty": "1", "price": "$12,500.00"},
        {"item": "SRV-DEP-02", "desc": "Servicio de Implementación en Clúster Kubernetes", "qty": "1", "price": "$3,500.00"},
        {"item": "SUP-247-03", "desc": "Soporte Técnico Especializado 24/7 (12 meses)", "qty": "1", "price": "$2,400.00"},
        {"item": "TRN-DEV-04", "desc": "Capacitación a Ingenieros Backend en Composición PDF", "qty": "2", "price": "$1,800.00"},
    ]

    doc.content(
        Column([
            # Title & Metadata
            Row([
                Column([
                    Text("FACTURA COMERCIAL", style=Typography.H1),
                    Text("Comprobante Fiscal B0100004523", style=Typography.BODY_MUTED),
                ]),
                Column([
                    Text("Fecha: 12/11/2026", style=Typography.BODY_BOLD, alignment=HorizontalAlignment.RIGHT),
                    Text("Vence: 12/12/2026", style=Typography.BODY_MUTED, alignment=HorizontalAlignment.RIGHT),
                    Text("Estado: PAGADA", style=Typography.BODY_BOLD, alignment=HorizontalAlignment.RIGHT),
                ]),
            ]),

            Spacer(12),
            Divider(thickness=1.5, color=Colors.PRIMARY),
            Spacer(12),

            # Customer & Company Details
            Row([
                Column([
                    Text("EMISOR:", style=Typography.CAPTION_BOLD),
                    Text("ReportForge Technologies Inc.", style=Typography.BODY_BOLD),
                    Text("Av. Central #100, Torre Empresarial", style=Typography.BODY),
                    Text("RNC: 101-98765-4 • contacto@reportforge.io", style=Typography.BODY_MUTED),
                ]).padding(all=10).background(Colors.GRAY_100).border(Colors.GRAY_300, 1),

                Column([
                    Text("CLIENTE:", style=Typography.CAPTION_BOLD),
                    Text("Corporación Financiera del Caribe", style=Typography.BODY_BOLD),
                    Text("Calle Principal #45, Santo Domingo", style=Typography.BODY),
                    Text("RNC: 130-12345-6 • finanzas@cfc.com.do", style=Typography.BODY_MUTED),
                ]).padding(all=10).background(Colors.GRAY_100).border(Colors.GRAY_300, 1),
            ], spacing=15),

            Spacer(18),
            Text("Detalle de Servicios y Productos", style=Typography.H3),
            Spacer(8),

            # Items Table
            Table(
                columns=[
                    TableColumn("item", width=80),
                    TableColumn("desc", flex=3),
                    TableColumn("qty", width=50, alignment=HorizontalAlignment.CENTER),
                    TableColumn("price", width=90, alignment=HorizontalAlignment.RIGHT),
                ],
                data=sales_data,
                header_background=Colors.PRIMARY,
                header_text_style=Typography.BODY_BOLD.copy_with(color=Colors.WHITE),
                zebra_color=Colors.BG_ZEBRA,
                border_color=Colors.BORDER_LIGHT,
                border_width=0.75,
            ),

            Spacer(15),

            # Summary and Verification QR / Barcode
            Row([
                Column([
                    Text("Verificación Electrónica:", style=Typography.CAPTION_BOLD),
                    Spacer(6),
                    QRCode("https://verify.reportforge.io/inv/INV-2026-089", size=75),
                    Spacer(6),
                    Barcode("INV2026089", barcode_type="code128", width=140, height=35),
                ]),

                Column([
                    Row([
                        Text("Subtotal:", style=Typography.BODY),
                        Text("$20,200.00", style=Typography.BODY, alignment=HorizontalAlignment.RIGHT),
                    ]),
                    Row([
                        Text("ITBIS / IVA (18%):", style=Typography.BODY),
                        Text("$3,636.00", style=Typography.BODY, alignment=HorizontalAlignment.RIGHT),
                    ]),
                    Divider(thickness=1, color=Colors.GRAY_300, margin_vertical=4),
                    Row([
                        Text("TOTAL A PAGAR:", style=Typography.H3),
                        Text("$23,836.00", style=Typography.H3, alignment=HorizontalAlignment.RIGHT),
                    ]),
                ]).padding(all=12).background(Colors.GRAY_50).border(Colors.PRIMARY, 1),
            ], spacing=20),

            Spacer(20),
            Text("Distribución Trimestral de Consumo", style=Typography.H3),
            Spacer(8),

            # Quarterly Chart
            Chart(
                chart_type="bar",
                labels=["T1", "T2", "T3", "T4 (Proy.)"],
                values=[4500, 7200, 12500, 20200],
                title="Consumo de Reportes por Trimestre (USD)",
                width=450,
                height=150,
            ),
        ])
    )

    # 4. Footer
    doc.footer(
        Text("Documento emitido electrónicamente por ReportForge Engine • www.reportforge.io", style=Typography.CAPTION)
        .align_center()
    )

    return doc


if __name__ == "__main__":
    doc = create_sales_invoice()
    output_path = "factura_reportforge.pdf"
    doc.generate(output_path)
    print(f"Factura generada exitosamente en: {output_path}")
