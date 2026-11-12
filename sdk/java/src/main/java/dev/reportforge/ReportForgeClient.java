package dev.reportforge;

import dev.reportforge.exceptions.ReportForgeException;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.Map;

public class ReportForgeClient {
    private final String baseUrl;
    private final String apiKey;
    private final HttpClient client;
    private final Duration timeout;

    public ReportForgeClient(String baseUrl, String apiKey, Duration timeout) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.apiKey = apiKey;
        this.timeout = timeout != null ? timeout : Duration.ofSeconds(30);
        this.client = HttpClient.newBuilder()
            .connectTimeout(this.timeout)
            .build();
    }

    public ReportForgeClient(String baseUrl, String apiKey) {
        this(baseUrl, apiKey, Duration.ofSeconds(30));
    }

    public ReportForgeClient(String baseUrl) {
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
                .header("User-Agent", "ReportForge-Java-SDK/2.0.0")
                .timeout(timeout)
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload));

            if (apiKey != null && !apiKey.isEmpty()) {
                reqBuilder.header("X-API-Key", apiKey);
            }

            HttpResponse<byte[]> response = client.send(reqBuilder.build(), HttpResponse.BodyHandlers.ofByteArray());

            if (response.statusCode() >= 400) {
                String errorBody = new String(response.body());
                throw new ReportForgeException("ReportForge Server Error (HTTP " + response.statusCode() + "): " + errorBody);
            }

            return response.body();
        } catch (Exception e) {
            if (e instanceof ReportForgeException) {
                throw (ReportForgeException) e;
            }
            throw new ReportForgeException("Failed to render document via HTTP: " + e.getMessage(), e);
        }
    }

    public byte[] render(Object templateData) {
        return render(templateData, "pdf");
    }
}
