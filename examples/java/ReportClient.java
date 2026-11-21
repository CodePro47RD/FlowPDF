import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * FlowPDF Java 11+ HttpClient Integration Example.
 */
public class ReportClient {

    public static void main(String[] args) throws IOException, InterruptedException {
        String endpoint = "http://localhost:8000/api/v1/reports/generate/";
        String apiKey = "rf_live_your_tenant_api_key_here";

        String jsonPayload = """
        {
          "document": {
            "page": { "size": "A4", "orientation": "portrait", "margin": 15 },
            "header": { "type": "text", "value": "REPORTE DE INVENTARIO", "style": "h2" },
            "content": [
              { "type": "text", "value": "Almacén Central - Bodega 01", "style": "body" },
              { "type": "spacer", "height": 10 },
              {
                "type": "table",
                "source": "inventory",
                "columns": [
                  { "field": "sku", "title": "SKU", "width": 80 },
                  { "field": "name", "title": "Descripción", "flex": 2 },
                  { "field": "stock", "title": "Stock Actual", "width": 70, "format": "number", "align": "right" }
                ],
                "zebra": true
              }
            ],
            "footer": { "type": "page_number", "format": "Página {page} de {total}", "alignment": "right" }
          },
          "data": {
            "inventory": [
              { "sku": "MOD-001", "name": "Módulo de Memoria RAM 32GB DDR5", "stock": 140 },
              { "sku": "MOD-002", "name": "Disco Sólido NVMe 2TB Gen4", "stock": 85 }
            ]
          },
          "format": "pdf",
          "response_type": "binary"
        }
        """;

        HttpClient httpClient = HttpClient.newHttpClient();

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(endpoint))
                .header("Content-Type", "application/json")
                .header("X-API-Key", apiKey)
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        System.out.println("Enviando petición HTTP desde Java...");
        HttpResponse<byte[]> response = httpClient.send(request, HttpResponse.BodyHandlers.ofByteArray());

        if (response.statusCode() == 200) {
            Path outputPath = Paths.get("inventario_java.pdf");
            Files.write(outputPath, response.body());
            System.out.println("Documento guardado con éxito: " + outputPath.toAbsolutePath());
        } else {
            System.err.println("Error HTTP " + response.statusCode() + ": " + new String(response.body()));
        }
    }
}
