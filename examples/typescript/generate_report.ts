/**
 * FlowPDF TypeScript Client Example
 * Demonstrates Strongly Typed Models & Fluent Document Builder
 */

import * as fs from 'fs';
import * as path from 'path';
import {
    FlowPdfClient,
    ReportDocument,
    DocumentDefinition,
    ReportPayload
} from '@flowpdf/client';

async function main(): Promise<void> {
    console.log('==========================================================');
    console.log(' FlowPDF TypeScript Client SDK - Typed & Fluent Demo  ');
    console.log('==========================================================\n');

    const baseUrl = 'http://localhost:8080';
    const apiKey = 'rf_live_docker_demo_12345';

    const client = new FlowPdfClient({
        baseUrl,
        apiKey
    });

    // -------------------------------------------------------------
    // OPCIÓN 1: Construcción usando la API Fluent (API fluida)
    // -------------------------------------------------------------
    console.log('[1/2] Construyendo reporte con Fluent Builder en TypeScript...');

    const fluentDoc = ReportDocument.create((page) =>
        page.letter().portrait().margin(20)
    )
        .header((header) =>
            header.text('INFORME TRIMESTRAL DE VENTAS & OPERACIONES', (t) =>
                t.h2().alignCenter().color('#1E3A8A').bold()
            )
        )
        .content((content) =>
            content
                .spacing(12)
                .row((row) =>
                    row
                        .spacing(10)
                        .relativeItem(2.0, (c) =>
                            c.column((col) =>
                                col
                                    .text('Resumen General de Rendimiento', (t) => t.h3().color('#1E3A8A'))
                                    .text('Período Fiscal: {{ period }}')
                                    .text('Responsable: {{ executive }}')
                                    .text('Departamento: {{ department }}')
                            )
                        )
                        .relativeItem(1.0, (c) =>
                            c.column((col) =>
                                col
                                    .text('Estado Auditoría', (t) => t.h3().color('#1E3A8A'))
                                    .text('Fecha: {{ report_date }}')
                                    .text('Calificación: {{ rating }}')
                                    .text('Certificado: ISO-9001')
                            )
                        )
                )
                .divider('#CBD5E1', 1.0, 8.0)
                .text('Desglose Financiero por Región:', (t) => t.h3().color('#1E3A8A'))
                .table((table) =>
                    table
                        .source('regions')
                        .zebra(true)
                        .border('#CBD5E1', 0.5)
                        .headerBackground('#1E3A8A')
                        .columns((cols) => {
                            cols.column('code', 'Código Región', { width: 90 });
                            cols.column('name', 'Nombre de Zona', { flex: 2.5 });
                            cols.column('target', 'Meta Proyectada', { width: 110, format: 'currency', align: 'right' });
                            cols.column('revenue', 'Ingresos Reales', { width: 110, format: 'currency', align: 'right' });
                            cols.column('growth', 'Crecimiento', { width: 90, format: 'percentage', align: 'center' });
                        })
                )
                .spacer(10)
                .row((row) =>
                    row
                        .relativeItem(1.0, (c) =>
                            c.column((col) =>
                                col
                                    .text('Código de Validación Blockchain:', (t) => t.caption().italic())
                                    .barcode('DOC-RF-2026-TS-998', 'code128', 180, 40)
                            )
                        )
                        .relativeItem(1.0, (c) =>
                            c.column((col) =>
                                col
                                    .text('Ventas Netas: RD$ {{ totals.revenue }}', (t) => t.alignRight())
                                    .text('Impuestos Retenidos: RD$ {{ totals.tax }}', (t) => t.alignRight())
                                    .text('BENEFICIO NETO: RD$ {{ totals.net_profit }}', (t) =>
                                        t.h2().color('#0F766E').alignRight().bold()
                                    )
                            )
                        )
                )
        )
        .footer((footer) =>
            footer.pageNumber('Página {page} de {total}', 'right', 'caption')
        );

    const reportData = {
        period: 'Q3 - Año Fiscal 2026',
        executive: 'Ing. Edwin Abreu',
        department: 'Dirección de Operaciones & Tecnología',
        report_date: '12/11/2026',
        rating: 'AAA (Sobresaliente)',
        regions: [
            { code: 'REG-NORTE', name: 'Región Cibao Central & Santiago', target: 2500000.0, revenue: 2890000.0, growth: 15.6 },
            { code: 'REG-SUR', name: 'Región Sur & Barahona', target: 1200000.0, revenue: 1340000.0, growth: 11.6 },
            { code: 'REG-ESTE', name: 'Región Este & Punta Cana', target: 3800000.0, revenue: 4210000.0, growth: 10.7 },
            { code: 'REG-METRO', name: 'Distrito Nacional & Santo Domingo', target: 6500000.0, revenue: 7120000.0, growth: 9.5 }
        ],
        totals: {
            revenue: '15,560,000.00',
            tax: '2,800,800.00',
            net_profit: '12,759,200.00'
        }
    };

    try {
        console.log('Enviando petición a FlowPDF desde TypeScript...');
        const pdfBytes = await client.generatePdf(fluentDoc, reportData);
        const outputPath = path.resolve(__dirname, 'informe_fluent_typescript.pdf');
        fs.writeFileSync(outputPath, Buffer.from(pdfBytes));
        console.log(`[✓] PDF generado con éxito (${pdfBytes.length.toLocaleString()} bytes): ${outputPath}\n`);

        // -------------------------------------------------------------
        // OPCIÓN 2: Construcción usando Interfaces y Tipos Puros
        // -------------------------------------------------------------
        console.log('[2/2] Construyendo reporte con Interfaces Estrictas de TypeScript...');

        const typedDoc: DocumentDefinition = {
            page: { size: 'A4', orientation: 'portrait', margin: 20 },
            header: {
                type: 'text',
                value: 'CERTIFICADO DE CONFORMIDAD TÉCNICA',
                style: 'h2',
                alignment: 'center',
                color: '#1E3A8A'
            },
            content: {
                type: 'column',
                spacing: 12,
                items: [
                    {
                        type: 'text',
                        value: 'Este documento acredita la total compatibilidad y tipado estricto con TypeScript.'
                    },
                    { type: 'spacer', height: 10 },
                    {
                        type: 'qr',
                        value: 'https://github.com/edwin-abreu/flowpdf',
                        size: 80
                    }
                ]
            },
            footer: {
                type: 'page_number',
                format: 'Página {page} de {total}',
                alignment: 'center'
            }
        };

        const typedPdfBytes = await client.generatePdf(typedDoc);
        const typedOutputPath = path.resolve(__dirname, 'certificado_tipado_typescript.pdf');
        fs.writeFileSync(typedOutputPath, Buffer.from(typedPdfBytes));
        console.log(`[✓] PDF tipado generado con éxito (${typedPdfBytes.length.toLocaleString()} bytes): ${typedOutputPath}\n`);

        console.log('¡Prueba de TypeScript completada exitosamente!');
    } catch (err: any) {
        console.error('[ERROR en TypeScript]:', err.message);
        if (err.responseBody) {
            console.error('Detalles del servidor:', err.responseBody);
        }
    }
}

main();
