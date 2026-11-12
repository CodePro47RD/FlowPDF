# ReportForge for .NET

**ReportForge** is a high-performance enterprise document and reporting engine for .NET 8, .NET 9, and .NET 10.

It combines a **declarative Fluent Builder API**, strongly-typed AST models, an HTTP REST client for microservices, and **in-process native rendering powered by the Rust Core (v2.0)** with pre-compiled embedded binaries for **Windows x64** and **Linux x64**.

---

## ⚡ Highlights

- **Dual-Engine Architecture**:
  - **In-Process Native Rust Core (`ReportForge.Native`)**: Generates production-ready PDFs in ~5 to 25 milliseconds directly in-process. Zero network overhead, zero external dependencies.
  - **Distributed HTTP Client (`ReportForge.Client`)**: Offload massive batch rendering to your distributed ReportForge cluster (Django + Celery + Redis).
- **Fluent Builder API**: Fluent, type-safe declarative API. Design complex invoices, purchase orders, statements, and catalogs in pure C#.
- **Rich Component Support**: Tables with zebra striping and custom column sizing, QR Codes, Code 128 barcodes, multi-column layouts, headers, and footers.
- **Cross-Platform**: Out-of-the-box support for Windows x64 and Linux x64 (glibc/Debian/Ubuntu/Alpine).

---

## 📦 Installation

Install via NuGet Package Manager or .NET CLI:

```bash
dotnet add package ReportForge
```

---

## 🚀 Quick Start (In-Process Native Rendering)

Generate a PDF in **5 milliseconds** with zero setup:

```csharp
using ReportForge.Fluent;

var pdfBytes = ReportDocument.Create(page => page.A4().Margins(30, 30, 30, 30))
    .Header(h => h.Text("INFORME EJECUTIVO").FontSize(20).Bold())
    .Content(col =>
    {
        col.Item().Text("Generado nativamente con ReportForge v2.0 (Rust Core)").FontSize(11).Color("#64748B");
        col.Item().Spacer(15);

        // Tabla tipada
        col.Item().Table(table =>
        {
            table.Columns(cols =>
            {
                cols.Column("sku", "SKU").Width(100);
                cols.Column("desc", "Descripción").Flex(1);
                cols.Column("price", "Precio").Width(80);
            });

            table.Rows(new[]
            {
                new { sku = "PROD-001", desc = "Laptop Dell XPS 15", price = "$1,899.00" },
                new { sku = "PROD-002", desc = "Monitor LG UltraWide 34\"", price = "$650.00" },
                new { sku = "PROD-003", desc = "Teclado Mecánico Keychron K2", price = "$95.00" }
            });
        });

        col.Item().Spacer(20);

        // Código QR
        col.Item().QrCode("https://reportforge.dev").Size(100);
    })
    .Footer(f => f.Text("Página 1 de 1").FontSize(9).Alignment("center"))
    .GeneratePdf("informe_ejecutivo.pdf"); // ¡Guarda directamente en disco!
```

---

## 🌐 Remote Microservice Rendering (HTTP Client)

When rendering asynchronously or delegating to a remote rendering cluster:

```csharp
using ReportForge.Client;
using ReportForge.Fluent;

using var client = new ReportForgeClient("http://localhost:8080", "rf_live_secret_key");

var doc = ReportDocument.Create(p => p.A4())
    .Content(col => col.Item().Text("Factura Electrónica"));

// Render síncrono binario
byte[] pdf = await doc.GeneratePdfRemoteAsync(client);
File.WriteAllBytes("factura_remota.pdf", pdf);
```

---

## 🏗 Architecture & Performance

| Mode | Engine | Latency | Throughput | Use Case |
|---|---|---|---|---|
| **Native In-Process** | Rust Core (`reportforge.dll` / `libreportforge.so`) | **~5 - 25 ms** | > 1,500 docs/sec | High-frequency invoices, microservices, local apps |
| **Distributed HTTP** | Django + Celery + Redis | ~150 - 300 ms | Scalable to millions/day | Heavy async batches, mail merge, centralized auditing |

---

## 📄 License

MIT © Edwin Abreu & ReportForge Contributors
