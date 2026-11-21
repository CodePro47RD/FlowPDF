// Prueba de humo del SDK de Java (JNA): tabla agrupada con los métodos fluidos de 1.0 (groupBy, fontSize,
// padding, zebraColor, columnas auto/format), PDF real y extracción de texto.
import io.github.codepro47rd.flowpdf.ReportDocument;

import java.util.List;
import java.util.Map;

public class Smoke {
    public static void main(String[] args) {
        List<Map<String, Object>> rows = List.of(
            Map.of("categoria", "Servidores", "sku", "SRV-01", "descripcion", "Servidor 32GB RAM", "monto", 3850),
            Map.of("categoria", "Servidores", "sku", "SRV-02", "descripcion", "Servidor 64GB RAM", "monto", 5200),
            Map.of("categoria", "Redes", "sku", "SW-48P", "descripcion", "Switch 48 puertos PoE+", "monto", 1450));

        ReportDocument doc = ReportDocument.create().content(c -> c.table(t -> t
            .groupBy("categoria", "#E8F0FE", "#1F3B8A")
            .fontSize(8.5).padding(6, 4)
            .headerColor("#FFFFFF").textColor("#111827").zebraColor("#F8FAFC")
            .column("Código", "sku", col -> col.auto())
            .column("Descripción", "descripcion", col -> col.flex(1))
            .column("Monto", "monto", col -> col.auto().currency().right())
            .data(rows)));

        String text = ReportDocument.extractText(doc.renderPdf());
        for (String k : new String[] {"Servidores", "Redes", "SRV-01", "$3850.00"}) {
            if (!text.contains(k)) {
                throw new IllegalStateException("Falta \"" + k + "\" en el PDF:\n" + text);
            }
        }
        System.out.println("SDK Java: SMOKE TEST PASSED");
    }
}
