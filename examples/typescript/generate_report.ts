/**
 * ReportForge TypeScript Client Example (Axios / Strong Typing)
 */

import axios, { AxiosResponse } from 'axios';
import * as fs from 'fs';

interface ReportPayload {
    template?: string;
    document?: Record<string, any>;
    data?: Record<string, any>;
    format?: 'pdf' | 'html';
    response_type?: 'binary' | 'json';
}

async function run(): Promise<void> {
    const endpoint = 'http://localhost:8000/api/v1/reports/generate/';
    const apiKey = 'rf_live_your_tenant_api_key_here';

    const payload: ReportPayload = {
        document: {
            page: { size: 'Letter', orientation: 'landscape', margin: 15 },
            header: {
                type: 'text',
                value: 'INFORME EJECUTIVO FINANCIERO - {{ period }}',
                style: 'h2'
            },
            content: [
                {
                    type: 'chart',
                    chart_type: 'bar',
                    title: 'Rendimiento por Unidad de Negocio (K USD)',
                    labels: ['Banca', 'Seguros', 'Inversión', 'Fintech'],
                    values: [450, 320, 780, 950],
                    width: 500,
                    height: 200
                }
            ],
            footer: {
                type: 'page_number',
                format: 'Página {page} de {total}',
                alignment: 'right'
            }
        },
        data: {
            period: 'Cuarto Trimestre 2026'
        },
        format: 'pdf',
        response_type: 'binary'
    };

    console.log('Generando reporte desde TypeScript...');

    const response: AxiosResponse<ArrayBuffer> = await axios.post(endpoint, payload, {
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': apiKey
        },
        responseType: 'arraybuffer'
    });

    const outputFilePath = 'informe_ts.pdf';
    fs.writeFileSync(outputFilePath, Buffer.from(response.data));
    console.log(`Documento generado con éxito: ${outputFilePath}`);
}

run().catch(err => {
    console.error('Fallo en la generación:', err.message);
});
