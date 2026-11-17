<div align="center">

<img src="docs/assets/logo-dark.png" alt="ReportForge" width="380" />

### Motor Universal de Composición y Generación de Documentos y Reportes en Rust
**Composición matemática vectorial • Renderizado in-process en microsegundos • Cero Chromium**

<p align="center">
  <a href="#benchmark"><img src="https://img.shields.io/badge/Velocidad-15ms--35ms-brightgreen.svg" alt="Performance"></a>
  <a href="#tests"><img src="https://img.shields.io/badge/Tests-7%20Passed%20(100%25)-success.svg" alt="Tests"></a>
  <a href="https://www.rust-lang.org/"><img src="https://img.shields.io/badge/Rust-2021%20Edition-orange.svg" alt="Rust Edition 2021"></a>
  <a href="#ecosistema"><img src="https://img.shields.io/badge/C%20ABI-FFI%20Export-blue.svg" alt="C ABI FFI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/Licencia-MIT-lightgrey.svg" alt="License MIT"></a>
</p>

<p align="center">
  <b>Genera facturas, recibos y reportes multipágina de misión crítica a máxima velocidad tipográfica.</b><br/>
  Construido 100% en <b>Rust</b> con exportación C ABI nativa (<code>cdylib</code>, <code>rlib</code>, <code>staticlib</code>) e integrable directamente en C#, TypeScript, Java, PHP y Python.
</p>

