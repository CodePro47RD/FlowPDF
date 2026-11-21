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

    public Map<String, Object> build() {
        return new LinkedHashMap<>(column);
    }
}
