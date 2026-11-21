/**
 * FlowPDF Client Example in Node.js / Modern JavaScript (Fetch API)
 */

const fs = require('fs');

async function generateReport() {
    const url = 'http://localhost:8000/api/v1/reports/generate/';
    const apiKey = 'rf_live_your_tenant_api_key_here';

    const payload = {
        document: {
            page: { size: 'A4', orientation: 'portrait', margin: 15 },
            header: {
                type: 'text',
                value: 'CERTIFICADO DE PARTICIPACIÓN - {{ student.name }}',
                style: 'h2'
            },
            content: [
                {
                    type: 'text',
                    value: 'Por cuanto el participante ha completado satisfactoriamente el programa formativo:',
                    style: 'body'
                },
                { type: 'spacer', height: 15 },
                {
                    type: 'text',
                    value: '{{ course.title }} ({{ course.hours }} Horas Académicas)',
                    style: 'h3'
                },
                { type: 'spacer', height: 20 },
                {
                    type: 'qr',
                    value: 'https://example.com/verify/{{ cert_code }}',
                    size: 80
                }
            ],
            footer: {
                type: 'page_number',
                format: 'Página {page} de {total}',
                alignment: 'center'
            }
        },
        data: {
            student: { name: 'Mariana Valenzuela' },
            course: { title: 'Arquitectura de Software y Document Composition en Python', hours: 40 },
            cert_code: 'CERT-2026-X992'
        },
        format: 'pdf',
        response_type: 'binary'
    };

    console.log('Solicitando generación de certificado a FlowPDF...');

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': apiKey
        },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Error en FlowPDF (${response.status}): ${errorText}`);
    }

    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    const outputFile = 'certificado_js.pdf';

    fs.writeFileSync(outputFile, buffer);
    console.log(`Certificado PDF generado con éxito: ${outputFile} (${buffer.length} bytes)`);
}

generateReport().catch(console.error);
