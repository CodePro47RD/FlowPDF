package io.github.codepro47rd.flowpdf.builders;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

public class TableBuilder {
    private final Map<String, Object> table = new LinkedHashMap<>();
    private final List<Map<String, Object>> columns = new ArrayList<>();

    public TableBuilder() {
        table.put("type", "table");
        table.put("columns", columns);
        table.put("zebra", true);
        table.put("repeat_header", true);
    }

    public TableBuilder column(String title, String field, Consumer<TableColumnBuilder> configure) {
        TableColumnBuilder b = new TableColumnBuilder(title);
        if (field != null) {
            b.field(field);
        }
        if (configure != null) {
            configure.accept(b);
        }
        columns.add(b.build());
        return this;
    }

    public TableBuilder column(String title, String field) {
        return column(title, field, null);
    }

    public TableBuilder column(String title, Consumer<TableColumnBuilder> configure) {
        return column(title, null, configure);
    }

    public TableBuilder source(String expression) {
        table.put("source", expression);
        return this;
    }

    public TableBuilder data(List<Map<String, Object>> rows) {
        table.put("data", rows);
        return this;
    }

    public TableBuilder rows(List<Map<String, Object>> rows) {
        return data(rows);
    }

    public TableBuilder headerBackground(String color) {
        table.put("header_background", color);
        return this;
    }

    public TableBuilder zebra(boolean enabled) {
        table.put("zebra", enabled);
        return this;
    }

    public TableBuilder border(String color, double width) {
        table.put("border_color", color);
        table.put("border_width", width);
        return this;
    }

    public Map<String, Object> build() {
        return new LinkedHashMap<>(table);
    }
}
