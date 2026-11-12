using System;
using System.IO;
using System.Threading.Tasks;
using ReportForge.Client;
using ReportForge.Client.Fluent;
using ReportForge.Client.Models;

namespace ReportForge.Examples
{
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("==========================================================");
            Console.WriteLine("   ReportForge .NET Client SDK - C# Typed & Fluent Demo   ");
            Console.WriteLine("==========================================================\n");

            string baseUrl = "http://localhost:8080";
            string apiKey = "rf_live_docker_demo_12345";

            using var client = new ReportForgeClient(baseUrl, apiKey);

            // -------------------------------------------------------------
            // OPCIÓN 1: Construcción usando la API Fluent (API fluida)
            // -------------------------------------------------------------
            Console.WriteLine("[1/2] Construyendo reporte con Fluent Builder (API fluida)...");

            var fluentDoc = ReportDocument.Create(page => page
                .A4()
                .Portrait()
                .Margin(20))
                .Header(header => header
                    .Text("ORDEN DE COMPRA COMERCIAL #{{ order_id }}", t => t
                        .H2()
                        .AlignCenter()
                        .Color("#1E3A8A")
                        .Bold()))
                .Content(content => content
                    .Spacing(12)
                    .Row(row => row
                        .Spacing(10)
                        .RelativeItem(2.0, c => c.Column(col => col
                            .Text("Datos del Cliente", t => t.H3().Color("#1E3A8A"))
                            .Text("Empresa: {{ client.company }}")
                            .Text("RNC: {{ client.rnc }}")
                            .Text("Contacto: {{ client.contact }}")))
                        .RelativeItem(1.0, c => c.Column(col => col
                            .Text("Detalles de Emisión", t => t.H3().Color("#1E3A8A"))
                            .Text("Fecha: {{ order_date }}")
                            .Text("Vence: {{ due_date }}")
                            .Text("Estado: {{ status }}"))))
                    .Divider("#CBD5E1", 1.0, 8.0)
                    .Table(table => table
                        .Source("items")
                        .Zebra(true)
                        .Border("#CBD5E1", 0.5)
                        .HeaderBackground("#1E3A8A")
                        .Columns(cols =>
                        {
                            cols.Column("sku", "Código").Width(70);
                            cols.Column("description", "Descripción del Producto").Flex(3.0);
                            cols.Add("qty", "Cant.", c => c.Width(50).Number().AlignCenter());
                            cols.Add("unit_price", "Precio", c => c.Width(80).Currency().AlignRight());
                            cols.Add("total", "Subtotal", c => c.Width(90).Currency().AlignRight());
                        }))
                    .Spacer(10)
                    .Row(row => row
                        .RelativeItem(1.0, c => c.Column(col => col
                            .Text("Código de Verificación Fiscal:", t => t.Caption().Italic())
                            .Barcode("OC-2026-9901-VAL", "code128", height: 35)))
                        .RelativeItem(1.0, c => c.Column(col => col
                            .Text("Subtotal: RD$ {{ totals.subtotal }}", t => t.AlignRight())
                            .Text("ITBIS (18%): RD$ {{ totals.tax }}", t => t.AlignRight())
                            .Text("TOTAL A PAGAR: RD$ {{ totals.grand_total }}", t => t.H2().Color("#1E3A8A").AlignRight().Bold())))))
                .Footer(footer => footer
                    .PageNumber("Página {page} de {total}", p => p.AlignRight().Color("#64748B")));

            // Datos dinámicos fuertemente tipados o anónimos
            var reportData = new
            {
                order_id = "OC-2026-9901",
                order_date = "12/11/2026",
                due_date = "30/11/2026",
                status = "APROBADO",
                client = new
                {
                    company = "Corporación Tecnológica del Caribe SRL",
                    rnc = "130-99887-1",
                    contact = "Lic. Carlos Mendoza"
                },
                items = new[]
                {
                    new { sku = "SRV-01", description = "Servidor Dell PowerEdge R750 32GB RAM", qty = 2, unit_price = 3850.00, total = 7700.00 },
                    new { sku = "SW-48P", description = "Switch Cisco Catalyst 9300 PoE+", qty = 3, unit_price = 1450.00, total = 4350.00 },
                    new { sku = "UPS-3K", description = "UPS APC Smart-UPS 3000VA LCD 120V", qty = 1, unit_price = 1100.00, total = 1100.00 }
                },
                totals = new
                {
                    subtotal = 13150.00,
                    tax = 2367.00,
                    grand_total = 15517.00
                }
            };

            try
            {
                Console.WriteLine("Generando PDF vía HTTP REST con el Fluent Document...");
                byte[] pdfBytes = await client.GeneratePdfAsync(fluentDoc, reportData);
                string outputPath = Path.Combine(AppContext.BaseDirectory, "orden_compra_fluent_csharp.pdf");
                await File.WriteAllBytesAsync(outputPath, pdfBytes);
                Console.WriteLine($"[✓] PDF generado con éxito ({pdfBytes.Length:N0} bytes): {outputPath}\n");

                // -------------------------------------------------------------
                // OPCIÓN 2: Construcción usando Clases Fuertemente Tipadas (POCOs)
                // -------------------------------------------------------------
                Console.WriteLine("[2/2] Construyendo reporte con Objetos Fuertemente Tipados (POCOs)...");

                var typedDoc = new DocumentDefinition
                {
                    Page = new PageSettings("Letter", "portrait", 20.0),
                    Header = new TextComponent("RESUMEN DE OPERACIONES (POCO TYPED)", style: "h2", alignment: "center", color: "#0F766E"),
                    Content = new ColumnComponent
                    {
                        Spacing = 10,
                        Items = new()
                        {
                            new TextComponent("Reporte generado con modelos puros de C# sin builders."),
                            new SpacerComponent(10),
                            new QrComponent("https://reportforge.dev/verify/OC-2026-9901", 70.0)
                        }
                    },
                    Footer = new PageNumberComponent("Página {page} de {total}", "center")
                };

                byte[] typedPdfBytes = await client.GeneratePdfAsync(typedDoc);
                string typedOutputPath = Path.Combine(AppContext.BaseDirectory, "resumen_tipado_csharp.pdf");
                await File.WriteAllBytesAsync(typedOutputPath, typedPdfBytes);
                Console.WriteLine($"[✓] PDF tipado generado con éxito ({typedPdfBytes.Length:N0} bytes): {typedOutputPath}\n");

                Console.WriteLine("¡Prueba de C# completada exitosamente!");
            }
            catch (ReportForgeApiException ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"[ERROR API HTTP {ex.StatusCode}]: {ex.Message}");
                if (!string.IsNullOrEmpty(ex.ResponseBody))
                {
                    Console.WriteLine($"Respuesta del servidor: {ex.ResponseBody}");
                }
                Console.ResetColor();
            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"[ERROR]: {ex.Message}");
                Console.ResetColor();
            }
        }
    }
}