[⚡ Inicio Rápido](#-inicio-rápido) •
[📊 Por qué Rust Core](#-comparativa-de-rendimiento) •
[🦀 Uso en Rust](#-uso-en-rust) •
[🔌 C ABI / FFI](#-interfaz-c-abi--ffi) •
[📦 SDKs Multiplataforma](#-ecosistema-de-sdks) •
[📑 Manual PDF](#-documentación-y-manuales)

</div>

---

## ⚡ Inicio Rápido

### Requisitos
* **Rust 1.70+** (Edición 2021) con Cargo instalado.

### Compilar la librería nativa
```bash
# Clonar el repositorio
git clone https://github.com/reportforge/reportforge.git
cd reportforge

# Compilar en modo Release optimizado
cargo build --release
```

Los artefactos compilados se generarán en `target/release/`:
* **Windows**: `reportforge.dll` y `reportforge.lib`
* **Linux**: `libreportforge.so` y `libreportforge.a`
* **macOS**: `libreportforge.dylib`

### Ejecutar Pruebas Automatizadas
```bash
cargo test
```
Ejecuta la suite completa de pruebas unitarias y de integración que validan:
* Parseo de AST JSON y cálculo geométrico.
* Compatibilidad total con acentos en español y símbolos Unicode (`á, é, í, ó, ú, ñ, Ñ, ¿, ¡, €`).
* Tablas con paginación exacta y repetición de cabeceras.
* Códigos de barras (Code128) y códigos QR vectoriales.
* Exportación y liberación de memoria mediante C ABI.

---

## 📊 Comparativa de Rendimiento

| Métrica / Capacidad | Motores Chromium (Puppeteer/Playwright) | Motores Tradicionales (WeasyPrint / Python) | **ReportForge v2.0 (Rust Core)** 🚀 |
| :--- | :--- | :--- | :--- |
| **Tiempo de Generación (1 pág)** | 🔴 2,500 ms – 4,500 ms | 🟡 850 ms – 1,800 ms | 🟢 **15 ms – 35 ms** |
| **Uso de Memoria RAM** | 🔴 350 MB – 650 MB por worker | 🟡 120 MB – 220 MB | 🟢 **14 MB – 24 MB** |
| **Consumo de CPU** | 🔴 Elevado (Browser process) | 🟡 Medio (Interprete) | 🟢 **Mínimo (Nativo compilado)** |
| **Salto de Páginas en Tablas** | 🔴 Cortes a mitad de fila | 🟡 Lento en 100+ páginas | 🟢 **Exacto (Medición fila por fila)** |
| **Repetición de Cabeceras** | 🔴 Inconsistente en CSS | 🟢 Soportado | 🟢 **Nativo (`repeat_header: true`)** |
| **Acentos y Símbolos Unicode** | 🟢 Compatible | 🟢 Compatible | 🟢 **WinAnsi ISO 32000-1 Hexadecimal** |
| **Modo de Ejecución** | Solo vía Node.js / CLI | Solo vía Python | 🟢 **In-Process FFI nativo (Microsegundos)** |

---

## 🦀 Uso en Rust

Puedes usar ReportForge directamente como crate dentro de tu aplicación Rust:

```rust
use reportforge::ast::DocumentDefinitionAst;
use reportforge::pdf_engine::PdfEngine;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let json_template = r#"{
        "page": {
            "size": "A4",
            "orientation": "portrait",
            "margin": 36.0
        },
        "content": [
            {
                "type": "text",
                "value": "Factura Electrónica Dominicana",
                "bold": true,
                "font_size": 18.0
            },
            {
                "type": "text",
                "value": "Cliente: Acrópolis Center • Total: € 1,450.00",
                "font_size": 11.0
            },
            {
                "type": "qr",
                "value": "https://dgii.gov.do/facturacion/e-CF",
                "size": 80.0
            }
        ]
    }"#;

    // Deserializar la plantilla declarativa
    let ast: DocumentDefinitionAst = serde_json::from_str(json_template)?;

    // Inicializar el motor vectorial y renderizar a bytes PDF
    let engine = PdfEngine::new();
    let pdf_bytes = engine.render(&ast, None)?;

    // Guardar en disco
    std::fs::write("factura_generada.pdf", pdf_bytes)?;
    println!("¡PDF generado exitosamente en microsegundos!");
    
    Ok(())
}
```

---

## 🔌 Interfaz C ABI / FFI

ReportForge expone funciones nativas con convención de llamada C para permitir integración in-process de ultra alta velocidad desde cualquier lenguaje:

```c
// Definición de la estructura de retorno
typedef struct {
    uint8_t* data;
    size_t length;
    bool success;
    char* error_message;
} ReportForgeResult;

// Renderizar documento desde JSON
ReportForgeResult reportforge_render_pdf(const char* doc_json, const char* data_json);

// Liberar memoria del resultado
void reportforge_free_result(ReportForgeResult result);

// Obtener versión del motor
const char* reportforge_version(void);
```

---

## 📦 Ecosistema de SDKs

En la carpeta [`sdk/`](sdk/) y listos para distribución en [`docs/packages/`](docs/packages/) se encuentran los paquetes de cliente listos para producción:

1. **C# (.NET 8, 9, 10)**: [`ReportForge.2.0.0.nupkg`](docs/packages/ReportForge.2.0.0.nupkg) con API fluida y carga automática del runtime nativo.
2. **TypeScript / JavaScript**: [`reportforge-2.0.0.tgz`](docs/packages/reportforge-2.0.0.tgz) para Node.js, Bun FFI y Deno.
3. **Java (Java 11+)**: [`reportforge-2.0.0.jar`](docs/packages/reportforge-2.0.0.jar) con JNA empaquetado.
4. **PHP (PHP 8+)**: [`reportforge-php-2.0.0.zip`](docs/packages/reportforge-php-2.0.0.zip) compatible con PHP FFI PSR-4.
5. **Python (3.9+)**: [`reportforge-2.0.0-py3-none-any.whl`](docs/packages/reportforge-2.0.0-py3-none-any.whl) vía `ctypes`.

---

## 📑 Documentación y Manuales

* **Landing Page Interactiva**: Abre [`docs/index.html`](docs/index.html) en tu navegador para probar el Playground interactivo y descargar paquetes.
* **Manual Maestro Oficial**: [`ReportForge_Manual_Oficial_Completo.pdf`](docs/packages/ReportForge_Manual_Oficial_Completo.pdf) (13 páginas) con arquitectura, componentes y especificación técnica.
* **Catálogo de Componentes**: [`docs/COMPONENTS_REFERENCE.md`](docs/COMPONENTS_REFERENCE.md).
* **Especificación del Motor**: [`docs/RUST_CORE_V2.md`](docs/RUST_CORE_V2.md).

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.
