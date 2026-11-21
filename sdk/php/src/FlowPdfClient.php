<?php

namespace FlowPdf;

use FlowPdf\Exceptions\FlowPdfException;

class FlowPdfClient
{
    private string $baseUrl;
    private ?string $apiKey;
    private int $timeout;

    public function __construct(string $baseUrl = 'http://localhost:8000', ?string $apiKey = null, int $timeout = 30)
    {
        $this->baseUrl = rtrim($baseUrl, '/');
        $this->apiKey = $apiKey;
        $this->timeout = $timeout;
    }

    public function render(mixed $templateData, string $format = 'pdf', array $options = []): string
    {
        if (is_object($templateData) && method_exists($templateData, 'build')) {
            $templateData = $templateData->build();
        }

        $url = "{$this->baseUrl}/api/v1/render/";
        $payload = json_encode([
            'template' => $templateData,
            'format' => $format,
            'options' => $options
        ], JSON_UNESCAPED_UNICODE);

        $headers = [
            'Content-Type: application/json',
            'Accept: application/pdf, application/json',
            'User-Agent: FlowPDF-PHP-SDK/1.0.0'
        ];

        if ($this->apiKey) {
            $headers[] = "X-API-Key: {$this->apiKey}";
        }

        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        curl_setopt($ch, CURLOPT_TIMEOUT, $this->timeout);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $error = curl_error($ch);
        curl_close($ch);

        if ($response === false) {
            throw new FlowPdfException("FlowPDF cURL Error: {$error}");
        }

        if ($httpCode >= 400) {
            throw new FlowPdfException("FlowPDF Server Error (HTTP {$httpCode}): {$response}");
        }

        return $response;
    }
}
