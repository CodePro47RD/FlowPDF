package io.github.codepro47rd.flowpdf;

import io.github.codepro47rd.flowpdf.exceptions.FlowPdfException;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.Map;

public class FlowPdfClient {
    private final String baseUrl;
    private final String apiKey;
    private final HttpClient client;
    private final Duration timeout;

    public FlowPdfClient(String baseUrl, String apiKey, Duration timeout) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.apiKey = apiKey;
        this.timeout = timeout != null ? timeout : Duration.ofSeconds(30);
        this.client = HttpClient.newBuilder()
            .connectTimeout(this.timeout)
            .build();
    }

    public FlowPdfClient(String baseUrl, String apiKey) {
        this(baseUrl, apiKey, Duration.ofSeconds(30));
    }

    public FlowPdfClient(String baseUrl) {
        this(baseUrl, null, Duration.ofSeconds(30));
    }

    public byte[] render(Object templateData, String format) {
        try {
            Map<String, Object> payload = new LinkedHashMap<>();
            payload.put("template", templateData instanceof ReportDocument ? ((ReportDocument) templateData).build() : templateData);
            payload.put("format", format != null ? format : "pdf");

            String jsonPayload = ReportDocument.toJson(payload);

            HttpRequest.Builder reqBuilder = HttpRequest.newBuilder()
                .uri(URI.create(baseUrl + "/api/v1/render/"))
                .header("Content-Type", "application/json")
                .header("Accept", "application/pdf, application/json")
                .header("User-Agent", "FlowPDF-Java-SDK/1.0.0")
                .timeout(timeout)
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload));

            if (apiKey != null && !apiKey.isEmpty()) {
                reqBuilder.header("X-API-Key", apiKey);
            }

            HttpResponse<byte[]> response = client.send(reqBuilder.build(), HttpResponse.BodyHandlers.ofByteArray());

            if (response.statusCode() >= 400) {
                String errorBody = new String(response.body());
                throw new FlowPdfException("FlowPDF Server Error (HTTP " + response.statusCode() + "): " + errorBody);
            }

            return response.body();
        } catch (Exception e) {
            if (e instanceof FlowPdfException) {
                throw (FlowPdfException) e;
            }
            throw new FlowPdfException("Failed to render document via HTTP: " + e.getMessage(), e);
        }
    }

    public byte[] render(Object templateData) {
        return render(templateData, "pdf");
    }
}
