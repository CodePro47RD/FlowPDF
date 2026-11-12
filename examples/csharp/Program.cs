using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

namespace ReportForge.Examples
{
    class Program
    {
        private static readonly HttpClient client = new HttpClient();

        static async Task Main(string[] args)
        {
            string baseUrl = "http://localhost:8000/api/v1/reports/generate/";
            string apiKey = "rf_live_your_tenant_api_key_here";

            var payload = new
            {
                document = new
                {
                    page = new { size = "A4", orientation = "portrait", margin = 15 },
                    header = new
                    {
                        type = "text",
                        value = "ORDEN DE COMPRA #{{ order_id }}",
                        style = "h2"
                    },
                    content = new object[]
                    {
                        new
                        {
                            type = "text",
                            value = "Proveedor: {{ vendor_name }} | Fecha: {{ order_date }}",
                            style = "body"
                        },
                        new { type = "spacer", height = 10 },
                        new
                        {
                            type = "table",
                            source = "items",
                            columns = new[]
                            {
                                new { field = "code", title = "Código", width = 80 },
                                new { field = "name", title = "Artículo", flex = 2 },
                                new { field = "qty", title = "Cant.", width = 50, format = "number" },
                                new { field = "cost", title = "Costo", width = 80, format = "currency", align = "right" }
                            },
                            zebra = true
                        }
                    },
                    footer = new
                    {
                        type = "page_number",
                        format = "Página {page} de {total}",
                        alignment = "right"
                    }
                },
                data = new
                {
                    order_id = "OC-2026-8801",
                    vendor_name = "Distribuidora Internacional",
                    order_date = "2026-11-12",
                    items = new[]
                    {
                        new { code = "ART-01", name = "Servidores Rack 2U", qty = 4, cost = 2500.00 },
                        new { code = "ART-02", name = "Switch Gestionable 48 Puertos", qty = 2, cost = 850.00 }
                    }
                },
                format = "pdf",
                response_type = "binary"
            };

            var jsonContent = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json"
            );

            client.DefaultRequestHeaders.Clear();
            client.DefaultRequestHeaders.Add("X-API-Key", apiKey);

            Console.WriteLine("Enviando petición a ReportForge desde C# (.NET)...");
            HttpResponseMessage response = await client.PostAsync(baseUrl, jsonContent);

            if (response.IsSuccessStatusCode)
            {
                byte[] pdfBytes = await response.Content.ReadAsByteArrayAsync();
                string outputFile = "orden_compra_csharp.pdf";
                await File.WriteAllBytesAsync(outputFile, pdfBytes);
                Console.WriteLine($"PDF guardado exitosamente: {outputFile} ({pdfBytes.Length} bytes)");
            }
            else
            {
                string error = await response.Content.ReadAsStringAsync();
                Console.WriteLine($"Error ({response.StatusCode}): {error}");
            }
        }
    }
}
