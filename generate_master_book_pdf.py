"""
Master Documentation PDF Generator for ReportForge.
Creates an exhaustive, multi-chapter technical manual covering:
1. Complete Architecture & Declarative Composition Mathematics.
2. Component Catalog with Full Property Specifications.
3. 8 Production-grade Report Types with Real Visual Previews.
4. Production Code in 6 Languages (C#, JavaScript, TypeScript, PHP, Java, Python).
5. Declarative JSON Schema Spec v1.0 with Security & Formatters.
6. REST API Reference & Multi-Tenancy Architecture.
7. Enterprise Deployment (Docker, Celery, Redis, Nginx, PostgreSQL, S3).
8. Troubleshooting & Performance Engineering.
"""

import sys
import os

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


def chapter_banner(number: str, title: str, subtitle: str):
    """Render a prominent chapter title banner."""
    return Column([
        Row([
            Text(f"CAPÍTULO {number}", style=TextStyle(font_name="Helvetica-Bold", font_size=10, color=Colors.PRIMARY_LIGHT)),
            Text("REPORTFORGE ENTERPRISE MANUAL", style=TextStyle(font_name="Helvetica", font_size=8, color=Colors.TEXT_MUTED), alignment=HorizontalAlignment.RIGHT),
        ]),
        Spacer(4),
        Text(title, style=Typography.H1.copy_with(color=Colors.PRIMARY_DARK)),
        Spacer(4),
        Text(subtitle, style=Typography.BODY_MUTED.copy_with(font_size=9.5)),
        Spacer(6),
        Divider(thickness=2.0, color=Colors.PRIMARY, margin_vertical=2),
    ]).padding(all=10).background(Colors.GRAY_100).border(Colors.GRAY_300, 1)


def section_title(title: str):
    return Column([
        Spacer(10),
        Text(title, style=Typography.H2.copy_with(color=Colors.PRIMARY_DARK)),
        Spacer(4),
        Divider(thickness=1.0, color=Colors.PRIMARY_LIGHT, margin_vertical=2),
        Spacer(6),
    ])


def callout_box(title: str, text: str, alert_type: str = "NOTE"):
    color_map = {
        "NOTE": (Colors.PRIMARY, Color.hex("#EFF6FF")),
        "TIP": (Colors.SUCCESS, Color.hex("#ECFDF5")),
        "WARNING": (Colors.WARNING, Color.hex("#FFFBEB")),
        "IMPORTANT": (Colors.DANGER, Color.hex("#FEF2F2")),
    }
    border_col, bg_col = color_map.get(alert_type, (Colors.PRIMARY, Color.hex("#EFF6FF")))

    return Column([
        Row([
            Text(f"[{alert_type}] {title}", style=TextStyle(font_name="Helvetica-Bold", font_size=9.0, color=border_col)),
        ]),
        Spacer(3),
        Text(text, style=TextStyle(font_name="Helvetica", font_size=8.5, line_height=1.35, color=Colors.GRAY_800)),
    ]).padding(all=8).background(bg_col).border(border_col, 1.2)


def code_box(title: str, language: str, code_snippet: str):
    """Render a syntax-styled dark theme code block."""
    style_title = TextStyle(font_name="Helvetica-Bold", font_size=8.0, color=Color.hex("#38BDF8"))
    style_lang = TextStyle(font_name="Helvetica", font_size=7.5, color=Color.hex("#94A3B8"))
    style_code = TextStyle(font_name="Courier", font_size=6.8, line_height=1.26, color=Color.hex("#F8FAFC"))

    header = Row([
        Text(f"● {title}", style=style_title),
        Text(language.upper(), style=style_lang, alignment=HorizontalAlignment.RIGHT),
    ])

    code_lines = Text(code_snippet.strip(), style=style_code)

    return Column([
        header,
        Spacer(3),
        Divider(thickness=0.5, color=Color.hex("#334155"), margin_vertical=2),
        Spacer(3),
        code_lines,
    ]).padding(all=7).background(Color.hex("#0F172A")).border(Color.hex("#1E293B"), 1)


