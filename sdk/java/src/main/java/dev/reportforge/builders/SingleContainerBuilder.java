package dev.reportforge.builders;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.function.Consumer;

public class SingleContainerBuilder {
    private Map<String, Object> child;

    public SingleContainerBuilder text(String value, Consumer<TextBuilder> configure) {
        TextBuilder b = new TextBuilder(value);
        if (configure != null) {
            configure.accept(b);
        }
        this.child = b.build();
        return this;
    }

    public SingleContainerBuilder text(String value) {
        return text(value, null);
    }

    public SingleContainerBuilder row(Consumer<RowBuilder> configure, double spacing) {
        RowBuilder b = new RowBuilder(spacing);
        configure.accept(b);
        this.child = b.build();
        return this;
    }

    public SingleContainerBuilder row(Consumer<RowBuilder> configure) {
        return row(configure, 0.0);
    }

    public SingleContainerBuilder column(Consumer<ColumnBuilder> configure, double spacing) {
        ColumnBuilder b = new ColumnBuilder(spacing);
        configure.accept(b);
        this.child = b.build();
        return this;
    }

    public SingleContainerBuilder column(Consumer<ColumnBuilder> configure) {
        return column(configure, 0.0);
    }

    public SingleContainerBuilder table(Consumer<TableBuilder> configure) {
        TableBuilder b = new TableBuilder();
        configure.accept(b);
        this.child = b.build();
        return this;
    }

    public SingleContainerBuilder qr(String value, double size) {
        Map<String, Object> q = new LinkedHashMap<>();
        q.put("type", "qr");
        q.put("value", value);
        q.put("size", size);
        this.child = q;
        return this;
    }

    public SingleContainerBuilder qrCode(String value, double size) {
        return qr(value, size);
    }

    public SingleContainerBuilder barcode(String value) {
        Map<String, Object> bc = new LinkedHashMap<>();
        bc.put("type", "barcode");
        bc.put("value", value);
        bc.put("barcode_type", "code128");
        bc.put("width", 150.0);
        bc.put("height", 40.0);
        bc.put("include_text", true);
        this.child = bc;
        return this;
    }

    public Map<String, Object> build() {
        return child;
    }
}
