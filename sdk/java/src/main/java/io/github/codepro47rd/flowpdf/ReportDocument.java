package io.github.codepro47rd.flowpdf;

import io.github.codepro47rd.flowpdf.builders.ColumnBuilder;
import io.github.codepro47rd.flowpdf.builders.PageConfigBuilder;
import io.github.codepro47rd.flowpdf.builders.SingleContainerBuilder;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

public class ReportDocument {
    private final Map<String, Object> doc = new LinkedHashMap<>();

    public ReportDocument() {
        doc.put("version", "2.0");
        doc.put("page", new PageConfigBuilder().build());
        doc.put("content", new ColumnBuilder().build());
    }

    public static ReportDocument create(Consumer<PageConfigBuilder> pageConfigure) {
        ReportDocument d = new ReportDocument();
        if (pageConfigure != null) {
            d.page(pageConfigure);
        }
        return d;
    }

    public static ReportDocument create() {
        return create(null);
    }

    public ReportDocument title(String title) {
        doc.put("title", title);
        return this;
    }

    public ReportDocument author(String author) {
        doc.put("author", author);
        return this;
    }

    public ReportDocument page(Consumer<PageConfigBuilder> configure) {
        PageConfigBuilder b = new PageConfigBuilder();
        configure.accept(b);
        doc.put("page", b.build());
        return this;
    }

    public ReportDocument header(Consumer<SingleContainerBuilder> configure) {
        SingleContainerBuilder b = new SingleContainerBuilder();
        configure.accept(b);
        Map<String, Object> child = b.build();
        if (child != null) {
            doc.put("header", child);
        }
        return this;
    }

    public ReportDocument content(Consumer<ColumnBuilder> configure) {
        ColumnBuilder b = new ColumnBuilder();
        configure.accept(b);
        doc.put("content", b.build());
        return this;
    }

    public ReportDocument footer(Consumer<SingleContainerBuilder> configure) {
        SingleContainerBuilder b = new SingleContainerBuilder();
        configure.accept(b);
        Map<String, Object> child = b.build();
        if (child != null) {
            doc.put("footer", child);
        }
        return this;
    }

    @SuppressWarnings("unchecked")
    public ReportDocument addFont(String name, String path, String data) {
        List<Map<String, Object>> fonts = (List<Map<String, Object>>) doc.computeIfAbsent("fonts", k -> new java.util.ArrayList<>());
        Map<String, Object> fontDef = new LinkedHashMap<>();
        fontDef.put("name", name);
        if (path != null) fontDef.put("path", path);
        if (data != null) fontDef.put("data", data);
        fonts.add(fontDef);
        return this;
    }

    public static boolean registerFont(String fontName, byte[] fontBytes) {
        return FlowPdfEngine.registerFont(fontName, fontBytes);
    }

    public Map<String, Object> build() {
        return new LinkedHashMap<>(doc);
    }

    public String toJson() {
        return toJson(this.build());
    }

    public byte[] renderPdf(String dataJson) {
        return FlowPdfEngine.renderPdf(toJson(), dataJson);
    }

    public byte[] renderPdf() {
        return renderPdf(null);
    }

    public static String extractText(byte[] pdfBytes) {
        return FlowPdfEngine.extractText(pdfBytes);
    }

    public static String extractJson(byte[] pdfBytes, String optionsJson) {
        return FlowPdfEngine.extractJson(pdfBytes, optionsJson);
    }

    public static String toJson(Object obj) {
        if (obj == null) return "null";
        if (obj instanceof String) {
            return "\"" + escapeJson((String) obj) + "\"";
        }
        if (obj instanceof Number || obj instanceof Boolean) {
            return obj.toString();
        }
        if (obj instanceof Map) {
            StringBuilder sb = new StringBuilder("{");
            boolean first = true;
            for (Map.Entry<?, ?> entry : ((Map<?, ?>) obj).entrySet()) {
                if (entry.getValue() == null) continue;
                if (!first) sb.append(",");
                sb.append("\"").append(escapeJson(entry.getKey().toString())).append("\":");
                sb.append(toJson(entry.getValue()));
                first = false;
            }
            sb.append("}");
            return sb.toString();
        }
        if (obj instanceof Iterable) {
            StringBuilder sb = new StringBuilder("[");
            boolean first = true;
            for (Object item : (Iterable<?>) obj) {
                if (!first) sb.append(",");
                sb.append(toJson(item));
                first = false;
            }
            sb.append("]");
            return sb.toString();
        }
        return "\"" + escapeJson(obj.toString()) + "\"";
    }

    private static String escapeJson(String s) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"': sb.append("\\\""); break;
                case '\\': sb.append("\\\\"); break;
                case '\b': sb.append("\\b"); break;
                case '\f': sb.append("\\f"); break;
                case '\n': sb.append("\\n"); break;
                case '\r': sb.append("\\r"); break;
                case '\t': sb.append("\\t"); break;
                default:
                    if (c < ' ') {
                        sb.append(String.format("\\u%04x", (int) c));
                    } else {
                        sb.append(c);
                    }
            }
        }
        return sb.toString();
    }
}
