package io.github.codepro47rd.flowpdf.builders;

import java.util.LinkedHashMap;
import java.util.Map;

public class TableColumnBuilder {
    private final Map<String, Object> column = new LinkedHashMap<>();

    public TableColumnBuilder(String title) {
        column.put("title", title);
        column.put("flex", 1.0);
        column.put("align", "left");
    }

    public TableColumnBuilder field(String field) {
        column.put("field", field);
        return this;
    }

    public TableColumnBuilder width(double width) {
        column.put("width", width);
        return this;
    }

    public TableColumnBuilder flex(double flex) {
        column.put("flex", flex);
        return this;
    }

    public TableColumnBuilder align(String align) {
        column.put("align", align);
        return this;
    }

    public TableColumnBuilder right() { return align("right"); }
    public TableColumnBuilder center() { return align("center"); }
    public TableColumnBuilder left() { return align("left"); }

    /** Ancho según el contenido (texto más ancho de la columna, cabecera incluida). Su texto no se parte. */
    public TableColumnBuilder auto() {
        column.put("auto", true);
        return this;
    }

    /** Formateador del valor: currency, number, percentage, date, uppercase, lowercase. */
    public TableColumnBuilder format(String format) {
        column.put("format", format);
        return this;
    }

    public TableColumnBuilder currency() { return format("currency"); }
    public TableColumnBuilder number() { return format("number"); }
    public TableColumnBuilder percentage() { return format("percentage"); }
    public TableColumnBuilder date() { return format("date"); }
    public TableColumnBuilder uppercase() { return format("uppercase"); }

    public Map<String, Object> build() {
        return new LinkedHashMap<>(column);
    }
}
