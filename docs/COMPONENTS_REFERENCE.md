# Catálogo de Componentes FlowPDF

> FlowPDF es una librería dominicana 🇩🇴 de código abierto para la generación de reportes y documentos PDF.

Referencia exhaustiva de todos los componentes disponibles tanto en la API fluida de Python como en el esquema declarativo JSON.

---

## 1. Text (Texto)
Renderiza texto plano o enriquecido con envoltura automática de líneas y cálculo métrico de fuentes.

### Python Fluent API:
```python
from engine import Text, Typography, Colors

Text("Factura Comercial", style=Typography.H1, alignment="left")
Text("Total a Pagar: $15,000", style=Typography.BODY_BOLD)
```

### JSON Template:
```json
{
  "type": "text",
  "value": "Total a Pagar: {{ total | currency }}",
  "style": "h2",
  "alignment": "right",
  "color": "#1E40AF"
}
```

---

## 2. Table (Tablas Dinámicas)
Permite construir tablas de alto rendimiento con anchos de columna fijos o relativos (`flex`), encabezados estilizados, colores de celdas alternados (zebra), divisores y división multipágina automática con repetición de encabezados.

### Python Fluent API:
```python
from engine import Table, TableColumn, Colors

table = Table(
    columns=[
        TableColumn("SKU", width=80),
        TableColumn("Descripción", flex=3),
        TableColumn("Cantidad", width=60, alignment="center"),
        TableColumn("Precio", width=90, alignment="right"),
    ],
    data=items,
    header_background=Colors.PRIMARY,
    zebra_color=Colors.BG_ZEBRA,
    repeat_header=True
)
```

### JSON Template:
```json
{
  "type": "table",
  "source": "items",
  "columns": [
    { "field": "sku", "title": "SKU", "width": 80 },
    { "field": "desc", "title": "Descripción", "flex": 3 },
    { "field": "qty", "title": "Cant.", "width": 60, "format": "number", "align": "center" },
    { "field": "price", "title": "Precio", "width": 90, "format": "currency", "align": "right" }
  ],
  "header_background": "#1E40AF",
  "zebra": true,
  "repeat_header": true
}
```

---

## 3. Chart (Gráficos Estadísticos)
Genera gráficos de barras, líneas, circulares (pie) o áreas con renderizado de alta resolución (200 DPI).

### Python Fluent API:
```python
from engine import Chart

Chart(
    chart_type="bar",
    labels=["Q1", "Q2", "Q3", "Q4"],
    values=[12000, 18500, 24000, 31000],
    title="Crecimiento de Ventas 2026",
    width=400,
    height=180
)
```

---

## 4. QRCode & Barcode (Códigos QR y de Barras)

### Python Fluent API:
```python
from engine import QRCode, Barcode

QRCode("https://example.com/inv/9901", size=80)
Barcode("INV9901", barcode_type="code128", width=160, height=40)
```

---

## 5. Column & Row (Distribución Espacial)

### Python Fluent API:
```python
from engine import Column, Row, Text, Spacer

Row([
    Text("Columna A").padding(all=10).background("#F1F5F9"),
    Text("Columna B").padding(all=10).background("#E2E8F0"),
], spacing=15)
```

---

## 6. PageNumber (Numeración de Páginas)
Muestra la numeración dinámica calculada en dos pasadas exactas:

### Python Fluent API:
```python
from engine import PageNumber

PageNumber(format_str="Página {page} de {total}", alignment="right")
```

---

## 7. Watermark (Marcas de Agua Flotantes)
Permite superponer marcas de agua en texto flotante en cualquier coordenada libre `(x, y)` o mediante presets de alineación (`center`, `top-left`, etc.), con rotación en cualquier ángulo, opacidad graduable y compatibilidad idéntica en PDF, Word (.docx) y Excel (.xlsx).

### JSON Template:
```json
{
  "watermark": {
    "text": "CONFIDENCIAL",
    "x": 120.0,
    "y": 300.0,
    "rotation": -45.0,
    "opacity": 0.18,
    "font_size": 48.0,
    "color": "#DC2626",
    "background": true
  }
}
```

### C# Fluent API:
```csharp
doc.Watermark("BORRADOR", rotation: -45f, opacity: 0.15f, color: "#888888");
```

---

## 8. Formatos de Salida Multi-Plataforma
FlowPDF permite exportar el mismo documento declarativo a tres formatos empresariales nativos:

1. **PDF (`.pdf`)**: Motor vectorial nativo con paginación predictiva, fuentes TrueType y marcas de agua translúcidas (`flowpdf_render_pdf`).
2. **Microsoft Excel (`.xlsx`)**: Hojas de cálculo con tablas dinámicas, zebra striping, formatos de moneda/número y marca de agua flotante (`flowpdf_render_xlsx`).
3. **Microsoft Word (`.docx`)**: Documentos editables de Microsoft Word con tipografía, párrafos, tablas estilizadas y marcas de agua (`flowpdf_render_docx`).
