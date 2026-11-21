# FlowPDF PHP SDK

Universal Document Engine and Fluent Report Builder SDK for **PHP (8.0+)**, powered by in-process **Rust Core** and high-throughput remote HTTP rendering.

[![Packagist](https://img.shields.io/packagist/v/codepro47rd/flowpdf)](https://packagist.org/packages/codepro47rd/flowpdf)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⚡ Key Highlights

- **Ultra-Fast In-Process Generation**: Generates complete PDFs in **~15ms - 35ms** with zero network latency using PHP FFI (`ext-ffi`) and native Rust Core.
- **Embedded Multi-Platform Runtimes**: Bundles precompiled `win-x64` (`flowpdf_native.dll`) and `linux-x64` (`libflowpdf_native.so`) runtimes automatically loaded via FFI.
- **Full Unicode & Spanish Accents**: Native WinAnsi hex encoding for `á, é, í, ó, ú, ñ, Ñ, ¿, ¡, €`.
- **Fluent Declarative Builder**: Composable, chainable, type-safe API for tables, barcodes, QR codes, multi-column layouts, headers, and footers.
- **Hybrid Support**: Run in-process via FFI or use `FlowPdfClient` with cURL for asynchronous background worker rendering.

---

## 📦 Installation

```bash
composer require codepro47rd/flowpdf
```

To enable in-process ultra-fast rendering with Rust Core, ensure `ext-ffi` is enabled in `php.ini`:
```ini
extension=ffi
ffi.enable=true
```

---

## 🚀 Quickstart: In-Process Native PDF Generation

```php
<?php

require_once __DIR__ . '/vendor/autoload.php';

use FlowPdf\ReportDocument;
use FlowPdf\Builders\PageConfigBuilder;
use FlowPdf\Builders\ColumnBuilder;
use FlowPdf\Builders\RowBuilder;
use FlowPdf\Builders\TableBuilder;
use FlowPdf\Builders\TableColumnBuilder;
use FlowPdf\Builders\TextBuilder;

// 1. Build document declaratively with Fluent API
$doc = ReportDocument::create(fn(PageConfigBuilder $p) => $p->a4()->portrait()->margin(15))
    ->title("Factura Comercial en PHP")
    ->header(fn($h) => (
        $h->row(fn(RowBuilder $r) => (
            $r->column(fn(ColumnBuilder $c) => (
                $c->text("FLOWPDF ENTERPRISE", fn(TextBuilder $t) => $t->h2()->bold()->color("#1E40AF")),
                $c->text("Facturación Electrónica en Español: á é í ó ú ñ Ñ ¿ ¡ €", fn(TextBuilder $t) => $t->caption()->color("#4B5563"))
            ), flex: 3),
            $r->column(fn(ColumnBuilder $c) => (
                $c->qrCode("https://example.com/verify/FAC-PHP-2026", size: 60)
            ), flex: 1)
        ))
    ))
    ->content(fn(ColumnBuilder $c) => (
        $c->spacer(10),
        $c->table(fn(TableBuilder $t) => (
            $t->column("Código", "sku", fn(TableColumnBuilder $col) => $col->width(70)),
            $t->column("Descripción del Artículo", "description", fn(TableColumnBuilder $col) => $col->flex(3)),
            $t->column("Cant.", "qty", fn(TableColumnBuilder $col) => $col->width(50)->center()),
            $t->column("Precio Unitario", "price", fn(TableColumnBuilder $col) => $col->width(90)->right()),
            $t->column("Total", "total", fn(TableColumnBuilder $col) => $col->width(90)->right()),
            $t->headerBackground("#1E40AF"),
            $t->zebra(true),
            $t->data([
                ["sku" => "SRV-01", "description" => "Licencia FlowPDF Enterprise Anual", "qty" => 1, "price" => "€ 1,200.00", "total" => "€ 1,200.00"],
                ["sku" => "SUP-02", "description" => "Soporte Técnico 24/7 y Consultoría", "qty" => 2, "price" => "€ 150.00", "total" => "€ 300.00"],
            ])
        )),
        $c->spacer(15),
        $c->divider(1.0, color: "#CBD5E1"),
        $c->spacer(5),
        $c->row(fn(RowBuilder $r) => (
            $r->column(fn(ColumnBuilder $col) => (
                $col->barcode("FACPHP2026", barcodeType: "code128", width: 160, height: 35)
            ), flex: 1),
            $r->column(fn(ColumnBuilder $col) => (
                $col->text("Subtotal: € 1,500.00", fn(TextBuilder $t) => $t->right()),
                $col->text("ITBIS / IVA (18%): € 270.00", fn(TextBuilder $t) => $t->right()),
                $col->text("Total Facturado: € 1,770.00", fn(TextBuilder $t) => $t->h2()->bold()->color("#16A34A")->right())
            ), flex: 1)
        ))
    ))
    ->footer(fn($f) => (
        $f->text("Documento generado in-process con FlowPDF PHP SDK & Rust Core", fn(TextBuilder $t) => $t->caption()->center())
    ));

// 2. Render directly in-process to PDF in ~30 ms!
$pdfBytes = $doc->renderPdf();

file_put_contents("factura_php.pdf", $pdfBytes);
echo "✅ PDF generado exitosamente (" . strlen($pdfBytes) . " bytes)!\n";
```

---

## 🌐 Remote HTTP Rendering (Cloud / Server)

```php
<?php

use FlowPdf\FlowPdfClient;
use FlowPdf\ReportDocument;

$client = new FlowPdfClient('http://localhost:8000', 'your-api-key');

$doc = ReportDocument::create()
    ->content(fn($c) => $c->text("Generado en worker asíncrono con Celery y Redis", fn($t) => $t->h1()));

$pdf = $client->render($doc->build());
file_put_contents("reporte_remoto_php.pdf", $pdf);
```

---

## 📄 License

MIT © 2026 Edwin Abreu & FlowPDF Contributors.
