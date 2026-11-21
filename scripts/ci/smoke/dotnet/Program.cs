// Prueba de humo del paquete NuGet: carga el motor nativo empaquetado, genera un PDF
// y lo vuelve a leer. Sale con código != 0 si algo falla.
using System.Runtime.InteropServices;
using ReportForge.Fluent;
using ReportForge.Native;

const string Marker = "ReportForge smoke test OK";

Console.WriteLine($"Plataforma: {RuntimeInformation.OSDescription} ({RuntimeInformation.ProcessArchitecture})");
string engineVersion = ReportForgeEngine.GetVersion();
Console.WriteLine($"Motor nativo: {engineVersion}");
// El motor debe ser el compilado para esta versión del paquete (no un binario viejo)
string? expected = typeof(ReportDocument).Assembly
    .GetCustomAttributes(typeof(System.Reflection.AssemblyInformationalVersionAttribute), false)
    .OfType<System.Reflection.AssemblyInformationalVersionAttribute>().FirstOrDefault()?.InformationalVersion?.Split('+')[0];
if (expected is not null && !engineVersion.EndsWith("v" + expected))
    throw new Exception($"Versión del motor ({engineVersion}) no coincide con la del paquete ({expected})");

var doc = ReportDocument.Create(page => page.A4().Portrait().Margins(25, 25, 25, 25))
    .Header(h => h.Text(Marker, t => t.H2().Bold()))
    .Content(c => c
        .Text("Acentos: áéíóú ñ Ñ ¿¡ €")
        .Table(table => table
            .Columns(cols =>
            {
                cols.Column("sku", "Código").Width(70);
                cols.Column("qty", "Cant.").Width(50);
            })
            .Rows(new[] { new { sku = "A-1", qty = 2 }, new { sku = "B-2", qty = 5 } }))
        .Barcode("SMOKE-001", "code128", height: 30));

byte[] pdf = doc.GeneratePdf();
if (pdf.Length < 500 || !System.Text.Encoding.ASCII.GetString(pdf, 0, 5).StartsWith("%PDF"))
    throw new Exception($"PDF inválido ({pdf.Length} bytes)");

string outPath = Path.Combine(AppContext.BaseDirectory, "smoke.pdf");
File.WriteAllBytes(outPath, pdf);
Console.WriteLine($"PDF generado: {pdf.Length:N0} bytes -> {outPath}");

string text = ReportDocument.ExtractText(pdf);
if (!text.Contains(Marker))
    throw new Exception($"El texto extraído no contiene el marcador. Extraído:\n{text}");
Console.WriteLine("Extracción de texto: OK");
Console.WriteLine("SMOKE TEST PASSED");
