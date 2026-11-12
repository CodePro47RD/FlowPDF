package dev.reportforge.builders;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

public class RowBuilder {
    private final Map<String, Object> row = new LinkedHashMap<>();
    private final List<Map<String, Object>> items = new ArrayList<>();

    public RowBuilder(double spacing) {
        row.put("type", "row");
        row.put("items", items);
        row.put("spacing", spacing);
    }

    public RowBuilder() {
        this(0.0);
    }

    public RowBuilder item(Map<String, Object> component, Double width, Double flex) {
        Map<String, Object> itemWrapper = new LinkedHashMap<>();
        if (width != null) itemWrapper.put("width", width);
        if (flex != null) itemWrapper.put("flex", flex);
        itemWrapper.put("item", component);
        items.add(itemWrapper);
        return this;
    }

    public RowBuilder column(Consumer<ColumnBuilder> configure, Double width, Double flex) {
        ColumnBuilder col = new ColumnBuilder();
        configure.accept(col);
        return item(col.build(), width, flex);
    }

    public RowBuilder column(Consumer<ColumnBuilder> configure) {
        return column(configure, null, 1.0);
    }

    public Map<String, Object> build() {
        return new LinkedHashMap<>(row);
    }
}
