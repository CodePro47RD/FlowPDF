<?php
/**
 * FlowPDF PHP Integration Example using cURL
 */

$url = 'http://localhost:8000/api/v1/reports/generate/';
$apiKey = 'fp_live_your_tenant_api_key_here';

$payload = [
    'document' => [
        'page' => ['size' => 'A4', 'orientation' => 'portrait', 'margin' => 15],
        'header' => [
            'type' => 'text',
            'value' => 'COTIZACIÓN FORMAL #{{ quote_id }}',
            'style' => 'h2'
        ],
        'content' => [
            [
                'type' => 'text',
                'value' => 'Atención a: {{ customer_name }}',
                'style' => 'body'
            ],
            ['type' => 'spacer', 'height' => 10],
            [
                'type' => 'table',
                'source' => 'services',
                'columns' => [
                    ['field' => 'service', 'title' => 'Servicio', 'flex' => 3],
                    ['field' => 'cost', 'title' => 'Inversión', 'width' => 90, 'format' => 'currency', 'align' => 'right']
                ],
                'zebra' => true
            ]
        ],
        'footer' => [
            'type' => 'page_number',
            'format' => 'Página {page} de {total}',
            'alignment' => 'right'
        ]
    ],
    'data' => [
        'quote_id' => 'COT-2026-44',
        'customer_name' => 'Laboratorios Unidos S.A.',
        'services' => [
            ['service' => 'Mantenimiento Preventivo de Servidores', 'cost' => 1200.00],
            ['service' => 'Auditoría de Ciberseguridad ISO 27001', 'cost' => 4500.00]
        ]
    ],
    'format' => 'pdf',
    'response_type' => 'binary'
];

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/json',
    'X-API-Key: ' . $apiKey
]);

echo "Enviando solicitud cURL a FlowPDF...\n";
$pdfData = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

if ($httpCode === 200) {
    $filename = 'cotizacion_php.pdf';
    file_put_contents($filename, $pdfData);
    echo "Reporte guardado exitosamente: " . $filename . " (" . strlen($pdfData) . " bytes)\n";
} else {
    echo "Error del servidor HTTP " . $httpCode . ": " . $pdfData . "\n";
}

curl_close($ch);
