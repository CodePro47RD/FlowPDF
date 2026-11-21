using System;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using FlowPdf.Client;
using FlowPdf.Fluent;
using FlowPdf.Models;
using FlowPdf.Native;

namespace FlowPdf.Examples
{
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("==================================================================");
            Console.WriteLine("    FlowPDF - .NET NuGet Package & Hybrid Engine Demo    ");
            Console.WriteLine("==================================================================\n");

            // -------------------------------------------------------------
            // VERIFICACIÓN DEL MOTOR NATIVO RUST CORE
            // -------------------------------------------------------------
            string nativeVersion = FlowPdfEngine.GetVersion();
            Console.WriteLine($"[Core] FlowPDF Native Engine Version: {nativeVersion}\n");

            // -------------------------------------------------------------
            // CONSTRUCCIÓN DEL REPORTE CON LA API FLUIDA
            // -------------------------------------------------------------
            Console.WriteLine("[1/3] Construyendo documento con Fluent Builder API...");

            var invoiceDoc = ReportDocument.Create(page => page
                .A4()
                .Portrait()
                .Margins(25, 25, 25, 25))
                .Header(header => header
                    .Text("ORDEN DE COMPRA COMERCIAL #OC-2026-9901", t => t
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
                            .Text("Empresa: Corporación Tecnológica del Caribe SRL")
                            .Text("RNC: 130-99887-1")
                            .Text("Contacto: Lic. Carlos Mendoza")))
                        .RelativeItem(1.0, c => c.Column(col => col
                            .Text("Detalles de Emisión", t => t.H3().Color("#1E3A8A"))
                            .Text("Fecha: 12/11/2026")
                            .Text("Vence: 30/11/2026")
                            .Text("Estado: APROBADO"))))
                    .Divider("#CBD5E1", 1.0, 8.0)
                    .Table(table => table
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
                        })
                        .Rows(new[]
                        {
                            new { sku = "SRV-01", description = "Servidor Dell PowerEdge R750 32GB RAM", qty = 2, unit_price = 3850.00, total = 7700.00 },
                            new { sku = "SW-48P", description = "Switch Cisco Catalyst 9300 PoE+", qty = 3, unit_price = 1450.00, total = 4350.00 },
                            new { sku = "UPS-3K", description = "UPS APC Smart-UPS 3000VA LCD 120V", qty = 1, unit_price = 1100.00, total = 1100.00 }
                        }))
                    .Spacer(10)
                    .Row(row => row
                        .RelativeItem(1.0, c => c.Column(col => col
                            .Text("Código de Verificación Fiscal:", t => t.Caption().Italic())
                            .Barcode("OC-2026-9901-VAL", "code128", height: 35)))
                        .RelativeItem(1.0, c => c.Column(col => col
                            .Text("Subtotal: RD$ 13,150.00", t => t.AlignRight())
                            .Text("ITBIS (18%): RD$ 2,367.00", t => t.AlignRight())
                            .Text("TOTAL A PAGAR: RD$ 15,517.00", t => t.H2().Color("#1E3A8A").AlignRight().Bold()))))
                    .Spacer(15)
                    .QrCode("https://example.com/verify/OC-2026-9901", 80))
                .Footer(footer => footer
                    .Text("Generado por FlowPDF - www.flowpdf.dev", t => t.AlignCenter().Color("#64748B")));

            // -------------------------------------------------------------
            // TEST 1: RENDER IN-PROCESS CON MOTOR NATIVO RUST
            // -------------------------------------------------------------
            Console.WriteLine("[2/3] Generando PDF IN-PROCESS con motor nativo Rust (flowpdf.dll)...");
            var sw = Stopwatch.StartNew();
            byte[] nativePdf = invoiceDoc.GeneratePdf();
            sw.Stop();

            string nativeOutputPath = Path.Combine(AppContext.BaseDirectory, "orden_compra_nativa_rust.pdf");
            await File.WriteAllBytesAsync(nativeOutputPath, nativePdf);
            Console.ForegroundColor = ConsoleColor.Green;
            Console.WriteLine($"[✓] PDF Nativo generado en {sw.ElapsedMilliseconds} ms ({nativePdf.Length:N0} bytes): {nativeOutputPath}");
            Console.ResetColor();

            // -------------------------------------------------------------
            // TEST 2: RENDER VÍA HTTP CLIENT (MICROSERVICIO CLOUD)
            // -------------------------------------------------------------
            Console.WriteLine("\n[3/3] Generando PDF VÍA CLIENTE HTTP REST (Microservicio Django/Celery)...");
            string baseUrl = "http://localhost:8080";
            string apiKey = "fp_live_docker_demo_12345";

            using var client = new FlowPdfClient(baseUrl, apiKey);
            try
            {
                sw.Restart();
                byte[] remotePdf = await invoiceDoc.GeneratePdfRemoteAsync(client);
                sw.Stop();

                string remoteOutputPath = Path.Combine(AppContext.BaseDirectory, "orden_compra_remota_http.pdf");
                await File.WriteAllBytesAsync(remoteOutputPath, remotePdf);
                Console.ForegroundColor = ConsoleColor.Cyan;
                Console.WriteLine($"[✓] PDF Remoto HTTP generado en {sw.ElapsedMilliseconds} ms ({remotePdf.Length:N0} bytes): {remoteOutputPath}");
                Console.ResetColor();
            }
            catch (Exception ex)
            {
                Console.ForegroundColor = ConsoleColor.Yellow;
                Console.WriteLine($"[Aviso HTTP]: No se pudo conectar al cluster remoto ({ex.Message}).");
                Console.WriteLine("El render nativo in-process funciona al 100% sin depender del servidor HTTP.");
                Console.ResetColor();
            }

            Console.WriteLine("\n==================================================================");
            Console.WriteLine("    ¡Demostración de FlowPDF para C# finalizada con éxito!    ");
            Console.WriteLine("==================================================================");
        }
    }
}
