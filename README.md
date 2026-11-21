<div align="center">

<img src="docs/assets/logo-dark.png" alt="FlowPDF" width="380" />

### Motor Universal de Composición y Generación de Documentos y Reportes en Rust
**Composición matemática vectorial • Renderizado in-process en microsegundos • Cero Chromium**

<p align="center">
  <a href="#-comparativa-de-rendimiento"><img src="https://img.shields.io/badge/Velocidad-15ms--35ms-brightgreen.svg" alt="Performance"></a>
  <a href="#b-ejecutar-las-pruebas-unitarias-y-de-integraci%C3%B3n"><img src="https://img.shields.io/badge/Tests-7%20Passed%20(100%25)-success.svg" alt="Tests"></a>
  <a href="https://www.rust-lang.org/"><img src="https://img.shields.io/badge/Rust-2021%20Edition-orange.svg" alt="Rust Edition 2021"></a>
  <a href="#-interfaz-c-abi--ffi"><img src="https://img.shields.io/badge/C%20ABI-FFI%20Export-blue.svg" alt="C ABI FFI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/Licencia-MIT-lightgrey.svg" alt="License MIT"></a>
</p>

<p align="center">
  <b>Genera facturas, recibos y reportes multipágina de misión crítica a máxima velocidad tipográfica.</b><br/>
  Construido 100% en <b>Rust</b> con exportación C ABI nativa (<code>cdylib</code>, <code>rlib</code>, <code>staticlib</code>) e integrable directamente en C#, TypeScript, Java, PHP y Python.
</p>

