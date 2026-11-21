# FlowPDF Java SDK

Universal Document Engine and Fluent Report Builder SDK for **Java (11+)**, powered by in-process **Rust Core** and high-throughput remote HTTP rendering.

🇩🇴 **Made in the Dominican Republic** — FlowPDF is an open-source Dominican library for report and PDF generation.

[![Maven Central](https://img.shields.io/maven-central/v/io.github.codepro47rd/flowpdf)](https://central.sonatype.com/artifact/io.github.codepro47rd/flowpdf)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ⚡ Key Highlights

- **Ultra-Fast In-Process Generation**: Generates complete PDFs in **~15ms - 35ms** with zero network latency using JNA and native Rust Core.
- **Embedded Multi-Platform Runtimes**: Bundles precompiled `win-x64` (`flowpdf_native.dll`) and `linux-x64` (`libflowpdf_native.so`) runtimes automatically extracted and loaded.
- **Full Unicode & Spanish Accents**: Native WinAnsi hex encoding for `á, é, í, ó, ú, ñ, Ñ, ¿, ¡, €`.
- **Zero Third-Party JSON Dependencies**: Built-in lightweight serializer for seamless integration into enterprise Spring Boot, Quarkus, Micronaut, and plain Java applications.
- **Fluent Declarative Builder**: Composable, chainable, type-safe API for tables, barcodes, QR codes, multi-column layouts, headers, and footers.
- **Standard HTTP Client**: Built-in `FlowPdfClient` using `java.net.http.HttpClient` for background worker rendering.

---

## 📦 Installation

### Maven
```xml
<dependency>
    <groupId>io.github.codepro47rd</groupId>
    <artifactId>flowpdf</artifactId>
    <version>1.0.0</version>
</dependency>
<dependency>
    <groupId>net.java.dev.jna</groupId>
    <artifactId>jna</artifactId>
    <version>5.17.0</version>
</dependency>
```

### Gradle
```groovy
implementation 'io.github.codepro47rd:flowpdf:1.0.0'
implementation 'net.java.dev.jna:jna:5.17.0'
```

---

## 🚀 Quickstart: In-Process Native PDF Generation

```java
package com.example;

import io.github.codepro47rd.flowpdf.ReportDocument;
import io.github.codepro47rd.flowpdf.FlowPdfEngine;

import java.io.FileOutputStream;
import java.io.IOException;
import java.util.List;
import java.util.Map;

public class Main {
    public static void main(String[] args) throws IOException {
        // 1. Build document declaratively with Fluent API
        ReportDocument doc = ReportDocument.create(page -> page.a4().portrait().margin(15))
            .title("Factura Comercial en Java")
            .header(h -> h.row(r -> {
                r.column(c -> {
                    c.text("FLOWPDF ENTERPRISE", t -> t.h2().bold().color("#1E40AF"));
                    c.text("Facturación Electrónica en Español: á é í ó ú ñ Ñ ¿ ¡ €", t -> t.caption().color("#4B5563"));
                }, null, 3.0);
                r.column(c -> {
                    c.qrCode("https://example.com/verify/FAC-JAVA-2026", 60);
                }, null, 1.0);
            }))
            .content(c -> {
                c.spacer(10);
                c.table(t -> {
                    t.column("Código", "sku", col -> col.width(70));
                    t.column("Descripción del Artículo", "description", col -> col.flex(3));
                    t.column("Cant.", "qty", col -> col.width(50).center());
                    t.column("Precio Unitario", "price", col -> col.width(90).right());
                    t.column("Total", "total", col -> col.width(90).right());
                    t.headerBackground("#1E40AF");
                    t.zebra(true);
                    t.data(List.of(
                        Map.of("sku", "SRV-01", "description", "Licencia FlowPDF Enterprise Anual", "qty", 1, "price", "€ 1,200.00", "total", "€ 1,200.00"),
                        Map.of("sku", "SUP-02", "description", "Soporte Técnico 24/7 y Consultoría", "qty", 2, "price", "€ 150.00", "total", "€ 300.00")
                    ));
                });
                c.spacer(15);
                c.divider(1.0, "#CBD5E1");
                c.spacer(5);
                c.row(r -> {
                    r.column(col -> {
                        col.barcode("FACJAVA2026", "code128", 160, 35, true);
                    }, null, 1.0);
                    r.column(col -> {
                        col.text("Subtotal: € 1,500.00", t -> t.right());
                        col.text("ITBIS / IVA (18%): € 270.00", t -> t.right());
                        col.text("Total Facturado: € 1,770.00", t -> t.h2().bold().color("#16A34A").right());
                    }, null, 1.0);
                });
            })
            .footer(f -> f.text("Documento generado in-process con FlowPDF Java SDK & Rust Core", t -> t.caption().center()));

        // 2. Render directly in-process to PDF in ~30 ms!
        byte[] pdfBytes = doc.renderPdf();

        try (FileOutputStream out = new FileOutputStream("factura_java.pdf")) {
            out.write(pdfBytes);
        }

        System.out.println("✅ PDF generado exitosamente (" + pdfBytes.length + " bytes)!");
    }
}
```

---

## 🌐 Remote HTTP Rendering (Cloud / Server)

```java
import io.github.codepro47rd.flowpdf.FlowPdfClient;
import io.github.codepro47rd.flowpdf.ReportDocument;

FlowPdfClient client = new FlowPdfClient("http://localhost:8000", "your-api-key");

ReportDocument doc = ReportDocument.create()
    .content(c -> c.text("Generado en worker asíncrono con Celery y Redis", t -> t.h1()));

byte[] pdf = client.render(doc);
```

---

## 📄 License

MIT © 2026 Edwin Abreu & FlowPDF Contributors.
