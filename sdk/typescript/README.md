# FlowPDF TypeScript / JavaScript SDK

Universal Document Engine and Fluent Report Builder SDK for **TypeScript**, **JavaScript**, **Node.js**, and **Bun**, powered by in-process **Rust Core**.

[![npm](https://img.shields.io/npm/v/flowpdf)](https://www.npmjs.com/package/flowpdf)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⚡ Highlights

- **Ultra-Fast In-Process Execution**: Generates complete PDFs in **~15ms - 35ms** with zero network latency.
- **Embedded Native Runtimes**: Precompiled `flowpdf_native.dll` (`win-x64`) and `libflowpdf_native.so` (`linux-x64`) included directly in the npm package.
- **Fluent Report Builder**: Declarative, composable, strictly-typed API for pages, tables, barcodes, QR codes, headers, and footers.
- **Full Unicode & Spanish Accents**: Native WinAnsi hex encoding for `á, é, í, ó, ú, ñ, Ñ, ¿, ¡, €`.
- **Bun & Node.js Support**: Instant native execution via Bun FFI or Node.js (`koffi`), plus `FlowPdfClient` for HTTP/REST server rendering.

---

## 📦 Installation

```bash
# Using npm
npm install flowpdf

# Optional: For in-process native rendering in Node.js
npm install koffi

# Using yarn
yarn add flowpdf

# Using pnpm
pnpm add flowpdf

# Using Bun
bun add flowpdf
```

---

## 🚀 Quickstart: In-Process Native PDF Generation

```typescript
import { ReportDocument, FlowPdfEngine } from 'flowpdf';
import * as fs from 'fs';

// 1. Build document declaratively with Fluent API
const doc = ReportDocument.create(page => page.a4().portrait().margin(15))
    .header(h => {
        h.row(r => {
            r.relativeItem(3, col => {
                col.column(c => {
                    c.text('FLOWPDF ENTERPRISE', t => t.h2().bold().color('#1E40AF'));
                    c.text('Facturación Electrónica en Español: á é í ó ú ñ Ñ ¿ ¡ €', t => t.caption().color('#4B5563'));
                });
            });
            r.relativeItem(1, col => {
                col.qr('https://example.com/verify/FAC-2026-9901', 60);
            });
        });
    })
    .content(c => {
        c.spacer(10);
        c.table(t => {
            t.column({ title: 'Código', field: 'sku', width: 70 });
            t.column({ title: 'Descripción del Producto', field: 'description', flex: 3 });
            t.column({ title: 'Cant.', field: 'qty', width: 50 });
            t.column({ title: 'Precio Unit.', field: 'price', width: 90 });
            t.column({ title: 'Total', field: 'total', width: 90 });
            t.headerBackground('#1E40AF');
            t.zebra(true);
            t.data([
                { sku: 'SRV-01', description: 'Licencia FlowPDF Enterprise', qty: 1, price: '€ 1,200.00', total: '€ 1,200.00' },
                { sku: 'SUP-02', description: 'Soporte Técnico 24/7 Dedicado', qty: 2, price: '€ 150.00', total: '€ 300.00' },
            ]);
        });
        c.spacer(15);
        c.divider({ thickness: 1, color: '#CBD5E1' });
        c.spacer(10);
        c.row(r => {
            r.relativeItem(1, col => {
                col.barcode('FAC20269901', 'code128', { width: 160, height: 35 });
            });
            r.relativeItem(1, col => {
                col.column(sub => {
                    sub.text('Subtotal: € 1,500.00', t => t.caption());
                    sub.text('IVA (18%): € 270.00', t => t.caption());
                    sub.text('Total: € 1,770.00', t => t.h2().bold().color('#16A34A'));
                });
            });
        });
    })
    .footer(f => {
        f.text('Generado in-process con FlowPDF TypeScript SDK & Rust Core', t => t.caption().align('center'));
    });

// 2. Render directly in-process to PDF
const pdfBytes = doc.renderPdf();

fs.writeFileSync('factura_typescript.pdf', Buffer.from(pdfBytes));
console.log(`✅ PDF generado exitosamente (${pdfBytes.length} bytes) en ~25ms!`);
```

---

## 🌐 Remote HTTP Rendering (Cloud / Server)

```typescript
import { FlowPdfClient, ReportDocument } from 'flowpdf';
import * as fs from 'fs';

const client = new FlowPdfClient({
    baseUrl: 'http://localhost:8000',
    apiKey: 'your-api-key'
});

const doc = ReportDocument.create()
    .content(c => c.text('Generado mediante worker asíncrono con Celery y Redis', t => t.h1()));

async function main() {
    const pdfBuffer = await client.render(doc.build());
    fs.writeFileSync('reporte_remoto.pdf', pdfBuffer);
}
main();
```

---

## 📄 License

MIT © 2026 Edwin Abreu & FlowPDF Contributors.
