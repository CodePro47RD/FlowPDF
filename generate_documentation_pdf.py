"""
Script to generate the master documentation PDF for ReportForge.
Covers all printable report types, JSON definitions, and integration code
in Python, C#, JavaScript, TypeScript, PHP, and Java.
"""

import sys
import os

# Ensure repo root is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

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
    Color,
    TextStyle,
    HorizontalAlignment,
    VerticalAlignment,
    EdgeInsets,
)


def code_box(title: str, language: str, code_snippet: str):
    """Render a syntax-styled code block card."""
    style_title = TextStyle(
        font_name="Helvetica-Bold",
        font_size=8.5,
        color=Color.hex("#38BDF8"),  # Sky blue
    )
    style_lang = TextStyle(
        font_name="Helvetica",
        font_size=7.5,
        color=Color.hex("#94A3B8"),
    )
    style_code = TextStyle(
        font_name="Courier",
        font_size=7.2,
        line_height=1.28,
        color=Color.hex("#F8FAFC"),
    )

    header = Row([
        Text(f"● {title}", style=style_title),
        Text(language.upper(), style=style_lang, alignment=HorizontalAlignment.RIGHT),
    ])

    code_lines = Text(code_snippet.strip(), style=style_code)

    return Column([
        header,
        Spacer(4),
        Divider(thickness=0.5, color=Color.hex("#334155"), margin_vertical=2),
        Spacer(4),
        code_lines,
    ]).padding(all=8).background(Color.hex("#0F172A")).border(Color.hex("#1E293B"), 1)


