# Manual Oficial de ReportForge para .NET (Paquete NuGet `ReportForge`)

> **Versión del Paquete:** `2.0.0`  
> **Target Frameworks:** `.NET 8.0`, `.NET 9.0`, `.NET 10.0`  
> **Licencia:** MIT  
> **Plataformas Nativas Soportadas:** Windows x64 (`reportforge_native.dll`), Linux x64 (`libreportforge_native.so`)  
> **Repositorio:** [github.com/reportforge/reportforge](https://github.com/reportforge/reportforge)

---

## 1. Visión General y Propuesta de Valor

**ReportForge** es un motor de composición y renderizado de documentos empresariales de alto rendimiento para el ecosistema .NET moderno. ReportForge introduce un **modelo híbrido de renderizado dual**:

1. **Renderizado Nativo In-Process (Rust Core v2.0):** Compilado en Rust con enlace nativo C-ABI (P/Invoke). Genera documentos PDF de calidad de imprenta en **5 a 25 milisegundos** sin dependencias externas (sin WebKit, sin Node, sin Chromium, sin Python en tiempo de ejecución).
2. **Cliente Remoto de Microservicio (`ReportForgeClient`):** Conector HTTP asíncrono para delegar procesamiento masivo de lotes (batch processing de millones de reportes) a un clúster distribuido de ReportForge (Django + Celery + Redis + S3).

### Comparativa frente a otras soluciones en .NET

| Característica | ReportForge .NET | Otras librerías .NET | iTextSharp / iText 7 | WeasyPrint / wkhtmltopdf |
|---|---|---|---|---|
| **Licencia** | **MIT (100% Libre y Comercial)** | Comercial / PolyForm Noncommercial | AGPL / Comercial de alto costo | BSD / LGPL |
| **Tiempo de Render (Factura Estándar)** | **~5 - 35 ms** | ~20 - 60 ms | ~80 - 200 ms | ~600 - 2,500 ms |
| **Consumo de Memoria** | **< 15 MB** | ~30 - 80 MB | ~50 - 120 MB | > 150 MB (Headless browser) |
| **API Fluent Declarativa** | **Sí** | Sí | No (Imperativa verbosa) | No (HTML / CSS estricto) |
| **Códigos QR y Barcodes Nativos** | **Sí (Zero-dependency en Core)** | Requiere SkiaSharp externo | Requiere módulos adicionales | Requiere librerías JS/Python |
| **Capacidad de Delegación Cloud** | **Nativa (`ReportForgeClient`)** | No (Solo local) | No | Requiere wrappers custom |
| **Binarios Nativos Embebidos** | **Win-x64 y Linux-x64 incluidos** | Solo SkiaSharp | No | No |
| **Soporte Unicode / Acentos / Símbolos** | **Nativo Hexadecimal (WinAnsi/Latin-1)** | Sí | Sí | Sí |

---

## 2. Instalación y Requisitos

### Requisitos del Sistema
- **SDK de .NET:** .NET 8.0 LTS, .NET 9.0 STS o .NET 10.0 Preview.
- **Sistemas Operativos:**
  - Windows x64 (Windows 10, 11, Windows Server 2016 o superior).
  - Linux x64 (glibc 2.31+, Ubuntu 20.04+, Debian 11+, Red Hat Enterprise Linux 8+, Alpine con compatibilidad gnu).
  - macOS (Soporte en roadmap v2.1).

### Instalación vía .NET CLI

```bash
dotnet add package ReportForge --version 2.0.0
```

### Instalación vía Package Manager Console (Visual Studio)

```powershell
Install-Package ReportForge -Version 2.0.0
```

### Configuración en `.csproj`

```xml
<ItemGroup>
  <PackageReference Include="ReportForge" Version="2.0.0" />
</ItemGroup>
```

> [!NOTE]
> El paquete NuGet incluye automáticamente en su interior los binarios nativos bajo la ruta `runtimes/win-x64/native/reportforge_native.dll` y `runtimes/linux-x64/native/libreportforge_native.so`. Al compilar o publicar tu proyecto, el SDK de .NET copia el binario correspondiente al directorio de salida automáticamente.

---

## 3. Arquitectura del Paquete

El paquete está estructurado en 4 espacios de nombres cohesivos:

```
ReportForge
│
├── ReportForge.Fluent       -> API Fluent declarativa para diseño ágil (ReportDocument)
├── ReportForge.Models       -> Modelos POCO fuertemente tipados del AST (DocumentDefinition)
├── ReportForge.Native       -> Motor nativo in-process P/Invoke en Rust (ReportForgeEngine)
└── ReportForge.Client       -> Cliente HTTP para conexión a clusters distribuidos
```

```mermaid
flowchart TD
    A["Tu Aplicación C# / ASP.NET Core"] --> B["ReportDocument.Create(...)"]
    B --> C{"¿Dónde se Renderiza?"}
    
    C -->|"In-Process (Local / Ultrarrápido)"| D["doc.GeneratePdf()"]
    D --> E["ReportForge.Native.ReportForgeEngine"]
    E --> F["NativeLibraryResolver (Windows/Linux)"]
    F --> G["Rust Core v2.0 (reportforge_native.dll / .so)"]
    G --> H["Salida Binaria PDF (~5-25 ms)"]

    C -->|"Remoto (Cluster Asíncrono)"| I["doc.GeneratePdfRemoteAsync(client)"]
    I --> J["ReportForgeClient (HTTP REST)"]
    J --> K["Cluster ReportForge (Django + Celery)"]
    K --> L["Descarga S3 / Streaming"]
```

---

## 4. Primeros Pasos: "Hello World" en 10 Líneas

Crea un archivo `Program.cs` y ejecuta:

```csharp
using ReportForge.Fluent;

var pdf = ReportDocument.Create(page => page.A4().Margins(30, 30, 30, 30))
    .Header(h => h.Text("¡HOLA MUNDO REPORTFORGE!", t => t.H1().Bold().Color("#1E3A8A").AlignCenter()))
    .Content(col =>
    {
        col.Text("Documento generado con el paquete NuGet oficial de ReportForge.").FontSize(12);
        col.Spacer(15);
        col.QrCode("https://reportforge.dev", 80);
    })
    .Footer(f => f.Text("Página 1 de 1", t => t.AlignCenter().Color("#94A3B8")))
    .GeneratePdf("hola_mundo.pdf");

Console.WriteLine("¡PDF generado en microsegundos!");
```

---

## 5. Referencia Exhaustiva de la API Fluent

### 5.1. Configuración de Página (`PageSettingsBuilder`)

El método `ReportDocument.Create(page => ...)` o `doc.Page(page => ...)` permite establecer la geometría base de las páginas.

```csharp
ReportDocument.Create(page => page
    .A4()                             // Tamaños disponibles: .A3(), .A4(), .A5(), .Letter(), .Legal()
    .Portrait()                       // .Portrait() o .Landscape()
    .Margins(top: 25, right: 20, bottom: 25, left: 20) // Márgenes individuales en puntos
    // O margen simétrico:
    // .Margin(20)
);
```

### 5.2. Encabezado y Pie de Página (`Header` y `Footer`)

Se repiten automáticamente en cada página del documento si el contenido principal desborda en varias hojas:

```csharp
doc.Header(header => header
    .Row(row =>
    {
        row.RelativeItem(2.0, col => col.Column(c =>
        {
            c.Text("ACME INDUSTRIAL S.A.", t => t.H2().Bold().Color("#0F172A"));
            c.Text("RNC: 101-23456-7 | info@acme.com", t => t.Caption().Color("#64748B"));
        }));
        row.RelativeItem(1.0, col => col.Column(c =>
        {
            c.Text("FECHA: 12/11/2026", t => t.AlignRight());
            c.Text("ESTADO: PAGADO", t => t.AlignRight().Color("#16A34A").Bold());
        }));
    })
);

doc.Footer(footer => footer
    .Text("Documento emitido electrónicamente con validez fiscal según Ley 126-02.", t => t.Caption().AlignCenter())
);
```

### 5.3. Sistema de Layout: Filas y Columnas Flexibles

El motor implementa un layout flexible, similar a CSS Flexbox:
- `ColumnBuilder`: Apila componentes verticalmente respetando espaciado (`Spacing`).
- `RowBuilder`: Distribuye componentes horizontalmente:
  - `RelativeItem(weight, builder)`: Distribución proporcional basada en peso relativo (flex).
  - `Spacing(pts)`: Espacio horizontal entre celdas contiguas.

```csharp
col.Row(row =>
{
    row.Spacing(12);
    // Columna izquierda (66% del ancho disponible)
    row.RelativeItem(2.0, c => c.Column(clientCol =>
    {
        clientCol.Text("Facturar A:", t => t.H3().Bold());
        clientCol.Text("Banco Internacional del Caribe");
        clientCol.Text("Av. Winston Churchill #1099");
    }));

    // Columna derecha (33% del ancho disponible)
    row.RelativeItem(1.0, c => c.Column(metaCol =>
    {
        metaCol.Text("Número: FAC-2026-0891", t => t.Bold().AlignRight());
        metaCol.Text("Vence: 30/11/2026", t => t.AlignRight());
    }));
});
```

### 5.4. Tipografía, Estilos de Texto y Soporte Unicode Nativo

Los textos aceptan helpers ergonómicos para personalización completa:

```csharp
col.Text("Título Principal", t => t
    .FontSize(18)           // Tamaño en puntos
    .Bold()                 // Negrita
    .Italic()               // Cursiva
    .Color("#1E3A8A")       // Color hexadecimal (#RGB o #RRGGBB)
    .AlignCenter()          // .AlignLeft(), .AlignCenter(), .AlignRight(), .AlignJustify()
);

// Helpers semánticos predefinidos:
col.Text("Subtítulo H2", t => t.H2().Color("#0F766E"));
col.Text("Nota aclaratoria pequeña", t => t.Caption().Italic());
```

#### Soporte Completo para Unicode, Acentos y Caracteres Internacionales

El motor nativo de ReportForge (v2.0) incorpora un encoder hexadecimal ISO 32000-1 para WinAnsi / Latin-1. Esto garantiza que todos los caracteres y símbolos se dibujen con máxima nitidez y sin errores de codificación (mojibake como `Ã³` o `Ã±`):
- **Acentos y caracteres en español:** `á`, `é`, `í`, `ó`, `ú`, `Á`, `É`, `Í`, `Ó`, `Ú`, `ñ`, `Ñ`, `ü`, `Ü`, `¿`, `¡`
- **Símbolos monetarios internacionales:** `€` (Euro), `$`, `£`, `¥`
- **Signos tipográficos y comillas:** `—` (em-dash), `–` (en-dash), `“` `”` (curly quotes), `‘` `’`, `•` (bullet), `©`, `®`, `™`, `°`, `±`

```csharp
col.Text("Facturación Electrónica en Español: á é í ó ú ñ Ñ ¿ ¡ € — • “ ” © ® ™");
```

### 5.5. Tablas de Datos (`TableBuilder`)

Las tablas soportan zebra striping, columnas por píxeles fijos (`Width`) o flexibles (`Flex`), encabezados coloreados y enlace de datos tipados o anónimos:

```csharp
col.Table(table =>
{
    table.Zebra(true)                 // Alternancia de color en filas
         .Border("#E2E8F0", 0.5)      // Borde y grosor
         .HeaderBackground("#1E3A8A") // Color de fondo del encabezado
         .Columns(cols =>
         {
             cols.Column("sku", "Código").Width(70);
             cols.Column("desc", "Descripción").Flex(3.0);
             cols.Add("qty", "Cant.", c => c.Width(50).Number().AlignCenter());
             cols.Add("price", "Precio Unitario", c => c.Width(90).Currency().AlignRight());
             cols.Add("total", "Total", c => c.Width(90).Currency().AlignRight());
         })
         .Rows(new[]
         {
             new { sku = "SRV-01", desc = "Servidor Dell PowerEdge R750", qty = 2, price = "$3,850.00", total = "$7,700.00" },
             new { sku = "SW-48P", desc = "Switch Cisco Catalyst 9300", qty = 3, price = "$1,450.00", total = "$4,350.00" },
             new { sku = "UPS-3K", desc = "UPS APC Smart-UPS 3000VA", qty = 1, price = "$1,100.00", total = "$1,100.00" }
         });
});
```

### 5.6. Códigos QR y Códigos de Barras

Generados 100% vectorialmente sin rasterizado con pérdida:

```csharp
// Código QR
col.QrCode("https://reportforge.dev/verify/FAC-2026", size: 85);

// Código de barras Code 128 (Subset B industrial)
col.Barcode("FAC-2026-9901-VAL", barcodeType: "code128", width: 180, height: 40);
```

### 5.7. Separadores y Espaciadores

```csharp
col.Spacer(15);                                     // Espacio vertical de 15 puntos
col.Divider(color: "#CBD5E1", thickness: 1.0, marginVertical: 8.0); // Línea horizontal
```

---

## 6. Modelos POCO Fuertemente Tipados (AST)

Si prefieres construir documentos mediante estructuras puras de datos o serializarlos/deserializarlos a JSON desde una base de datos:

```csharp
using ReportForge.Models;
using ReportForge.Native;

var document = new DocumentDefinition
{
    Page = new PageSettings("A4", "portrait", 20.0),
    Header = new TextComponent("INFORME FINANCIERO MENSUAL", style: "h2", alignment: "center", color: "#1E3A8A"),
    Content = new ColumnComponent
    {
        Spacing = 12,
        Items = new List<ComponentDefinition>
        {
            new TextComponent("Resumen del estado contable al cierre de mes."),
            new SpacerComponent(10),
            new TableComponent
            {
                Zebra = true,
                BorderColor = "#CBD5E1",
                HeaderBackground = "#1E3A8A",
                Columns = new List<TableColumnDefinition>
                {
                    new("rubro", "Rubro Contable") { Flex = 2.0 },
                    new("monto", "Balance RD$") { Width = 100, Alignment = "right" }
                },
                Data = new List<Dictionary<string, object>>
                {
                    new() { ["rubro"] = "Activos Corrientes", ["monto"] = "RD$ 4,520,000.00" },
                    new() { ["rubro"] = "Pasivos a Corto Plazo", ["monto"] = "RD$ 1,210,000.00" }
                }
            },
            new SpacerComponent(15),
            new QrComponent("https://portal.banco.com/audit/2026-11", 75.0)
        }
    },
    Footer = new PageNumberComponent("Página {page} de {total}", alignment: "center")
};

// Renderizar directamente el objeto POCO con el motor nativo
byte[] pdfBytes = ReportForgeEngine.RenderPdf(document);
File.WriteAllBytes("informe_poco.pdf", pdfBytes);
```

---

## 7. Renderizado In-Process con `ReportForgeEngine`

La clase `ReportForge.Native.ReportForgeEngine` expone métodos de alto nivel con P/Invoke ultra-optimizado:

```csharp
// Método 1: Renderizar desde instancia Fluent
byte[] pdf = doc.GeneratePdf();

// Método 2: Renderizar directamente a archivo en disco
doc.GeneratePdf("C:\\Reportes\\factura.pdf");

// Método 3: Renderizar pasando JSON en crudo y datos dinámicos
string templateJson = File.ReadAllText("template.json");
string dataJson = File.ReadAllText("data.json");
byte[] pdfFromRawJson = ReportForgeEngine.RenderPdf(templateJson, dataJson);

// Método 4: Consultar versión del core Rust embebido
string version = ReportForgeEngine.GetVersion(); // "ReportForge Rust Core v2.0.0"
```

---

## 8. Integración con ASP.NET Core y Web APIs

### 8.1. Endpoint Minimal API (Descarga Directa)

```csharp
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using ReportForge.Fluent;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/api/facturas/{id}/pdf", (string id) =>
{
    var doc = ReportDocument.Create(p => p.A4())
        .Header(h => h.Text($"FACTURA #{id}", t => t.H2().Bold()))
        .Content(c =>
        {
            c.Text($"Factura emitida para la orden {id}.").FontSize(12);
            c.Spacer(10);
            c.QrCode($"https://miempresa.com/factura/{id}", 80);
        });

    byte[] pdfBytes = doc.GeneratePdf();

    // Devuelve el PDF en memoria con el header MIME correcto en ~15 ms
    return Results.File(pdfBytes, "application/pdf", $"Factura_{id}.pdf");
});

app.Run();
```

### 8.2. Inyección de Dependencias para `ReportForgeClient` (Cluster Remoto)

En `Program.cs`:

```csharp
builder.Services.AddSingleton(sp =>
{
    var config = sp.GetRequiredService<IConfiguration>();
    string baseUrl = config["ReportForge:BaseUrl"] ?? "http://reportforge-cluster:8080";
    string apiKey = config["ReportForge:ApiKey"] ?? "rf_live_secret";
    return new ReportForgeClient(baseUrl, apiKey);
});
```

En tu Controlador o Servicio:

```csharp
public class OrderService
{
    private readonly ReportForgeClient _reportForgeClient;

    public OrderService(ReportForgeClient reportForgeClient)
    {
        _reportForgeClient = reportForgeClient;
    }

    public async Task<byte[]> ExportLargeInvoiceAsync(ReportDocument document)
    {
        // Se ejecuta en el cluster Celery/Redis de manera asíncrona
        return await document.GeneratePdfRemoteAsync(_reportForgeClient);
    }
}
```

---

## 9. Despliegue en Docker y Linux

Al compilar tu aplicación para contenedores Linux (por ejemplo, `mcr.microsoft.com/dotnet/aspnet:8.0`), no necesitas instalar librerías adicionales ni compilar nada en C++.

### Ejemplo de `Dockerfile` para ASP.NET Core

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["MiApp.csproj", "./"]
RUN dotnet restore "MiApp.csproj"
COPY . .
RUN dotnet build "MiApp.csproj" -c Release -o /app/build
RUN dotnet publish "MiApp.csproj" -c Release -o /app/publish -r linux-x64 --self-contained false

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app
COPY --from=build /app/publish .

# El archivo libreportforge_native.so ya se encuentra dentro de runtimes/linux-x64/native/
# ReportForge lo resuelve automáticamente sin ninguna configuración extra.
ENTRYPOINT ["dotnet", "MiApp.dll"]
```

---

## 10. Cuatro Ejemplos Completos de Producción

### Ejemplo 1: Factura Comercial Electrónica B2B

```csharp
using ReportForge.Fluent;

var factura = ReportDocument.Create(page => page.A4().Margins(25, 25, 25, 25))
    .Header(header => header.Row(r =>
    {
        r.RelativeItem(2.0, c => c.Column(col =>
        {
            col.Text("SOLUCIONES EN LA NUBE S.R.L.", t => t.H2().Bold().Color("#0F172A"));
            col.Text("RNC: 1-31-88990-2 | Reg. Mercantil: 55421-SD").Caption().Color("#64748B");
            col.Text("Av. Lope de Vega #45, Santo Domingo, R.D.").Caption().Color("#64748B");
        }));
        r.RelativeItem(1.0, c => c.Column(col =>
        {
            col.Text("FACTURA DE CRÉDITO FISCAL", t => t.Bold().Color("#1E3A8A").AlignRight());
            col.Text("NCF: B0100045892", t => t.H3().Bold().AlignRight());
            col.Text("Fecha: 12/11/2026", t => t.AlignRight());
        }));
    }))
    .Content(content => content
        .Divider("#E2E8F0", 1.0, 10.0)
        .Row(r =>
        {
            r.RelativeItem(1.5, c => c.Column(col =>
            {
                col.Text("DATOS DEL RECEPTOR", t => t.Bold().Color("#1E3A8A"));
                col.Text("Cliente: Corporación de Telecomunicaciones Antillana");
                col.Text("RNC: 1-01-77884-3");
                col.Text("Condición: Crédito 30 días");
            }));
            r.RelativeItem(1.0, c => c.Column(col =>
                col.Barcode("B0100045892", "code128", width: 140, height: 35)
            ));
        })
        .Spacer(12)
        .Table(t =>
        {
            t.Zebra(true)
             .HeaderBackground("#1E3A8A")
             .Border("#CBD5E1", 0.5)
             .Columns(c =>
             {
                 c.Column("sku", "Item").Width(60);
                 c.Column("desc", "Descripción").Flex(3.0);
                 c.Add("cant", "Cant.", col => col.Width(45).AlignCenter());
                 c.Add("precio", "Precio Unit.", col => col.Width(80).AlignRight());
                 c.Add("itbis", "ITBIS", col => col.Width(70).AlignRight());
                 c.Add("total", "Importe", col => col.Width(85).AlignRight());
             })
             .Rows(new[]
             {
                 new { sku = "SRV-01", desc = "Cluster Kubernetes Dedicado (Mes Nov 2026)", cant = "1", precio = "85,000.00", itbis = "15,300.00", total = "100,300.00" },
                 new { sku = "STG-TB", desc = "Almacenamiento NVMe Tier 1 (10 TB)", cant = "10", precio = "2,500.00", itbis = "4,500.00", total = "29,500.00" },
                 new { sku = "SUP-24", desc = "Soporte Platinum 24/7 con SLA 15 min", cant = "1", precio = "20,000.00", itbis = "3,600.00", total = "23,600.00" }
             });
        })
        .Spacer(10)
        .Row(r =>
        {
            r.RelativeItem(1.5, c => c.Column(col =>
            {
                col.Text("Verificación Fiscal DGII:", t => t.Caption().Italic());
                col.QrCode("https://dgii.gov.do/ecf/v?ncf=B0100045892&rnc=131889902", 75);
            }));
            r.RelativeItem(1.0, c => c.Column(col =>
            {
                col.Text("Subtotal: RD$ 130,000.00", t => t.AlignRight());
                col.Text("ITBIS (18%): RD$ 23,400.00", t => t.AlignRight());
                col.Text("TOTAL A PAGAR: RD$ 153,400.00", t => t.H2().Bold().Color("#1E3A8A").AlignRight());
            }));
        }))
    .Footer(f => f.Text("Factura electrónica firmada digitalmente según Ley 126-02.", t => t.Caption().AlignCenter().Color("#94A3B8")));

factura.GeneratePdf("factura_b2b.pdf");
```

### Ejemplo 2: Estado de Cuenta Bancario Mensual

```csharp
using ReportForge.Fluent;

var estadoCuenta = ReportDocument.Create(page => page.Letter().Margins(20, 20, 20, 20))
    .Header(h => h.Row(r =>
    {
        r.RelativeItem(1.0, c => c.Text("BANCO DE AHORROS Y CRÉDITO DEL SUR", t => t.H2().Bold().Color("#047857")));
        r.RelativeItem(1.0, c => c.Text("ESTADO DE CUENTA", t => t.H2().Bold().AlignRight().Color("#334155")));
    }))
    .Content(content => content
        .Divider("#047857", 2.0, 6.0)
        .Text("Titular: ING. MARCOS ANDRÉS PEÑA | Cuenta Corriente: 401-998823-1").Bold()
        .Text("Período: 01/10/2026 al 31/10/2026 | Moneda: DOP").Color("#64748B")
        .Spacer(10)
        .Table(table =>
        {
            table.Zebra(true)
                 .HeaderBackground("#047857")
                 .Columns(cols =>
                 {
                     cols.Column("fecha", "Fecha").Width(65);
                     cols.Column("desc", "Concepto / Descripción").Flex(3.0);
                     cols.Add("debito", "Débito (-)", c => c.Width(80).AlignRight());
                     cols.Add("credito", "Crédito (+)", c => c.Width(80).AlignRight());
                     cols.Add("balance", "Balance", c => c.Width(85).AlignRight());
                 })
                 .Rows(new[]
                 {
                     new { fecha = "01/10", desc = "BALANCE INICIAL", debito = "", credito = "", balance = "142,500.00" },
                     new { fecha = "05/10", desc = "Transferencia LBTR Recibida de Codia SRL", debito = "", credito = "85,000.00", balance = "227,500.00" },
                     new { fecha = "12/10", desc = "Pago de Nómina Quincenal Lote #89", debito = "64,200.00", credito = "", balance = "163,300.00" },
                     new { fecha = "28/10", desc = "Pago Servicios Cloud y Telecomunicaciones", debito = "15,400.00", credito = "", balance = "147,900.00" }
                 });
        })
        .Spacer(15)
        .Text("Balance Disponible al Cierre: RD$ 147,900.00", t => t.H3().Bold().Color("#047857").AlignRight()))
    .Footer(f => f.Text("Comuníquese al 809-555-0100 para cualquier aclaración dentro de los 30 días posteriores al corte.", t => t.Caption().AlignCenter()));

estadoCuenta.GeneratePdf("estado_cuenta_bancario.pdf");
```

### Ejemplo 3: Etiqueta Logística Térmica de Despacho (Shipping Label)

```csharp
using ReportForge.Fluent;

var etiqueta = ReportDocument.Create(page => page.A5().Portrait().Margins(15, 15, 15, 15))
    .Header(h => h.Row(r =>
    {
        r.RelativeItem(2.0, c => c.Text("EXPRESS LOGISTICS • NEXT DAY", t => t.H2().Bold().Color("#DC2626")));
        r.RelativeItem(1.0, c => c.Text("PRIORITY", t => t.H1().Bold().AlignRight()));
    }))
    .Content(content => content
        .Divider("#000000", 2.0, 5.0)
        .Row(r =>
        {
            r.RelativeItem(1.0, c => c.Column(col =>
            {
                col.Text("ORIGEN (SHIP FROM):", t => t.Caption().Bold());
                col.Text("Centro de Distribución Haina");
                col.Text("Km 12 Carr. Sánchez, Haina, R.D.");
            }));
            r.RelativeItem(1.0, c => c.Column(col =>
            {
                col.Text("DESTINO (SHIP TO):", t => t.Caption().Bold());
                col.Text("Dra. Elena Rosario");
                col.Text("Calle Del Sol #204, Santiago, R.D.");
                col.Text("Tel: 809-555-9874");
            }));
        })
        .Spacer(10)
        .Divider("#000000", 1.0, 4.0)
        .Row(r =>
        {
            r.RelativeItem(1.0, c => c.Text("PESO: 4.8 KG", t => t.Bold()));
            r.RelativeItem(1.0, c => c.Text("BULTOS: 1 DE 1", t => t.Bold().AlignRight()));
        })
        .Spacer(10)
        .Barcode("TRK-889920194-DO", "code128", width: 220, height: 50)
        .Spacer(10)
        .Row(r =>
        {
            r.RelativeItem(1.0, c => c.QrCode("https://track.logistics.com/TRK-889920194-DO", 65));
            r.RelativeItem(2.0, c => c.Column(col =>
            {
                col.Text("NÚMERO DE GUÍA:", t => t.Caption());
                col.Text("TRK-889920194-DO", t => t.H2().Bold());
                col.Text("Ruta: STI-HUB-04").Bold();
            }));
        }))
    .GeneratePdf("etiqueta_envio.pdf");
```

### Ejemplo 4: Certificado de Acreditación / Diploma

```csharp
using ReportForge.Fluent;

var diploma = ReportDocument.Create(page => page.A4().Landscape().Margins(40, 40, 40, 40))
    .Header(h => h.Text("INSTITUTO TECNOLÓGICO DE LAS AMÉRICAS", t => t.H2().Bold().AlignCenter().Color("#1E3A8A")))
    .Content(content => content
        .Spacer(15)
        .Text("OTORGA EL PRESENTE DIPLOMA A:", t => t.Caption().AlignCenter().Color("#64748B"))
        .Spacer(8)
        .Text("ING. ALEJANDRO RAMÍREZ CASTILLO", t => t.H1().Bold().AlignCenter().Color("#0F172A"))
        .Spacer(6)
        .Divider("#D97706", 1.5, 6.0)
        .Spacer(10)
        .Text("Por haber completado satisfactoriamente los 120 créditos académicos y la evaluación práctica del programa especializado en:", t => t.AlignCenter())
        .Spacer(8)
        .Text("ARQUITECTURA DE SOFTWARE DISTRIBUIDO Y SISTEMAS DE ALTO RENDIMIENTO", t => t.H3().Bold().AlignCenter().Color("#1E3A8A"))
        .Spacer(25)
        .Row(r =>
        {
            r.RelativeItem(1.0, c => c.Column(col =>
            {
                col.Divider("#64748B", 1.0, 4.0);
                col.Text("Dr. Roberto Méndez", t => t.Bold().AlignCenter());
                col.Text("Rector Académico", t => t.Caption().AlignCenter());
            }));
            r.RelativeItem(0.5, c => c.QrCode("https://cert.itla.edu.do/verify/CERT-2026-990", 60));
            r.RelativeItem(1.0, c => c.Column(col =>
            {
                col.Divider("#64748B", 1.0, 4.0);
                col.Text("Ing. Carmen Santana", t => t.Bold().AlignCenter());
                col.Text("Directora del Decanato", t => t.Caption().AlignCenter());
            }));
        }))
    .Footer(f => f.Text("Certificado registrado en el Libro V, Folio 128, Registro Académico Nacional.", t => t.Caption().AlignCenter().Color("#94A3B8")));

diploma.GeneratePdf("diploma_academico.pdf");
```

---

## 11. Rendimiento y Métricas de Benchmark

Pruebas ejecutadas en entorno estándar Windows 11 x64 / Intel Core i7 / 32 GB RAM:

| Escenario | Método | Páginas | Tiempo de Render | Consumo RAM |
|---|---|---|---|---|
| **Factura Comercial B2B** | In-Process Rust Core | 1 | **12.4 ms** | 12 MB |
| **Estado de Cuenta con 100 Filas** | In-Process Rust Core | 3 | **34.1 ms** | 18 MB |
| **Lote de 1,000 Facturas** | Paralelo (Parallel.ForEach) | 1,000 | **2.8 segundos** | 65 MB |
| **Factura vía HTTP Remoto** | `ReportForgeClient` | 1 | **829 ms** (Red + Celery) | Remoto |

> [!TIP]
> Para aplicaciones web con alto tráfico (por ejemplo, e-commerce generando comprobantes o pasarelas de pago generando recibos), utiliza siempre `doc.GeneratePdf()` in-process. Podrás despachar miles de solicitudes por segundo por nodo sin tocar la base de datos de reportes ni encolar tareas.

---

## 12. Preguntas Frecuentes y Solución de Problemas

#### ¿Por qué el binario nativo se llama `reportforge_native.dll`?
En Windows, el sistema de archivos NTFS no distingue mayúsculas de minúsculas. Si la DLL de C# se llama `ReportForge.dll` y la DLL nativa de C se llamase `reportforge.dll`, Windows intentaría cargar la biblioteca administrada de C# al invocar `DllImport`, causando un `EntryPointNotFoundException`. Al nombrarla `reportforge_native.dll`, se garantiza una resolución 100% limpia sin ninguna colisión.

#### ¿Necesito instalar Rust en mis servidores de producción?
**No.** Los binarios para Windows x64 (`reportforge_native.dll`) y Linux x64 (`libreportforge_native.so`) ya vienen compilados y firmados dentro del paquete NuGet. Solo necesitas el runtime estándar de .NET.

#### ¿Cómo publico una aplicación Single-File (`--self-contained`)?
Al ejecutar:
```bash
dotnet publish -c Release -r win-x64 --self-contained
```
El `NativeLibraryResolver` de ReportForge está programado para buscar en:
1. `AppContext.BaseDirectory`
2. La subcarpeta `runtimes/win-x64/native/`
3. El directorio de ensamblado
4. Las rutas del sistema operativo.
Por tanto, funcionará directamente sin parámetros adicionales.

---

## 13. Estructura Sugerida para tu Sitio Web de Documentación

Si vas a publicar esta documentación en un generador estático (como Docusaurus, VitePress, Starlight o Nextra), te recomendamos la siguiente jerarquía de páginas:

```
docs/
├── index.md                 -> Introducción y propuesta de valor
├── getting-started/
│   ├── installation.md      -> Instalación NuGet y compatibilidad
│   ├── quickstart.md        -> Hola Mundo en 5 minutos
│   └── architecture.md      -> Arquitectura Dual (Rust Core vs HTTP)
├── fluent-api/
│   ├── pages.md             -> Configuración de Página (A4, márgenes)
│   ├── layouts.md           -> Filas, Columnas y Flex Spacing
│   ├── typography.md        -> Tipografía, colores y estilos
│   ├── tables.md            -> Tablas, columnas y datos
│   └── barcodes-qr.md       -> Códigos QR y Code 128
├── poco-models/
│   └── ast-reference.md     -> Uso de DocumentDefinition sin builders
├── integration/
│   ├── aspnet-core.md       -> Minimal APIs y Controladores
│   ├── dependency-injection.md -> Registro en IServiceCollection
│   └── docker.md            -> Dockerfile para Linux x64
├── examples/
│   ├── invoice-b2b.md       -> Factura Comercial B2B
│   ├── bank-statement.md    -> Estado de Cuenta
│   ├── shipping-label.md    -> Etiqueta de Envíos
│   └── certificate.md       -> Diploma Académico
└── api-reference/
    ├── report-document.md   -> Clase ReportDocument
    └── reportforge-engine.md -> Clase ReportForgeEngine
```