def build_exhaustive_book():
    doc = Document(
        title="ReportForge - Manual Técnico Definitivo y Catálogo de Reportes",
        author="ReportForge Software Architecture Team",
        subject="Manual exhaustivo de composición de documentos PDF, plantillas JSON y SDKs",
    )

    doc.page(size="A4", orientation="portrait", margin=14)

    # Repeating Header on every page
    doc.header(
        Row([
            Text("REPORTFORGE ENTERPRISE • MANUAL TÉCNICO OFICIAL", style=Typography.CAPTION_BOLD),
            PageNumber(format_str="Página {page} de {total}", alignment=HorizontalAlignment.RIGHT),
        ]),
        spacing=6,
    )

    blocks = []

    # =========================================================================
    # PORTADA DE ALTA CALIDAD
    # =========================================================================
    blocks.extend([
        Column([
            Text("REPORTFORGE", style=TextStyle(font_name="Helvetica-Bold", font_size=32, color=Colors.PRIMARY_DARK)),
            Spacer(4),
            Text(
                "Motor Universal de Composición y Generación de Reportes",
                style=Typography.H2.copy_with(color=Colors.GRAY_700),
            ),
            Spacer(6),
            Text(
                "Manual Técnico de Arquitectura, Catálogo Maestro de Documentos Empresariales, "
                "Especificación del Esquema Declarativo JSON v1.0 y Guía de Integración para "
                "C#, JavaScript, TypeScript, PHP, Java y Python.",
                style=Typography.BODY.copy_with(line_height=1.35),
            ),
            Spacer(10),
            Divider(thickness=1.5, color=Colors.PRIMARY, margin_vertical=2),
            Spacer(8),
            Row([
                Column([
                    Text("INFORMACIÓN DE PUBLICACIÓN:", style=Typography.CAPTION_BOLD),
                    Text("• Versión del Motor: 1.0.0 Enterprise", style=Typography.CAPTION),
                    Text("• Arquitectura: Microservicio Desacoplado", style=Typography.CAPTION),
                    Text("• Motor de Dibujo: ReportLab + Canvas Top-Down", style=Typography.CAPTION),
                ]),
                Column([
                    Text("COMPATIBILIDAD CLIENTE:", style=Typography.CAPTION_BOLD),
                    Text("• HTTP REST API v1 (Universal)", style=Typography.CAPTION),
                    Text("• SDK Nativo: Python (requests)", style=Typography.CAPTION),
                    Text("• Licencia: MIT Open Enterprise", style=Typography.CAPTION),
                ]),
            ], spacing=20),
        ]).padding(all=16).background(Colors.GRAY_100).border(Colors.PRIMARY, 2),
        Spacer(14),

        callout_box(
            "Finalidad de este Manual",
            "Este documento sirve como especificación formal y catálogo exhaustivo de los tipos de reportes "
            "que pueden generarse con ReportForge. Ha sido producido directamente por el motor de ReportForge "
            "demostrando sus capacidades de medición de cajas, división multipágina, tablas cebra, códigos de barras, "
            "códigos QR y gráficos estadísticos de alta resolución.",
            "NOTE",
        ),
        Spacer(12),

        # ÍNDICE GENERAL / TABLA DE CONTENIDOS
        Column([
            Text("ÍNDICE GENERAL Y CONTENIDO DEL MANUAL", style=Typography.H2.copy_with(color=Colors.PRIMARY_DARK)),
            Spacer(4),
            Divider(thickness=1.5, color=Colors.PRIMARY, margin_vertical=2),
            Spacer(6),
            Table(
                columns=[
                    TableColumn("Capítulo / Módulo", flex=2),
                    TableColumn("Descripción y Contenido Clave", flex=3),
                ],
                data=[
                    {"Capítulo / Módulo": "Capítulo 1: Arquitectura y Motor Matemático", "Descripción y Contenido Clave": "Filosofía declarativa en Python, BoxConstraints, coordenadas Top-Down y algoritmo de dos pasadas."},
                    {"Capítulo / Módulo": "Capítulo 2: Catálogo Técnico de Componentes", "Descripción y Contenido Clave": "Especificación de Text, Container, Column, Row, Table, Chart (200 DPI), QRCode y Barcode."},
                    {"Capítulo / Módulo": "Capítulo 3: Catálogo de Reportes y Multilenguaje", "Descripción y Contenido Clave": "9 Reportes: Facturas, Bancos, Nómina, Clínicos, Compras, Diplomas, Logística, Vales y Pasajes."},
                    {"Capítulo / Módulo": "Capítulo 4: Especificación de Plantillas JSON v1.0", "Descripción y Contenido Clave": "Esquema AST en Pydantic, seguridad (cero eval) y formateadores (currency, number, date)."},
                    {"Capítulo / Módulo": "Capítulo 5: API REST y Multi-Tenancy", "Descripción y Contenido Clave": "Autenticación por API Key (rf_live_...), aislamiento por inquilino y colas Celery + Redis."},
                    {"Capítulo / Módulo": "Capítulo 6: Infraestructura de Producción", "Descripción y Contenido Clave": "Docker Compose, Nginx Reverse Proxy, Postgres 16, Redis, Almacenamiento S3 y Troubleshooting."},
                    {"Capítulo / Módulo": "Capítulo 7: SDK Python y Automatización", "Descripción y Contenido Clave": "Cliente oficial, generación asíncrona con polling inteligente y registro dinámico de plantillas."},
                ],
                header_background=Colors.PRIMARY,
                header_text_style=Typography.CAPTION_BOLD.copy_with(color=Colors.WHITE),
                zebra_color=Colors.BG_ZEBRA,
                cell_padding=EdgeInsets.symmetric(vertical=4, horizontal=6),
                border_width=0.5,
            ),
        ]),
        Spacer(16),
    ])

    # =========================================================================
    # CAPÍTULO 1: ARQUITECTURA Y MODELO MATEMÁTICO DE COMPOSICIÓN
    # =========================================================================
    blocks.extend([
        chapter_banner("1", "ARQUITECTURA Y MOTOR MATEMÁTICO", "Separación de responsabilidades, BoxConstraints y coordenadas"),
        Spacer(10),

        section_title("1.1 Filosofía de Composición Declarativa"),
        Text(
            "ReportForge surge como respuesta a las limitaciones críticas de los motores basados en navegadores web (Chromium/Puppeteer): "
            "la incertidumbre de los saltos de página, el desbordamiento de celdas en tablas y el enorme consumo de memoria RAM. "
            "Con una filosofía declarativa,ReportForge implementa un motor nativo en Python donde cada documento "
            "es un árbol jerárquico de componentes medibles matemáticamente antes de ser trazados sobre el PDF.",
            style=Typography.BODY,
        ),
        Spacer(8),

        section_title("1.2 El Algoritmo de Medición y Restricciones (BoxConstraints)"),
        Text(
            "Cada nodo del documento implementa la interfaz base Component:\n\n"
            "• measure(constraints: BoxConstraints, context: LayoutContext) -> Size: Calcula el ancho y alto necesarios "
            "dentro de las restricciones mínimas y máximas impuestas por el contenedor padre.\n\n"
            "• draw(rect: Rect, context: DrawContext) -> None: Dibuja los elementos vectoriales en las coordenadas asignadas.\n\n"
            "• split(available_height: float, context: LayoutContext) -> (fitted, remaining): Permite a componentes como Column "
            "y Table cortarse limpiamente cuando el contenido excede el espacio de la página.",
            style=Typography.BODY,
        ),
        Spacer(8),

        section_title("1.3 Normalización de Coordenadas Top-Down"),
        Text(
            "ReportLab trabaja nativamente con un plano cartesiano con origen inferior izquierdo (y=0 en el fondo). "
            "ReportForge implementa DrawContext, que traduce de forma transparente y determinista todas las operaciones al "
            "estándar Top-Left (y=0 arriba, creciendo hacia abajo):\n"
            "canvas_y = page_height - y - height\n"
            "Esto simplifica el cálculo de márgenes, encabezados y flujo natural del texto.",
            style=Typography.BODY,
        ),
        Spacer(8),

        section_title("1.4 Algoritmo de Paginación en Dos Pasadas"),
        Text(
            "El paginador (Paginator) calcula el presupuesto exacto disponible para el cuerpo del documento restando la altura real "
            "del encabezado y del pie de página. Durante la primera pasada, se determina la cantidad total de páginas requeridas (total_pages). "
            "En la segunda pasada de renderizado, el componente PageNumber tiene acceso inmediato al número total de páginas "
            "permitiendo imprimir 'Página X de Y' con 100% de exactitud y sin aproximaciones.",
            style=Typography.BODY,
        ),
        Spacer(14),
    ])

    # =========================================================================
    # CAPÍTULO 2: CATÁLOGO DE COMPONENTES DEL MOTOR
    # =========================================================================
    blocks.extend([
        chapter_banner("2", "CATÁLOGO TÉCNICO DE COMPONENTES", "Especificaciones completas de propiedades y modificadores fluidos"),
        Spacer(10),

        section_title("2.1 Text & TextSpan (Tipografía y Envoltura)"),
        Text(
            "Text permite renderizar cadenas de texto o spans enriquecidos. Utiliza pdfmetrics.stringWidth para medir la longitud "
            "de las palabras y dividirlas en líneas sin cortar vocablos. Soporta alineación (left, center, right, justify) y decoraciones "
            "como subrayado y tachado.",
            style=Typography.BODY,
        ),
        Spacer(6),
        Table(
            columns=[
                TableColumn("Propiedad", width=80),
                TableColumn("Tipo", width=80),
                TableColumn("Descripción", flex=2),
                TableColumn("Valor por Defecto", width=90),
            ],
            data=[
                {"Propiedad": "style", "Tipo": "TextStyle", "Descripción": "Presets: H1..H4, BODY, CAPTION, CODE", "Valor por Defecto": "Typography.BODY"},
                {"Propiedad": "alignment", "Tipo": "HorizontalAlignment", "Descripción": "Alineación horizontal del párrafo", "Valor por Defecto": "'left'"},
                {"Propiedad": "bold / italic", "Tipo": "bool", "Descripción": "Modificadores de peso y cursiva", "Valor por Defecto": "False"},
                {"Propiedad": "underline / strike", "Tipo": "bool", "Descripción": "Líneas decorativas trazadas en el canvas", "Valor por Defecto": "False"},
                {"Propiedad": "max_lines", "Tipo": "int | None", "Descripción": "Límite superior de renglones a renderizar", "Valor por Defecto": "None (sin límite)"},
            ],
            header_background=Colors.PRIMARY,
            header_text_style=Typography.CAPTION_BOLD.copy_with(color=Colors.WHITE),
            zebra_color=Colors.BG_ZEBRA,
            cell_padding=EdgeInsets.symmetric(vertical=3, horizontal=6),
        ),
        Spacer(10),

        section_title("2.2 Container (Modelo de Cajas)"),
        Text(
            "Container actúa como la base de estilizado de ReportForge. Implementa márgenes exteriores, rellenos interiores (padding), "
            "bordes con radio de curvatura (border_radius), color de fondo y alineación interna del elemento hijo.",
            style=Typography.BODY,
        ),
        Spacer(6),
        code_box(
            "Ejemplo de uso de Container en Python",
            "python",
            """Text("Panel Corporativo")
    .padding(all=12)
    .background("#F8FAFC")
    .border(color="#E2E8F0", width=1.0, radius=4.0)
    .align_center()"""
        ),
        Spacer(10),

        section_title("2.3 Column & Row (Distribución Espacial)"),
        Text(
            "• Column: Apila componentes verticalmente con espaciado uniforme (spacing). Implementa split() para fluir entre páginas.\n"
            "• Row: Distribuye elementos horizontalmente con pesos flexibles proporcionales (.relative_item(flex, comp)) o anchos fijos (.constant_item(width, comp)).",
            style=Typography.BODY,
        ),
        Spacer(10),

        section_title("2.4 Table (Tablas Corporativas de Alto Rendimiento)"),
        Text(
            "El componente Table resuelve uno de los mayores dolores de cabeza en generación de documentos: la división de tablas "
            "multipágina con repetición automática de encabezados. Cada fila se mide en base a sus columnas y se distribuye "
            "sin desbordar la página.",
            style=Typography.BODY,
        ),
        Spacer(10),

        section_title("2.5 Chart (Gráficos Estadísticos a 200 DPI)"),
        Text(
            "Genera gráficos de alta resolución integrados de forma nativa en el PDF. Utiliza un backend headless de Matplotlib (Agg) "
            "que no requiere entorno de ventanas ni dependencias de interfaz gráfica.",
            style=Typography.BODY,
        ),
        Spacer(6),

        (
            Row(spacing=10)
            .relative_item(
                2.5,
                Column([
                    Text("DEMOSTRACIÓN DE GRÁFICO VECTORIAL:", style=Typography.CAPTION_BOLD),
                    Spacer(4),
                    Chart(
                        chart_type="bar",
                        labels=["2023", "2024", "2025", "2026"],
                        values=[4800, 7900, 14200, 23500],
                        title="Documentos Procesados por Año (Miles)",
                        width=320,
                        height=130,
                    ),
                ])
            )
            .relative_item(
                1.0,
                Column([
                    Text("ESPECIFICACIONES:", style=Typography.CAPTION_BOLD),
                    Spacer(4),
                    Text("• DPI: 200 (Impresión nítida)", style=Typography.CAPTION),
                    Text("• Formatos: Barras, Línea, Pie", style=Typography.CAPTION),
                    Text("• Paleta: Hexadecimal configurable", style=Typography.CAPTION),
                    Text("• Títulos y leyendas automáticas", style=Typography.CAPTION),
                ])
            )
        ),
        Spacer(10),

        section_title("2.6 QRCode y Barcode (Identificación y Trazabilidad)"),
        Text(
            "Permite incluir códigos QR bidimensionales para comprobantes fiscales y URLs de verificación, así como códigos de "
            "barras lineales 1D (Code 128, EAN-13, EAN-8) para logística e inventario.",
            style=Typography.BODY,
        ),
        Spacer(6),
        Row([
            Column([
                Text("QR CODE BIDIMENSIONAL:", style=Typography.CAPTION_BOLD),
                Spacer(4),
                QRCode("https://reportforge.io/docs/manual", size=65),
            ]),
            Column([
                Text("CÓDIGO DE BARRAS LINEAL (CODE 128):", style=Typography.CAPTION_BOLD),
                Spacer(4),
                Barcode("DOC-RF-2026", barcode_type="code128", width=180, height=45),
            ]),
        ], spacing=20),
        Spacer(14),
    ])

    # =========================================================================
    # CAPÍTULO 3: CATÁLOGO DE REPORTES Y EJEMPLOS MULTILENGUAJE
    # =========================================================================
    blocks.extend([
        chapter_banner("3", "CATÁLOGO DE REPORTES Y EJEMPLOS MULTILENGUAJE", "Implementaciones exhaustivas para cada sector empresarial"),
        Spacer(10),

        # ---------------------------------------------------------------------
        # REPORTE 1: FACTURA COMERCIAL
        # ---------------------------------------------------------------------
        section_title("3.1 Factura Comercial y Comprobantes Fiscales (Invoices)"),
        Text(
            "Utilizada en sistemas de facturación electrónica, ERPs y plataformas de e-commerce. "
            "Incluye información del emisor, receptor, desglose impositivo y código QR tributario.",
            style=Typography.BODY,
        ),
        Spacer(6),

        (
            Row(spacing=10)
            .relative_item(
                2.0,
                Column([
                    Text("EJEMPLO DE FACTURA EN VIVO:", style=Typography.CAPTION_BOLD),
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

        code_box(
            "C# (.NET 8+) - Generación de Factura Comercial",
            "csharp",
            """using System.IO;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;

using var client = new HttpClient();
client.DefaultRequestHeaders.Add("X-API-Key", "rf_live_secret_key");

var payload = new {
    document = new {
        page = new { size = "A4", orientation = "portrait", margin = 15 },
        header = new { type = "text", value = "FACTURA #{{ id }}", style = "h2" },
        content = new object[] {
            new { type = "text", value = "Cliente: {{ customer }} | Fecha: {{ date }}" },
            new { type = "spacer", height = 10 },
            new {
                type = "table",
                source = "items",
                columns = new[] {
                    new { field = "sku", title = "SKU", width = 80 },
                    new { field = "desc", title = "Concepto", flex = 3 },
                    new { field = "total", title = "Monto", width = 90, format = "currency", align = "right" }
                },
                header_background = "#1E40AF",
                zebra = true
            },
            new { type = "qr", value = "https://verify.tax.gov/inv/{{ id }}", size = 70 }
        },
        footer = new { type = "page_number", format = "Página {page} de {total}", alignment = "right" }
    },
    data = new {
        id = "FAC-2026-001",
        customer = "Corporación Alfa S.A.",
        date = "2026-11-12",
        items = new[] {
            new { sku = "SRV-01", desc = "Consultoría Arquitectura Cloud", total = 3500.00 },
            new { sku = "LIC-02", desc = "Licencia ReportForge Enterprise", total = 12500.00 }
        }
    },
    response_type = "binary"
};

var response = await client.PostAsJsonAsync("http://localhost:8080/api/v1/reports/generate/", payload);
byte[] pdfBytes = await response.Content.ReadAsByteArrayAsync();
await File.WriteAllBytesAsync("factura_comercial.pdf", pdfBytes);"""
        ),
        Spacer(6),

        code_box(
            "JavaScript / Node.js - Generación de Factura Comercial",
            "javascript",
            """const fs = require('fs');

async function exportInvoice() {
    const res = await fetch('http://localhost:8080/api/v1/reports/generate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-API-Key': 'rf_live_secret_key' },
        body: JSON.stringify({
            template: 'invoice_template',
            data: { id: 'FAC-2026-001', customer: 'Acme Corp', total: 16000.0 },
            response_type: 'binary'
        })
    });
    const buffer = Buffer.from(await res.arrayBuffer());
    fs.writeFileSync('factura_node.pdf', buffer);
}
exportInvoice();"""
        ),
        Spacer(12),

        # ---------------------------------------------------------------------
        # REPORTE 2: ESTADO DE CUENTA BANCARIO
        # ---------------------------------------------------------------------
        section_title("3.2 Estado de Cuenta Bancario y Extractos Financieros"),
        Text(
            "Documento esencial para entidades financieras, cooperativas y bancos. Se compone de transacciones "
            "cronológicas con formato de fecha, descripción de la operación y valores en débito/crédito.",
            style=Typography.BODY,
        ),
        Spacer(6),

        code_box(
            "TypeScript (Axios) - Estado de Cuenta Bancario",
            "typescript",
            """import axios, { AxiosResponse } from 'axios';
import * as fs from 'fs';

interface AccountMovement {
    date: string;
    concept: string;
    amount: number;
}

const movements: AccountMovement[] = [
    { date: '2026-11-01', concept: 'Depósito en Efectivo', amount: 450000.00 },
    { date: '2026-11-05', concept: 'Transferencia ACH a Proveedor', amount: -128000.00 },
    { date: '2026-11-10', concept: 'Cobro de Factura Electrónica', amount: 89000.00 }
];

const res: AxiosResponse<ArrayBuffer> = await axios.post(
    'http://localhost:8080/api/v1/reports/generate/',
    {
        document: {
            page: { size: 'Letter', orientation: 'portrait', margin: 15 },
            header: { type: 'text', value: 'ESTADO DE CUENTA - {{ client }}', style: 'h2' },
            content: [
                { type: 'text', value: 'Cuenta No: {{ account }} | Moneda: DOP', style: 'body' },
                { type: 'spacer', height: 10 },
                {
                    type: 'table',
                    source: 'items',
                    columns: [
                        { field: 'date', title: 'Fecha', width: 75, format: 'date' },
                        { field: 'concept', title: 'Concepto', flex: 3 },
                        { field: 'amount', title: 'Monto', width: 95, format: 'currency', align: 'right' }
                    ],
                    zebra: true
                }
            ],
            footer: { type: 'page_number', format: 'Página {page} de {total}', alignment: 'right' }
        },
        data: { client: 'Grupo Ramos', account: '980-00123-1', items: movements },
        response_type: 'binary'
    },
    {
        headers: { 'Content-Type': 'application/json', 'X-API-Key': 'rf_live_secret_key' },
        responseType: 'arraybuffer'
    }
);

fs.writeFileSync('estado_cuenta.pdf', Buffer.from(res.data));"""
        ),
        Spacer(6),

        code_box(
            "Java 17+ (HttpClient) - Estado de Cuenta Bancario",
            "java",
            """import java.io.IOException;
import java.net.URI;
import java.net.http.*;
import java.nio.file.*;

public class AccountStatementClient {
    public static void main(String[] args) throws IOException, InterruptedException {
        HttpClient client = HttpClient.newHttpClient();
        String jsonPayload = \"\"\"
        {
          "document": {
            "page": { "size": "A4", "orientation": "portrait", "margin": 15 },
            "header": { "type": "text", "value": "EXTRACTO DE CUENTA BANCARIA", "style": "h2" },
            "content": [
              { "type": "text", "value": "Titular: {{ holder }}", "style": "body" },
              { "type": "spacer", "height": 10 },
              {
                "type": "table",
                "source": "txs",
                "columns": [
                  { "field": "date", "title": "Fecha", "width": 80 },
                  { "field": "desc", "title": "Operación", "flex": 2 },
                  { "field": "val", "title": "Importe", "width": 90, "format": "currency", "align": "right" }
                ],
                "zebra": true
              }
            ],
            "footer": { "type": "page_number", "format": "Página {page} de {total}", "alignment": "right" }
          },
          "data": {
            "holder": "Inversiones Caribe S.A.",
            "txs": [
              { "date": "2026-11-01", "desc": "Nómina Quincenal", "val": -850000.0 },
              { "date": "2026-11-04", "desc": "Ingreso por Servicios", "val": 1250000.0 }
            ]
          },
          "format": "pdf",
          "response_type": "binary"
        }
        \"\"\";

        HttpRequest req = HttpRequest.newBuilder()
            .uri(URI.create("http://localhost:8080/api/v1/reports/generate/"))
            .header("Content-Type", "application/json")
            .header("X-API-Key", "rf_live_secret_key")
            .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
            .build();

        HttpResponse<byte[]> res = client.send(req, HttpResponse.BodyHandlers.ofByteArray());
        Files.write(Paths.get("estado_cuenta_java.pdf"), res.body());
    }
}"""
        ),
        Spacer(12),

        # ---------------------------------------------------------------------
        # REPORTE 3: RECIBO DE NÓMINA (PAY SLIP)
        # ---------------------------------------------------------------------
        section_title("3.3 Recibo de Nómina y Pago Salarial (Pay Slip)"),
        Text(
            "Comprobante salarial emitido por departamentos de Recursos Humanos. Detalla los ingresos brutos, "
            "horas extras, comisiones, así como las retenciones legales de seguridad social, pensiones e impuestos.",
            style=Typography.BODY,
        ),
        Spacer(6),

        Row([
            Column([
                Text("PERCEPCIONES (INGRESOS):", style=Typography.CAPTION_BOLD),
                Spacer(4),
                Table(
                    columns=[
                        TableColumn("Concepto", flex=2),
                        TableColumn("Monto", width=70, alignment=HorizontalAlignment.RIGHT),
                    ],
                    data=[
                        {"Concepto": "Sueldo Base Mensual", "Monto": "$85,000.00"},
                        {"Concepto": "Horas Extras (10 hrs)", "Monto": "$7,500.00"},
                        {"Concepto": "Bonificación por Desempeño", "Monto": "$12,000.00"},
                    ],
                    header_background=Colors.PRIMARY,
                    header_text_style=Typography.CAPTION_BOLD.copy_with(color=Colors.WHITE),
                    cell_padding=EdgeInsets.symmetric(vertical=3, horizontal=6),
                ),
            ]),
            Column([
                Text("DEDUCCIONES LEGALES:", style=Typography.CAPTION_BOLD),
                Spacer(4),
                Table(
                    columns=[
                        TableColumn("Concepto", flex=2),
                        TableColumn("Monto", width=70, alignment=HorizontalAlignment.RIGHT),
                    ],
                    data=[
                        {"Concepto": "Seguro de Salud (SFS 3.04%)", "Monto": "$2,584.00"},
                        {"Concepto": "Fondo de Pensiones (AFP 2.87%)", "Monto": "$2,439.50"},
                        {"Concepto": "Retención Impuesto (ISR)", "Monto": "$8,950.00"},
                    ],
                    header_background=Colors.DANGER,
                    header_text_style=Typography.CAPTION_BOLD.copy_with(color=Colors.WHITE),
                    cell_padding=EdgeInsets.symmetric(vertical=3, horizontal=6),
                ),
            ]),
        ], spacing=15),
        Spacer(8),

        code_box(
            "Python (ReportForge Engine Nativo) - Recibo de Nómina",
            "python",
            """from engine import Document, Table, TableColumn, Row, Text, Spacer, Typography, Colors

doc = Document(title="Recibo de Salario")
doc.page(size="A4", orientation="portrait", margin=15)
doc.header(Text("COMPROBANTE DE PAGO DE NÓMINA", style=Typography.H2))
doc.content(
    Row([
        Table(columns=[TableColumn("Percepción", flex=2), TableColumn("Monto", width=80)], data=incomes),
        Table(columns=[TableColumn("Deducción", flex=2), TableColumn("Monto", width=80)], data=deductions),
    ], spacing=15)
)
doc.generate("recibo_nomina.pdf")"""
        ),
        Spacer(12),

        # ---------------------------------------------------------------------
        # REPORTE 4: INFORME MÉDICO Y LABORATORIO CLÍNICO
        # ---------------------------------------------------------------------
        section_title("3.4 Historial Clínico y Laboratorio Médico"),
        Text(
            "Documentos para hospitales, clínicas y centros de diagnóstico. Presenta análisis con valores numéricos, "
            "unidades de medida, rangos normales de referencia y marcas de alerta visual para valores anormales.",
            style=Typography.BODY,
        ),
        Spacer(6),

        Table(
            columns=[
                TableColumn("Prueba / Análisis", flex=2),
                TableColumn("Resultado", width=75, alignment=HorizontalAlignment.CENTER),
                TableColumn("Unidad", width=60),
                TableColumn("Rango Normal", width=95),
                TableColumn("Estado", width=70, alignment=HorizontalAlignment.CENTER),
            ],
            data=[
                {"Prueba / Análisis": "Glucosa en Ayunas", "Resultado": "92.0", "Unidad": "mg/dL", "Rango Normal": "70 - 100", "Estado": "NORMAL"},
                {"Prueba / Análisis": "Colesterol Total", "Resultado": "215.0", "Unidad": "mg/dL", "Rango Normal": "< 200", "Estado": "ELEVADO"},
                {"Prueba / Análisis": "Triglicéridos", "Resultado": "140.0", "Unidad": "mg/dL", "Rango Normal": "< 150", "Estado": "NORMAL"},
                {"Prueba / Análisis": "Hemoglobina", "Resultado": "14.5", "Unidad": "g/dL", "Rango Normal": "13.5 - 17.5", "Estado": "NORMAL"},
            ],
            header_background=Colors.PRIMARY_DARK,
            header_text_style=Typography.CAPTION_BOLD.copy_with(color=Colors.WHITE),
            zebra_color=Colors.BG_ZEBRA,
            cell_padding=EdgeInsets.symmetric(vertical=4, horizontal=6),
            border_width=0.5,
        ),
        Spacer(8),

        code_box(
            "JSON Template - Resultados de Laboratorio Clínico",
            "json",
            """{
  "document": {
    "page": { "size": "A4", "margin": 15 },
    "header": { "type": "text", "value": "LABORATORIOS CLÍNICOS INTEGRALES", "style": "h2" },
    "content": [
      { "type": "text", "value": "Paciente: {{ patient.name }} | Médico: {{ doctor }}" },
      { "type": "spacer", "height": 10 },
      {
        "type": "table",
        "source": "tests",
        "columns": [
          { "field": "test", "title": "Análisis", "flex": 2 },
          { "field": "result", "title": "Resultado", "width": 80, "align": "center" },
          { "field": "ref", "title": "Valores Referencia", "width": 100 }
        ],
        "zebra": true
      },
      { "type": "spacer", "height": 15 },
      { "type": "qr", "value": "https://lab.clinic.org/results/{{ hash }}", "size": 65 }
    ]
  },
  "data": {
    "patient": { "name": "Elena Morales" },
    "doctor": "Dr. Fernando Ruiz",
    "hash": "LAB-9921-X",
    "tests": [{ "test": "Glucosa", "result": "92 mg/dL", "ref": "70 - 100 mg/dL" }]
  }
}"""
        ),
        Spacer(12),

        # ---------------------------------------------------------------------
        # REPORTE 5: ÓRDENES DE COMPRA Y COTIZACIONES
        # ---------------------------------------------------------------------
        section_title("3.5 Órdenes de Compra y Cotizaciones a Proveedores"),
        Text(
            "Documentos de compras y adquisiciones que formalizan acuerdos comerciales entre departamentos de suministros "
            "y proveedores autorizados.",
            style=Typography.BODY,
        ),
        Spacer(6),

        code_box(
            "PHP 8+ (cURL) - Cotización y Orden de Compra",
            "php",
            """<?php
$ch = curl_init('http://localhost:8080/api/v1/reports/generate/');
$data = [
    'document' => [
        'page' => ['size' => 'A4', 'margin' => 15],
        'header' => ['type' => 'text', 'value' => 'COTIZACIÓN FORMAL #{{ quote }}', 'style' => 'h2'],
        'content' => [
            ['type' => 'text', 'value' => 'Atención: {{ customer }}'],
            ['type' => 'spacer', 'height' => 10],
            [
                'type' => 'table',
                'source' => 'services',
                'columns' => [
                    ['field' => 'name', 'title' => 'Servicio', 'flex' => 3],
                    ['field' => 'qty', 'title' => 'Horas', 'width': 50, 'format' => 'number'],
                    ['field' => 'rate', 'title' => 'Tarifa', 'width' => 80, 'format' => 'currency', 'align' => 'right']
                ],
                'zebra' => true
            ]
        ],
        'footer' => ['type' => 'page_number', 'format' => 'Página {page} de {total}', 'alignment' => 'right']
    ],
    'data' => [
        'quote' => 'COT-2026-88',
        'customer' => 'Laboratorios Unidos S.A.',
        'services' => [
            ['name' => 'Auditoría de Seguridad ISO 27001', 'qty' => 40, 'rate' => 125.0],
            ['name' => 'Despliegue de Clúster Kubernetes', 'qty' => 20, 'rate' => 150.0]
        ]
    ],
    'format' => 'pdf',
    'response_type' => 'binary'
];

curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json', 'X-API-Key: rf_live_key']);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$pdf = curl_exec($ch);
file_put_contents('cotizacion.pdf', $pdf);
curl_close($ch);"""
        ),
        Spacer(12),

        # ---------------------------------------------------------------------
        # REPORTE 6: CERTIFICADOS Y DIPLOMAS ACADÉMICOS
        # ---------------------------------------------------------------------
        section_title("3.6 Certificados y Diplomas Académicos"),
        Text(
            "Emisión masiva de diplomas con formato horizontal (landscape), márgenes generosos, diseño solemne "
            "y firma digital respaldada por un código QR que enlaza al registro de acreditaciones.",
            style=Typography.BODY,
        ),
        Spacer(6),

        code_box(
            "Python (ReportForge SDK) - Certificado Académico",
            "python",
            """from reportforge_sdk import ReportForgeClient

client = ReportForgeClient(base_url="http://localhost:8080", api_key="rf_live_secret_key")

certificate_doc = {
    "page": {"size": "A4", "orientation": "landscape", "margin": 25},
    "content": [
        {"type": "text", "value": "CERTIFICADO DE EXCELENCIA ACADÉMICA", "style": "h1", "alignment": "center"},
        {"type": "spacer", "height": 15},
        {"type": "text", "value": "Por cuanto se certifica que:", "style": "body", "alignment": "center"},
        {"type": "spacer", "height": 10},
        {"type": "text", "value": "{{ student.name }}", "style": "h2", "alignment": "center"},
        {"type": "spacer", "height": 10},
        {"type": "text", "value": "ha completado satisfactoriamente el programa de Especialización en:", "style": "body", "alignment": "center"},
        {"type": "text", "value": "{{ course.title }} ({{ course.hours }} horas)", "style": "h3", "alignment": "center"},
        {"type": "spacer", "height": 20},
        {"type": "qr", "value": "https://certs.university.edu/verify/{{ cert_id }}", "size": 70, "alignment": "center"}
    ]
}

data = {
    "student": {"name": "Mariana Valenzuela Peña"},
    "course": {"title": "Arquitectura de Software y Composición PDF", "hours": 120},
    "cert_id": "CERT-2026-X88"
}

resp = client.generate(document=certificate_doc, data=data)
resp.save("certificado_academico.pdf")"""
        ),
        Spacer(12),

        # ---------------------------------------------------------------------
        # REPORTE 7: LOGÍSTICA Y PICKING CON CÓDIGOS DE BARRAS
        # ---------------------------------------------------------------------
        section_title("3.7 Logística, Almacén y Control de Inventario"),
        Text(
            "Etiquetas de despacho para bultos, órdenes de picking y reportes de almacén central que combinan tablas "
            "de productos con códigos de barras lineales Code 128 o EAN-13 para lectura con pistolas lectoras ópticas.",
            style=Typography.BODY,
        ),
        Spacer(6),

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
        Spacer(12),

        # ---------------------------------------------------------------------
        # REPORTE 8: RECIBO DE CAJA CHICA Y VALE DE EGRESO
        # ---------------------------------------------------------------------
        section_title("3.8 Recibos de Caja Menor y Vales de Egreso"),
        Text(
            "Comprobantes internos de tesorería y contabilidad para gastos menores, reposiciones de caja chica, "
            "viáticos de empleados y entregas de fondos con firmas de autorización y recepción.",
            style=Typography.BODY,
        ),
        Spacer(6),

        Row([
            Column([
                Text("VALE DE EGRESO #VAL-2026-402", style=Typography.CAPTION_BOLD),
                Spacer(4),
                Text("Beneficiario: Carlos Mendoza (Sistemas)", style=Typography.CAPTION),
                Text("Concepto: Compra de Cables Patch Cord Cat6 y Conectores RJ45", style=Typography.CAPTION),
                Text("Monto Entregado: $4,500.00 DOP", style=Typography.CAPTION_BOLD),
            ]).padding(all=8).background(Colors.GRAY_100).border(Colors.GRAY_300, 1),

            Column([
                Text("FIRMAS DE AUTORIZACIÓN:", style=Typography.CAPTION_BOLD),
                Spacer(12),
                Divider(thickness=0.5, color=Colors.GRAY_400),
                Text("Entregado por: Tesorería", style=Typography.CAPTION, alignment=HorizontalAlignment.CENTER),
                Spacer(12),
                Divider(thickness=0.5, color=Colors.GRAY_400),
                Text("Recibido conforme: C. Mendoza", style=Typography.CAPTION, alignment=HorizontalAlignment.CENTER),
            ]).padding(all=8).background(Colors.GRAY_100).border(Colors.GRAY_300, 1),
        ], spacing=15),
        Spacer(8),

        code_box(
            "JSON - Recibo de Caja Chica",
            "json",
            """{
  "document": {
    "page": { "size": "A5", "orientation": "landscape", "margin": 12 },
    "content": [
      { "type": "text", "value": "VALE DE CAJA CHICA #{{ id }}", "style": "h2" },
      { "type": "spacer", "height": 8 },
      { "type": "text", "value": "Pagado a: {{ payee }} | Monto: {{ amount | currency }}" },
      { "type": "text", "value": "Por concepto de: {{ reason }}" },
      { "type": "spacer", "height": 15 },
      { "type": "qr", "value": "https://finance.company.com/vouchers/{{ id }}", "size": 50 }
    ]
  },
  "data": { "id": "V-402", "payee": "Carlos Mendoza", "amount": 4500.0, "reason": "Suministros de Red" }
}"""
        ),
        Spacer(12),

        # ---------------------------------------------------------------------
        # REPORTE 9: TARJETA DE EMBARQUE Y TICKETS DE TRANSPORTE
        # ---------------------------------------------------------------------
        section_title("3.9 Tarjetas de Embarque, Pasajes y Boletos de Transporte"),
        Text(
            "Pases de abordar para aerolíneas, ferris y transporte terrestre con formato compacto, código de barras "
            "lineal PDF417/Code128 y código QR de validación en torniquetes.",
            style=Typography.BODY,
        ),
        Spacer(6),

        Row([
            Column([
                Text("BOARDING PASS - VUELO RF-801", style=Typography.CAPTION_BOLD),
                Spacer(4),
                Text("Pasajero: Edwin Abreu / Clase: Ejecutiva", style=Typography.CAPTION),
                Text("Origen: SDQ (Santo Domingo) -> Destino: MAD (Madrid)", style=Typography.CAPTION),
                Text("Puerta: B4 | Asiento: 02A | Embarque: 18:30", style=Typography.CAPTION_BOLD),
            ]).padding(all=8).background(Color.hex("#F0FDF4")).border(Colors.SUCCESS, 1),

            Column([
                Text("CÓDIGO DE ACCESO RÁPIDO:", style=Typography.CAPTION_BOLD),
                Spacer(4),
                Barcode("RF801SDQMAD02A", barcode_type="code128", width=170, height=35),
            ]).padding(all=8).background(Colors.GRAY_100).border(Colors.GRAY_300, 1),
        ], spacing=15),
        Spacer(14),
    ])

    # =========================================================================
    # CAPÍTULO 4: ESPECIFICACIÓN FORMAL DE PLANTILLAS JSON (SPEC v1.0)
    # =========================================================================
    blocks.extend([
        chapter_banner("4", "ESPECIFICACIÓN DE PLANTILLAS DECLARATIVAS JSON", "Esquema Pydantic v2, variables seguras y formateadores"),
        Spacer(10),

        section_title("4.1 Estructura Raíz del Esquema (JSON AST)"),
        Text(
            "Toda solicitud a ReportForge obedece a un esquema tipado estricto en Pydantic:\n"
            "• version: Versión del esquema declarativo (ej: '1.0').\n"
            "• document: Objeto contenedor que define la página (page), el encabezado (header), el contenido (content) y el pie (footer).\n"
            "• data: Objeto de diccionario que contiene los datos dinámicos a inyectar en las expresiones {{ path }}.",
            style=Typography.BODY,
        ),
        Spacer(8),

        section_title("4.2 Formateadores de Datos Integrados"),
        Text(
            "ReportForge incluye formateadores seguros que se aplican automáticamente dentro de las plantillas sin necesidad "
            "de escribir lógica en el servidor ni en el cliente:",
            style=Typography.BODY,
        ),
        Spacer(6),
        Table(
            columns=[
                TableColumn("Formateador", width=100),
                TableColumn("Ejemplo de Sintaxis", width=120),
                TableColumn("Entrada", width=70),
                TableColumn("Resultado Salida", width=110),
            ],
            data=[
                {"Formateador": "currency", "Ejemplo de Sintaxis": "{{ total | currency }}", "Entrada": "1250.5", "Resultado Salida": "$1,250.50"},
                {"Formateador": "currency:[simb]", "Ejemplo de Sintaxis": "{{ total | currency:€ }}", "Entrada": "1250.5", "Resultado Salida": "€1,250.50"},
                {"Formateador": "number", "Ejemplo de Sintaxis": "{{ cant | number }}", "Entrada": "15000", "Resultado Salida": "15,000.00"},
                {"Formateador": "percentage", "Ejemplo de Sintaxis": "{{ tasa | percentage }}", "Entrada": "0.18", "Resultado Salida": "18.0%"},
                {"Formateador": "date", "Ejemplo de Sintaxis": "{{ fecha | date }}", "Entrada": "'2026-11-12'", "Resultado Salida": "12/11/2026"},
                {"Formateador": "uppercase", "Ejemplo de Sintaxis": "{{ nombre | uppercase }}", "Entrada": "'juan'", "Resultado Salida": "JUAN"},
            ],
            header_background=Colors.PRIMARY,
            header_text_style=Typography.CAPTION_BOLD.copy_with(color=Colors.WHITE),
            zebra_color=Colors.BG_ZEBRA,
            cell_padding=EdgeInsets.symmetric(vertical=4, horizontal=6),
            border_width=0.5,
        ),
        Spacer(14),
    ])

    # =========================================================================
    # CAPÍTULO 5: ESPECIFICACIÓN DE LA API REST Y MULTI-TENANCY
    # =========================================================================
    blocks.extend([
        chapter_banner("5", "ESPECIFICACIÓN DE LA API REST Y MULTI-TENANCY", "Endpoints, autenticación, cuotas y colas Celery"),
        Spacer(10),

        section_title("5.1 Autenticación por Inquilino (Multi-Tenancy)"),
        Text(
            "ReportForge opera bajo un modelo de Multi-Tenancy donde cada aplicación cliente cuenta con su propia API Key "
            "(rf_live_...). Todas las plantillas, documentos y recursos subidos están estrictamente aislados en la base de datos "
            "evitando que un inquilino pueda acceder a la información de otro.",
            style=Typography.BODY,
        ),
        Spacer(8),

        section_title("5.2 Matriz de Endpoints de la API v1"),
        Table(
            columns=[
                TableColumn("Método", width=65),
                TableColumn("Endpoint", width=165),
                TableColumn("Propósito", flex=2),
                TableColumn("Respuesta", width=80),
            ],
            data=[
                {"Método": "POST", "Endpoint": "/api/v1/reports/generate/", "Propósito": "Genera reporte síncrono (PDF) o asíncrono en Celery", "Respuesta": "200 / 202"},
                {"Método": "POST", "Endpoint": "/api/v1/reports/preview/", "Propósito": "Previsualización instantánea en memoria sin persistir", "Respuesta": "200 PDF"},
                {"Método": "GET", "Endpoint": "/api/v1/reports/{id}/", "Propósito": "Consulta de estado y métricas (pending, completed, failed)", "Respuesta": "200 JSON"},
                {"Método": "GET", "Endpoint": "/api/v1/reports/{id}/download/", "Propósito": "Descarga de archivo PDF almacenado", "Respuesta": "200 Stream"},
                {"Método": "GET/POST", "Endpoint": "/api/v1/templates/", "Propósito": "Gestión CRUD de plantillas reutilizables del inquilino", "Respuesta": "200 / 201"},
                {"Método": "GET/POST", "Endpoint": "/api/v1/assets/", "Propósito": "Subida y consulta de logotipos, gráficos y fuentes TTF", "Respuesta": "200 / 201"},
                {"Método": "GET", "Endpoint": "/api/docs/", "Propósito": "Documentación interactiva Swagger UI / OpenAPI 3", "Respuesta": "200 HTML"},
            ],
            header_background=Colors.PRIMARY_DARK,
            header_text_style=Typography.CAPTION_BOLD.copy_with(color=Colors.WHITE),
            zebra_color=Colors.BG_ZEBRA,
            cell_padding=EdgeInsets.symmetric(vertical=4, horizontal=6),
            border_width=0.5,
        ),
        Spacer(10),

        section_title("5.3 Flujo Asíncrono para Reportes Masivos (Celery + Redis)"),
        Text(
            "Cuando se especifica 'async_mode': true en la petición, la API no bloquea la conexión esperando el renderizado. "
            "Crea inmediatamente un registro ReportJob en estado 'pending' y delega el procesamiento a la cola de trabajadores Celery. "
            "El cliente recibe HTTP 202 Accepted con la URL de seguimiento para sondear o recibir un webhook cuando esté completado.",
            style=Typography.BODY,
        ),
        Spacer(14),
    ])

    # =========================================================================
    # CAPÍTULO 6: INFRAESTRUCTURA DE ALTO RENDIMIENTO Y DESPLIEGUE
    # =========================================================================
    blocks.extend([
        chapter_banner("6", "DESPLIEGUE Y ARQUITECTURA DE ALTA ESCALABILIDAD", "Docker Compose, Nginx, Celery clúster y almacenamiento S3"),
        Spacer(10),

        section_title("6.1 Arquitectura de Contenedores"),
        Text(
            "El despliegue de ReportForge se organiza en micro-servicios aislados dentro de Docker Compose:\n\n"
            "1. reportforge_nginx: Reverse proxy en puerto 8080 que aplica compresión Gzip, sirve estáticos y delega peticiones dinámicas.\n"
            "2. reportforge_web: Servidor WSGI Gunicorn ejecutando Django REST Framework con workers gthread.\n"
            "3. reportforge_worker: Trabajadores Celery concurrentes que consumen tareas de renderizado pesado desde Redis.\n"
            "4. reportforge_db: Base de datos relacional PostgreSQL 16.\n"
            "5. reportforge_redis: Broker de mensajería y almacenamiento de estados en memoria.",
            style=Typography.BODY,
        ),
        Spacer(8),

        section_title("6.2 Estrategia de Almacenamiento Desacoplado"),
        Text(
            "El motor de almacenamiento (engine.storage) es totalmente agnóstico del proveedor:\n"
            "• LocalStorage: Guarda los archivos en el volumen persistente /app/media/reports.\n"
            "• S3Storage: Guarda los archivos directamente en buckets de AWS S3 o MinIO autohospedado, generando URLs prefirmadas "
            "con tiempo de expiración configurable (ej: 1 hora) para máxima seguridad.",
            style=Typography.BODY,
        ),
        Spacer(8),

        section_title("6.3 Matriz de Resolución de Problemas (Troubleshooting)"),
        Table(
            columns=[
                TableColumn("Síntoma", width=120),
                TableColumn("Causa Raíz", width=140),
                TableColumn("Solución Definitiva", flex=2),
            ],
            data=[
                {"Síntoma": "502 Bad Gateway en Nginx", "Causa Raíz": "Nginx almacena en caché la IP anterior de Docker al reiniciar contenedores.", "Solución Definitiva": "Configurar resolver 127.0.0.11 valid=5s en nginx.conf."},
                {"Síntoma": "403 CSRF Verification Failed", "Causa Raíz": "Falta incluir el puerto del proxy en CSRF_TRUSTED_ORIGINS de Django.", "Solución Definitiva": "Añadir http://localhost:8080 en settings y proxy_set_header Host $http_host."},
                {"Síntoma": "Celery no ejecuta tareas", "Causa Raíz": "El servicio Redis no está disponible o el worker está detenido.", "Solución Definitiva": "Verificar docker compose ps y usar CELERY_TASK_ALWAYS_EAGER=True en tests."},
                {"Síntoma": "Error de fuente tipográfica", "Causa Raíz": "Fuente no estándar de PDF no registrada con ReportLab.", "Solución Definitiva": "Usar fuentes estándar (Helvetica, Times, Courier) o registrar con Typography.register_font()."},
            ],
            header_background=Colors.PRIMARY,
            header_text_style=Typography.CAPTION_BOLD.copy_with(color=Colors.WHITE),
            zebra_color=Colors.BG_ZEBRA,
            cell_padding=EdgeInsets.symmetric(vertical=4, horizontal=6),
            border_width=0.5,
        ),
        Spacer(14),

        # =========================================================================
        # CAPÍTULO 7: SDK PYTHON Y AUTOMATIZACIÓN AVANZADA
        # =========================================================================
        chapter_banner("7", "SDK PYTHON Y AUTOMATIZACIÓN AVANZADA", "Cliente oficial, trabajos asíncronos y gestión de plantillas"),
        Spacer(10),

        section_title("7.1 Instalación y Configuración del Cliente"),
        Text(
            "El SDK de Python está desacoplado del servidor y puede instalarse en cualquier microservicio o script "
            "independiente. Provee reintentos exponenciales automáticos, manejo tipado de excepciones y soporte nativo para streams.",
            style=Typography.BODY,
        ),
        Spacer(6),

        code_box(
            "Python - Generación Asíncrona con Espera Controlada",
            "python",
            """from reportforge_sdk import ReportForgeClient, ServerError, TimeoutError

client = ReportForgeClient(
    base_url="http://localhost:8080",
    api_key="rf_live_secret_key",
    timeout=60.0,
    max_retries=3
)

try:
    # Envía a la cola Celery y espera el resultado mediante sondeo eficiente
    response = client.generate(
        template="large_audit_report",
        data={"company_id": 9921, "year": 2026},
        async_mode=True,
        wait=True,
        poll_interval=1.5,
        max_wait=120.0
    )
    response.save("auditoria_masiva.pdf")
    print(f"Reporte descargado: {response.size} bytes")
except TimeoutError:
    print("El reporte tardó más del tiempo límite configurado.")
except ServerError as e:
    print(f"Error en el servidor: {e}")"""
        ),
        Spacer(8),

        section_title("7.2 Creación Programática de Plantillas"),
        Text(
            "Los sistemas clientes pueden registrar plantillas directamente vía API para que otros servicios las reutilicen:",
            style=Typography.BODY,
        ),
        Spacer(6),

        code_box(
            "Python - Registro de Plantilla Dinámica",
            "python",
            """template_def = {
    "page": {"size": "A4", "margin": 15},
    "content": [
        {"type": "text", "value": "PLANTILLA AUTOMATIZADA: {{ name }}", "style": "h1"},
        {"type": "spacer", "height": 10},
        {"type": "qr", "value": "{{ validation_url }}", "size": 80}
    ]
}

client.create_template(
    name="plantilla_seguridad",
    version="1.0",
    description="Plantilla de verificación automática",
    definition=template_def
)"""
        ),
        Spacer(14),

        Column([
            Text("CONCLUSIÓN Y RECOMENDACIÓN DE ARQUITECTURA", style=Typography.H3),
            Spacer(4),
            Text(
                "ReportForge se consolida como una solución empresarial completa, sólida y probada. "
                "Cualquier aplicación en C#, JavaScript, TypeScript, PHP, Java o Python puede generar reportes de calidad "
                "de imprenta consumiendo su API REST sin necesidad de preocuparse por la complejidad interna del PDF.",
                style=Typography.BODY,
            ),
        ]).padding(all=10).background(Colors.GRAY_100).border(Colors.GRAY_300, 1),
    ])

    doc.content(Column(blocks, spacing=0))

    # Global Footer
    doc.footer(
        Text("ReportForge Enterprise Manual • Todos los derechos reservados • https://github.com/reportforge/reportforge", style=Typography.CAPTION)
        .align_center(),
        spacing=6,
    )

    return doc


if __name__ == "__main__":
    print("Iniciando compilación del Manual Completo Extendido de ReportForge en PDF...")
    doc = build_exhaustive_book()
    output_pdf = "ReportForge_Manual_Oficial_Completo.pdf"
    doc.generate(output_pdf)
    size_bytes = os.path.getsize(output_pdf)
    print(f"Manual Completo generado exitosamente:")
    print(f"-> Archivo: {os.path.abspath(output_pdf)}")
    print(f"-> Tamaño: {size_bytes:,} bytes")