def build_documentation_pdf():
    doc = Document(
        title="ReportForge - Manual de Reportes y Guía Multilenguaje",
        author="ReportForge Software Architecture Team",
        subject="Documentación técnica y catálogo de reportes imprimibles",
    )

    doc.page(size="A4", orientation="portrait", margin=14)

    # Global Page Header
    doc.header(
        Row([
            Text("REPORTFORGE • MANUAL OFICIAL DE REPORTES", style=Typography.CAPTION_BOLD),
            PageNumber(format_str="Página {page} de {total}", alignment=HorizontalAlignment.RIGHT),
        ]),
        spacing=8,
    )

    content_blocks = []

    # =========================================================================
    # PORTADA / TÍTULO PRINCIPAL
    # =========================================================================
    content_blocks.extend([
        Column([
            Text("REPORTFORGE ENTERPRISE", style=Typography.H1.copy_with(color=Colors.PRIMARY_DARK)),
            Spacer(4),
            Text(
                "Catálogo Maestro de Reportes Imprimibles y Guía de Integración Multilenguaje",
                style=Typography.H3.copy_with(color=Colors.GRAY_700),
            ),
            Spacer(6),
            Text(
                "Este manual documenta todos los tipos de reportes que ReportForge puede componer e imprimir: "
                "facturación comercial, finanzas, compras, acreditación académica, analítica ejecutiva "
                "y logística con códigos de barras. Incluye ejemplos de código listos para producción en "
                "C#, JavaScript, TypeScript, PHP, Java y Python.",
                style=Typography.BODY.copy_with(line_height=1.35),
            ),
        ]).padding(all=12).background(Colors.GRAY_100).border(Colors.PRIMARY, 1.5),
        Spacer(14),
    ])

    # =========================================================================
    # SECCIÓN 1: FACTURA COMERCIAL Y COMPROBANTES FISCALES (INVOICES)
    # =========================================================================
    content_blocks.extend([
        Text("1. FACTURA COMERCIAL Y COMPROBANTE FISCAL", style=Typography.H2),
        Spacer(4),
        Text(
            "Propósito: Generación de facturas B2B y B2C, comprobantes de crédito fiscal, recibos de pago y "
            "facturación electrónica con código QR para validación ante autoridades tributarias. "
            "Soporta repetición automática de encabezados en facturas con cientos de ítems.",
            style=Typography.BODY,
        ),
        Spacer(8),

        # Mini preview visual en la documentación
        (
            Row(spacing=10)
            .relative_item(
                2.0,
                Column([
                    Text("EJEMPLO IMPRESO EN VIVO:", style=Typography.CAPTION_BOLD),
                    Spacer(4),
                    Table(
                        columns=[
                            TableColumn("SKU", width=60),
                            TableColumn("Descripción", flex=2),
                            TableColumn("Precio", width=70, alignment=HorizontalAlignment.RIGHT),
                        ],
                        data=[
                            {"SKU": "LIC-01", "Descripción": "Licencia Cloud Pro", "Precio": "$1,200.00"},
                            {"SKU": "SUP-02", "Descripción": "Soporte Técnico 24/7", "Precio": "$450.00"},
                        ],
                        header_background=Colors.PRIMARY,
                        header_text_style=Typography.CAPTION_BOLD.copy_with(color=Colors.WHITE),
                        cell_padding=EdgeInsets.symmetric(vertical=3, horizontal=6),
                    ),
                ])
            )
            .relative_item(
                1.0,
                Column([
                    Text("VERIFICACIÓN QR:", style=Typography.CAPTION_BOLD),
                    Spacer(4),
                    QRCode("https://verify.reportforge.io/inv/FAC-2026-001", size=55),
                ])
            )
        ),

        Spacer(8),
        Text("Ejemplos de Consumo en Cada Lenguaje:", style=Typography.H4),
        Spacer(6),

        code_box(
            "C# (.NET HttpClient) - Generar Factura",
            "csharp",
            """using var client = new HttpClient();
client.DefaultRequestHeaders.Add("X-API-Key", "rf_live_secret_key");
var payload = new {
    document = new {
        page = new { size = "A4", orientation = "portrait" },
        header = new { type = "text", value = "FACTURA #{{ id }}", style = "h2" },
        content = new object[] {
            new { type = "table", source = "items", columns = new[] {
                new { field = "desc", title = "Concepto", flex = 3 },
                new { field = "total", title = "Monto", width = 80, format = "currency", align = "right" }
            }}
        }
    },
    data = new { id = "FAC-1001", items = new[] { new { desc = "Hosting Dedicado", total = 1500.0 } } },
    response_type = "binary"
};
var res = await client.PostAsJsonAsync("http://localhost:8080/api/v1/reports/generate/", payload);
File.WriteAllBytes("factura.pdf", await res.Content.ReadAsByteArrayAsync());"""
        ),
        Spacer(6),

        code_box(
            "JavaScript / Node.js (Fetch API)",
            "javascript",
            """const res = await fetch('http://localhost:8080/api/v1/reports/generate/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-API-Key': 'rf_live_secret_key' },
    body: JSON.stringify({
        template: 'invoice_template',
        data: { customer: 'Acme Corp', total: 4500.0 },
        response_type: 'binary'
    })
});
const pdfBuffer = Buffer.from(await res.arrayBuffer());
fs.writeFileSync('factura.pdf', pdfBuffer);"""
        ),
        Spacer(6),

        code_box(
            "PHP (cURL) - Generar Factura",
            "php",
            """$ch = curl_init('http://localhost:8080/api/v1/reports/generate/');
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'template' => 'invoice_template',
    'data' => ['invoice' => 'FAC-99', 'total' => 3200.0],
    'response_type' => 'binary'
]));
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json', 'X-API-Key: rf_live_key']);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$pdf = curl_exec($ch);
file_put_contents('factura.pdf', $pdf);"""
        ),
        Spacer(14),
    ])

    # =========================================================================
    # SECCIÓN 2: ESTADO DE CUENTA Y REPORTES FINANCIEROS
    # =========================================================================
    content_blocks.extend([
        Text("2. ESTADO DE CUENTA Y REPORTES FINANCIEROS", style=Typography.H2),
        Spacer(4),
        Text(
            "Propósito: Generación de extractos bancarios periódicos, balances contables, libros de mayor y "
            "estados de cuenta de préstamos o tarjetas de crédito. Se caracteriza por tablas extensas con fechas, "
            "conceptos formateados en moneda con alineación a la derecha y balances acumulados.",
            style=Typography.BODY,
        ),
        Spacer(8),

        code_box(
            "TypeScript (Axios)",
            "typescript",
            """import axios from 'axios';
import * as fs from 'fs';

const response = await axios.post('http://localhost:8080/api/v1/reports/generate/', {
    document: {
        page: { size: 'Letter', margin: 15 },
        header: { type: 'text', value: 'ESTADO DE CUENTA - {{ client }}', style: 'h2' },
        content: [
            { type: 'table', source: 'movements', columns: [
                { field: 'date', title: 'Fecha', width: 75, format: 'date' },
                { field: 'desc', title: 'Descripción', flex = 3 },
                { field: 'amount', title: 'Monto', width: 90, format: 'currency', align: 'right' }
            ], zebra: true }
        ]
    },
    data: { client: 'Banco Caribe', movements: [{ date: '2026-11-01', desc: 'Depósito', amount: 50000 }] },
    response_type: 'binary'
}, {
    headers: { 'X-API-Key': 'rf_live_key' },
    responseType: 'arraybuffer'
});
fs.writeFileSync('estado_cuenta.pdf', Buffer.from(response.data));"""
        ),
        Spacer(6),

        code_box(
            "Java 11+ (HttpClient)",
            "java",
            """HttpClient client = HttpClient.newHttpClient();
HttpRequest req = HttpRequest.newBuilder()
    .uri(URI.create("http://localhost:8080/api/v1/reports/generate/"))
    .header("Content-Type", "application/json")
    .header("X-API-Key", "rf_live_secret_key")
    .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
    .build();
HttpResponse<byte[]> res = client.send(req, HttpResponse.BodyHandlers.ofByteArray());
Files.write(Paths.get("estado_cuenta.pdf"), res.body());"""
        ),
        Spacer(14),
    ])

    # =========================================================================
    # SECCIÓN 3: ÓRDENES DE COMPRA Y COTIZACIONES
    # =========================================================================
    content_blocks.extend([
        Text("3. ÓRDENES DE COMPRA Y COTIZACIONES", style=Typography.H2),
        Spacer(4),
        Text(
            "Propósito: Documentación formal para compras empresariales, pedidos a proveedores y cotizaciones "
            "comerciales con plazos de entrega, condiciones contractuales y desglose de materiales.",
            style=Typography.BODY,
        ),
        Spacer(8),

        code_box(
            "Python (ReportForge SDK Oficial)",
            "python",
            """from reportforge_sdk import ReportForgeClient

client = ReportForgeClient(base_url="http://localhost:8080", api_key="rf_live_secret_key")
response = client.generate(
    template="purchase_order",
    data={
        "order_num": "OC-2026-99",
        "vendor": "Equipos Industriales S.A.",
        "items": [
            {"sku": "EQ-01", "desc": "Compresor 500L", "qty": 2, "cost": 3400.0}
        ]
    }
)
response.save("orden_compra.pdf")"""
        ),
        Spacer(14),
    ])

    # =========================================================================
    # SECCIÓN 4: INFORMES ESTADÍSTICOS Y CUADROS DE MANDO EJECUTIVOS
    # =========================================================================
    content_blocks.extend([
        Text("4. INFORMES ESTADÍSTICOS Y GRÁFICOS EJECUTIVOS", style=Typography.H2),
        Spacer(4),
        Text(
            "Propósito: Reportes de alta dirección, métricas trimestrales de desempeño, KPIs y evolución "
            "financiera. ReportForge renderiza gráficos vectoriales nítidos a 200 DPI integrados directamente "
            "en el PDF mediante el componente 'chart'.",
            style=Typography.BODY,
        ),
        Spacer(8),

        # Mini preview visual del gráfico dentro del PDF
        (
            Row(spacing=10)
            .relative_item(
                2.5,
                Column([
                    Text("PREVIEW DE GRÁFICO INTEGRADO EN PDF:", style=Typography.CAPTION_BOLD),
                    Spacer(4),
                    Chart(
                        chart_type="bar",
                        labels=["Ene", "Feb", "Mar", "Abr"],
                        values=[15000, 24000, 31000, 42000],
                        title="Ventas Acumuladas por Mes (USD)",
                        width=320,
                        height=130,
                    ),
                ])
            )
            .relative_item(
                1.0,
                Column([
                    Text("TIPOS DE GRÁFICOS:", style=Typography.CAPTION_BOLD),
                    Spacer(4),
                    Text("• 'bar': Barras estándar", style=Typography.CAPTION),
                    Text("• 'line': Tendencias temporales", style=Typography.CAPTION),
                    Text("• 'pie': Distribución porcentual", style=Typography.CAPTION),
                    Text("• 'area': Volúmenes acumulados", style=Typography.CAPTION),
                ])
            )
        ),

        Spacer(8),

        code_box(
            "Definición JSON del Componente Chart",
            "json",
            """{
  "type": "chart",
  "chart_type": "bar",
  "title": "Ingresos por Trimestre",
  "labels": ["T1", "T2", "T3", "T4"],
  "values": [12000, 18500, 24000, 31000],
  "width": 450,
  "height": 180,
  "colors": ["#1E40AF", "#059669", "#D97706", "#7C3AED"]
}"""
        ),
        Spacer(14),
    ])

    # =========================================================================
    # SECCIÓN 5: LOGÍSTICA, ALMACÉN Y CÓDIGOS DE BARRAS
    # =========================================================================
    content_blocks.extend([
        Text("5. LOGÍSTICA, ALMACÉN Y CÓDIGOS DE BARRAS", style=Typography.H2),
        Spacer(4),
        Text(
            "Propósito: Hojas de empaque (packing slips), etiquetas de despacho para logística, órdenes de picking "
            "y reportes de inventario con códigos de barras 1D (Code 128, EAN-13) escaneables mediante terminales portátiles.",
            style=Typography.BODY,
        ),
        Spacer(8),

        Row([
            Column([
                Text("CÓDIGO DE BARRAS (CODE 128):", style=Typography.CAPTION_BOLD),
                Spacer(4),
                Barcode("PKG-2026-X99", barcode_type="code128", width=160, height=40),
            ]),
            Column([
                Text("CÓDIGO QR DE RASTREO:", style=Typography.CAPTION_BOLD),
                Spacer(4),
                QRCode("https://track.reportforge.io/pkg/PKG-2026-X99", size=60),
            ]),
        ], spacing=20),

        Spacer(8),
        code_box(
            "Definición JSON para Logística (Barcode + QR)",
            "json",
            """[
  { "type": "barcode", "value": "PKG-2026-X99", "barcode_type": "code128", "width": 160, "height": 40 },
  { "type": "qr", "value": "https://track.reportforge.io/pkg/PKG-2026-X99", "size": 60 }
]"""
        ),
        Spacer(14),
    ])

    # =========================================================================
    # SECCIÓN 6: RESUMEN DE ENDPOINTS Y GUÍA DE REFERENCIA RÁPIDA
    # =========================================================================
    content_blocks.extend([
        Text("6. RESUMEN DE LA API REST Y TABLA DE COMPATIBILIDAD", style=Typography.H2),
        Spacer(4),
        Text(
            "ReportForge expone una API REST unificada accesible por cualquier lenguaje mediante HTTP/HTTPS:",
            style=Typography.BODY,
        ),
        Spacer(6),

        Table(
            columns=[
                TableColumn("Método", width=65),
                TableColumn("Endpoint", width=160),
                TableColumn("Descripción", flex=2),
                TableColumn("Retorno", width=75),
            ],
            data=[
                {"Método": "POST", "Endpoint": "/api/v1/reports/generate/", "Descripción": "Generación síncrona o asíncrona (Celery)", "Retorno": "PDF o JSON"},
                {"Método": "POST", "Endpoint": "/api/v1/reports/preview/", "Descripción": "Previsualización instantánea en memoria", "Retorno": "PDF binario"},
                {"Método": "GET", "Endpoint": "/api/v1/reports/{id}/", "Descripción": "Consulta de estado y métricas del reporte", "Retorno": "JSON"},
                {"Método": "GET", "Endpoint": "/api/v1/reports/{id}/download/", "Descripción": "Descarga del PDF generado", "Retorno": "PDF Stream"},
                {"Método": "GET/POST", "Endpoint": "/api/v1/templates/", "Descripción": "CRUD de plantillas reusables aisladas por tenant", "Retorno": "JSON"},
                {"Método": "GET", "Endpoint": "/api/docs/", "Descripción": "Interfaz interactiva Swagger / OpenAPI 3", "Retorno": "HTML / UI"},
            ],
            header_background=Colors.PRIMARY_DARK,
            header_text_style=Typography.CAPTION_BOLD.copy_with(color=Colors.WHITE),
            zebra_color=Colors.BG_ZEBRA,
            cell_padding=EdgeInsets.symmetric(vertical=4, horizontal=6),
            border_width=0.5,
        ),
        Spacer(14),
        Column([
            Text("CONCLUSIÓN Y RECOMENDACIÓN DE ARQUITECTURA", style=Typography.H3),
            Spacer(4),
            Text(
                "Para microservicios de alto tráfico se recomienda utilizar el modo asíncrono "
                "('async_mode': true), permitiendo que la cola de Celery distribuya la carga sobre los workers "
                "de composición sin bloquear las conexiones HTTP de la aplicación cliente.",
                style=Typography.BODY,
            ),
        ]).padding(all=10).background(Colors.GRAY_100).border(Colors.GRAY_300, 1),
    ])

    doc.content(Column(content_blocks, spacing=0))

    # Global Footer
    doc.footer(
        Text("ReportForge • Motor Universal de Documentos • https://github.com/reportforge/reportforge", style=Typography.CAPTION)
        .align_center(),
        spacing=6,
    )

    return doc


if __name__ == "__main__":
    print("Iniciando composición de la documentación maestra en PDF...")
    doc = build_documentation_pdf()
    output_pdf = "documentacion_reportes_reportforge.pdf"
    doc.generate(output_pdf)
    size_bytes = os.path.getsize(output_pdf)
    print(f"Documentación PDF generada exitosamente:")
    print(f"-> Archivo: {os.path.abspath(output_pdf)}")
    print(f"-> Tamaño: {size_bytes:,} bytes")