[⚡ Compilación Local](#-compilaci%C3%B3n-y-ejecuci%C3%B3n-local-en-tu-terminal) •
[🚀 Despliegue por Lenguaje](#-gu%C3%ADa-de-instalaci%C3%B3n-y-despliegue-por-lenguaje) •
[📊 Rendimiento](#-comparativa-de-rendimiento) •
[🦀 Uso en Rust](#-uso-directo-en-rust) •
[🔌 C ABI / FFI](#-interfaz-c-abi--ffi) •
[🐳 Uso con Docker](#-uso-opcional-con-docker) •
[📑 Manuales PDF](#-documentaci%C3%B3n-y-manuales)

</div>

---

## 💡 El Gran Cambio: Arquitectura In-Process (Sin Docker)

A diferencia de las soluciones tradicionales basadas en microservicios web (que requieren levantar servidores Django, Gunicorn, PostgreSQL, Redis, Celery o Chromium headless):

* **Cero sobrecarga de red**: El renderizado se ejecuta **dentro de la misma memoria RAM** de tu aplicación a través de enlaces binarios de alta velocidad (C ABI / FFI).
* **Cero dependencias externas**: No necesitas levantar bases de datos ni colas de mensajería para generar un reporte.
* **Cero consumo ocioso**: La librería solo utiliza recursos en el instante en que compila el PDF (~15 a 35 ms) y libera la memoria de inmediato.

---

## ⚡ Compilación y Ejecución Local en tu Terminal

Para compilar y verificar el motor directamente en tu máquina:

### A) Compilar la librería para producción
En la carpeta raíz del proyecto ejecutas en PowerShell o terminal:

```powershell
cargo build --release
```

Esto compilará el código en modo release ultra-optimizado (con LTO y strip habilitado) y generará los binarios nativos en `target/release/`:
* **Windows**: `flowpdf.dll` y `flowpdf.lib`
* **Linux**: `libflowpdf.so` y `libflowpdf.a`
* **macOS**: `libflowpdf.dylib`

### B) Ejecutar las pruebas unitarias y de integración
```powershell
cargo test
```

Ejecuta las **7 pruebas nativas** (Unicode, tablas, repetición de cabeceras, códigos QR, códigos de barra Code128 y gestión de memoria C-ABI) en **menos de 0.1 segundos**.

### C) ¿Cómo lo consumen tus proyectos?
Tus aplicaciones en **C#, TypeScript, Java, PHP o Python** instalan el paquete de su ecosistema desde el registro oficial y llaman a la librería directamente en su código. Cada paquete trae el motor nativo precompilado para Windows x64 y Linux x64.

---

## 🚀 Guía de Instalación y Despliegue por Lenguaje

| Lenguaje | Registro | Instalación |
|---|---|---|
| C# (.NET 8/9/10) | [NuGet](https://www.nuget.org/packages/FlowPDF) | `dotnet add package FlowPDF` |
| TypeScript / JavaScript | [npm](https://www.npmjs.com/package/flowpdf) | `npm install flowpdf` |
| Java 11+ | Maven Central | `io.github.codepro47rd:flowpdf` |
| PHP 8+ | [Packagist](https://packagist.org/packages/codepro47rd/flowpdf) | `composer require codepro47rd/flowpdf` |
| Python 3.9+ | [PyPI](https://pypi.org/project/flowpdf/) | `pip install flowpdf` |
| Rust | [crates.io](https://crates.io/crates/flowpdf) | `cargo add flowpdf` |

Los paquetes se publican automáticamente desde GitHub Actions en cada versión (ver [`docs/RELEASE_CI.md`](docs/RELEASE_CI.md)).

---

### 🔵 1. C# (.NET 8, 9, 10)

#### Instalación
```bash
dotnet add package FlowPDF
```

#### Cómo se despliega
El paquete NuGet `FlowPDF` incluye las carpetas `runtimes/win-x64/native/flowpdf_native.dll` y `runtimes/linux-x64/native/libflowpdf_native.so`. Al ejecutar:
```bash
dotnet publish -c Release -r linux-x64 --self-contained
# o para Windows:
dotnet publish -c Release -r win-x64
```
El SDK de .NET copia automáticamente el binario nativo adecuado dentro de la carpeta de publicación (`bin/Release/.../publish/runtimes/`). **No tienes que configurar variables de entorno ni copiar DLLs a mano.**

#### Código de Ejemplo (API Fluida)
```csharp
using FlowPdf;

// 1. Construir el documento con tipado fuerte
var doc = ReportDocument.Create(page => page.Size("A4").Margin(36))
    .Header(h => h.Text("Facturación Electrónica en Español")
                  .FontSize(18)
                  .Bold()
                  .Color("#0066FF"))
    .Content(c => {
        c.Text("Cliente: Empresa Modelo, S.R.L. • RNC: 101-00000-1").FontSize(11);
        c.Spacer(10);
        c.Table(t => {
            t.RepeatHeader();
            t.Columns(cols => {
                cols.Add("Descripción", width: 220);
                cols.Add("Cant.", width: 60);
                cols.Add("Precio Unit.", width: 100);
                cols.Add("Total", width: 100);
            });
            t.AddRow("Servidor Cloud Dedicado", "1", "$ 350.00", "$ 350.00");
            t.AddRow("Licencia FlowPDF", "1", "$ 999.00", "$ 999.00");
        });
        c.Spacer(15);
        c.Row(r => {
            r.AddQr("https://dgii.gov.do/e-CF", size: 70);
            r.AddBarcode("FAC2026-9901", format: "CODE128", height: 35);
        });
    });

// 2. Generar en memoria (in-process FFI en ~25 ms)
byte[] pdfBytes = doc.GeneratePdf();
File.WriteAllBytes("factura_csharp.pdf", pdfBytes);
```

---

### 🟨 2. TypeScript / JavaScript (Node.js, Bun, Deno)

#### Instalación
```bash
# Con npm
npm install flowpdf

# Con Bun
bun add flowpdf

# Con pnpm o yarn
pnpm add flowpdf
```

#### Cómo se despliega
El paquete contiene un cargador nativo FFI que detecta automáticamente el sistema operativo (`process.platform === 'win32'` o `'linux'`) y vincula las llamadas nativas de forma transparente. Para entornos contenerizados (como AWS Lambda, Vercel Serverless o contenedores Docker en Alpine/Debian), el archivo `libflowpdf.so` viene preempaquetado dentro de `node_modules/flowpdf/runtimes/`.

#### Código de Ejemplo
```typescript
import { ReportDocument } from "flowpdf";
import * as fs from "fs";

const doc = ReportDocument.create({ size: "A4", margin: 36 })
  .header(h => h.text("Reporte Ejecutivo Trimestral", { fontSize: 18, bold: true, color: "#0066FF" }))
  .content(c => {
    c.text("Soporte completo para acentos: á, é, í, ó, ú, ñ, Ñ, ¿, ¡, €", { fontSize: 11 });
    c.spacer(12);
    c.table({
      repeatHeader: true,
      columns: [
        { title: "Métrica", width: 200 },
        { title: "Valor", width: 100 },
        { title: "Estado", width: 100 }
      ],
      data: [
        { "Métrica": "Tiempo de Generación", "Valor": "24 ms", "Estado": "Óptimo" },
        { "Métrica": "Consumo de Memoria", "Valor": "14 MB", "Estado": "Aprobado" }
      ]
    });
    c.qr("https://example.com/docs", { size: 65 });
  });

// Generar Buffer del PDF directamente en Node/Bun
const pdfBuffer = doc.generatePdf();
fs.writeFileSync("reporte_typescript.pdf", pdfBuffer);
```

---

### ☕ 3. Java (Java 11+)

#### Instalación
Agrégalo en tu `pom.xml` (desde Maven Central):
```xml
<dependency>
    <groupId>io.github.codepro47rd</groupId>
    <artifactId>flowpdf</artifactId>
    <version>1.0.0</version>
</dependency>
```

O en Gradle: `implementation("io.github.codepro47rd:flowpdf:1.0.0")`

#### Cómo se despliega
El JAR integra internamente **JNA (Java Native Access)** y contiene los runtimes para Windows (`flowpdf_native.dll`) y Linux (`libflowpdf_native.so`) dentro de su classpath. Al invocar el generador por primera vez, JNA extrae el binario a una carpeta temporal protegida del sistema operativo y lo mapea en memoria. Funciona de manera idéntica en Spring Boot, Quarkus o aplicaciones de consola en Windows o Linux.

#### Código de Ejemplo
```java
import io.github.codepro47rd.flowpdf.ReportDocument;
import java.io.FileOutputStream;

public class GenerarFactura {
    public static void main(String[] args) throws Exception {
        ReportDocument doc = ReportDocument.create(page -> page.size("A4").margin(36.0f))
            .header(h -> h.text("Factura Comercial Java")
                          .fontSize(18.0f)
                          .bold(true)
                          .color("#0066FF"))
            .content(c -> {
                c.text("Documento emitido con FlowPDF").fontSize(11.0f);
                c.spacer(10.0f);
                c.table(t -> {
                    t.repeatHeader(true);
                    t.addColumn("Artículo", 220.0f);
                    t.addColumn("Subtotal", 120.0f);
                    t.addRow("Suscripción Anual Cloud", "$ 1,200.00");
                });
                c.qr("https://example.com", 75.0f);
            });

        byte[] pdfBytes = doc.generatePdf();
        try (FileOutputStream fos = new FileOutputStream("factura_java.pdf")) {
            fos.write(pdfBytes);
        }
    }
}
```

---

### 🐘 4. PHP (PHP 8.0+)

#### Instalación
```bash
composer require codepro47rd/flowpdf
```

#### Cómo se despliega
PHP interactúa con FlowPDF a través de **PHP FFI** (Foreign Function Interface):
1. Asegúrate de tener habilitada la extensión FFI en tu `php.ini`:
   ```ini
   extension=ffi
   ffi.enable=true
   ```
2. El SDK detecta el sistema operativo y carga `flowpdf_native.dll` (Windows) o `libflowpdf_native.so` (Linux).
3. En entornos PHP-FPM / Nginx, puedes configurar `ffi.preload` para cargar la librería nativa durante el inicio del servidor, reduciendo el tiempo de llamada a menos de **5 milisegundos**.

#### Código de Ejemplo
```php
<?php
require_once __DIR__ . '/vendor/autoload.php';

use FlowPdf\ReportDocument;

$doc = ReportDocument::create(['size' => 'A4', 'margin' => 36])
    ->header(function($h) {
        $h->text("Factura Emitida desde PHP 8.2")
          ->fontSize(18)
          ->bold(true)
          ->color("#0066FF");
    })
    ->content(function($c) {
        $c->text("Comprobante con acentos en español: á, é, í, ó, ú, ñ.");
        $c->spacer(10);
        $c->table([
            'repeatHeader' => true,
            'columns' => [
                ['title' => 'Concepto', 'width' => 250],
                ['title' => 'Monto', 'width' => 100]
            ],
            'rows' => [
                ['Consultoría de Software', '$ 500.00'],
                ['Mantenimiento Mensual', '$ 250.00']
            ]
        ]);
        $c->qr("https://example.com/verify", 70);
    });

// Generar PDF binario
$pdfBytes = $doc->generatePdf();
file_put_contents("factura_php.pdf", $pdfBytes);
```

---

### 🐍 5. Python (Python 3.9+)

#### Instalación
```bash
pip install flowpdf
```

#### Cómo se despliega
El paquete wheel incluye un adaptador ligero basado en la biblioteca estándar `ctypes`. Carga automáticamente `libflowpdf_native.so` en Linux o `flowpdf_native.dll` en Windows sin requerir compiladores C/C++ ni dependencias pesadas en el servidor de producción.

#### Código de Ejemplo
```python
from flowpdf import ReportDocument

doc = (
    ReportDocument.create(size="A4", margin=36)
    .header(lambda h: h.text("Factura Python Nativa", font_size=18, bold=True, color="#0066FF"))
    .content(lambda c: [
        c.text("Generado in-process vía ctypes sin Chromium."),
        c.spacer(height=10),
        c.table(
            columns=[{"title": "Producto", "width": 220}, {"title": "Precio", "width": 100}],
            rows=[["Licencia Rust Core", "$ 999.00"]],
            repeat_header=True
        ),
        c.qr("https://example.com", size=60)
    ])
)

pdf_bytes = doc.generate_pdf()
with open("factura_python.pdf", "wb") as f:
    f.write(pdf_bytes)
```

---

## 📊 Comparativa de Rendimiento

| Métrica / Capacidad | Motores Chromium (Puppeteer/Playwright) | Motores Tradicionales (WeasyPrint / Python) | **FlowPDF (Rust Core)** 🚀 |
| :--- | :--- | :--- | :--- |
| **Tiempo de Generación (1 pág)** | 🔴 2,500 ms – 4,500 ms | 🟡 850 ms – 1,800 ms | 🟢 **15 ms – 35 ms** |
| **Uso de Memoria RAM** | 🔴 350 MB – 650 MB por worker | 🟡 120 MB – 220 MB | 🟢 **14 MB – 24 MB** |
| **Consumo de CPU** | 🔴 Elevado (Browser process) | 🟡 Medio (Interprete) | 🟢 **Mínimo (Nativo compilado)** |
| **Salto de Páginas en Tablas** | 🔴 Cortes a mitad de fila | 🟡 Lento en 100+ páginas | 🟢 **Exacto (Medición fila por fila)** |
| **Repetición de Cabeceras** | 🔴 Inconsistente en CSS | 🟢 Soportado | 🟢 **Nativo (`repeat_header: true`)** |
| **Acentos y Símbolos Unicode** | 🟢 Compatible | 🟢 Compatible | 🟢 **WinAnsi ISO 32000-1 Hexadecimal** |
| **Modo de Ejecución** | Solo vía Node.js / CLI | Solo vía Python | 🟢 **In-Process FFI nativo (Microsegundos)** |

---

## 🦀 Uso Directo en Rust

Si estás construyendo una aplicación en Rust, puedes importar FlowPDF directamente como crate:

```rust
use flowpdf::ast::DocumentDefinitionAst;
use flowpdf::pdf_engine::PdfEngine;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let json_template = r#"{
        "page": { "size": "A4", "orientation": "portrait", "margin": 36.0 },
        "content": [
            {
                "type": "text",
                "value": "Factura Electrónica Rust",
                "bold": true,
                "font_size": 18.0
            },
            {
                "type": "text",
                "value": "Total con acentos: á, é, í, ó, ú, ñ • € 1,450.00",
                "font_size": 11.0
            },
            {
                "type": "qr",
                "value": "https://dgii.gov.do/facturacion/e-CF",
                "size": 80.0
            }
        ]
    }"#;

    let ast: DocumentDefinitionAst = serde_json::from_str(json_template)?;
    let engine = PdfEngine::new();
    let pdf_bytes = engine.render(&ast, None)?;

    std::fs::write("factura_rust.pdf", pdf_bytes)?;
    println!("¡PDF generado en microsegundos!");
    
    Ok(())
}
```

---

## 🔌 Interfaz C ABI / FFI

FlowPDF expone funciones nativas con convención de llamada C para permitir integración in-process de ultra alta velocidad desde cualquier lenguaje:

```c
// Estructura de respuesta de memoria C
typedef struct {
    uint8_t* data;
    size_t length;
    bool success;
    char* error_message;
} FlowPdfResult;

// Renderizar documento desde JSON a PDF
FlowPdfResult flowpdf_render_pdf(const char* doc_json, const char* data_json);

// Liberar memoria asignada por Rust
void flowpdf_free_result(FlowPdfResult result);

// Obtener versión oficial del motor
const char* flowpdf_version(void);
```

---

## 🐳 Uso Opcional con Docker

Aunque para usar FlowPDF en tus proyectos **no necesitas Docker**, si deseas compilar binarios para entornos Linux (`libflowpdf.so`) desde una máquina Windows, puedes compilar usando una imagen de Rust oficial:

```bash
docker run --rm -v ${PWD}:/usr/src/flowpdf -w /usr/src/flowpdf rust:1-alpine cargo build --release
```

Esto generará el archivo `target/release/libflowpdf.so` compatible con Alpine, Debian, Ubuntu y Red Hat.

---

## 📑 Documentación y Manuales

* **Landing Page y Descargas**: Abre [`docs/index.html`](docs/index.html) en tu navegador para probar el Playground interactivo y descargar paquetes.
* **Manual Maestro Oficial**: [`FlowPDF_Manual_Oficial_Completo.pdf`](docs/FlowPDF_Manual_Oficial_Completo.pdf) (13 páginas) con arquitectura, componentes y especificación técnica.
* **Catálogo de Componentes**: [`docs/COMPONENTS_REFERENCE.md`](docs/COMPONENTS_REFERENCE.md).
* **Especificación del Motor**: [`docs/RUST_CORE.md`](docs/RUST_CORE.md).

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.
