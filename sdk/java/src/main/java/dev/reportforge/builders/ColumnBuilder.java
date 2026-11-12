package dev.reportforge.builders;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

public class ColumnBuilder {
    private final Map<String, Object> column = new LinkedHashMap<>();
    private final List<Map<String, Object>> items = new ArrayList<>();

    public ColumnBuilder(double spacing) {
        column.put("type", "column");
        column.put("items", items);
        column.put("spacing", spacing);
    }

    public ColumnBuilder() {
        this(0.0);
    }

    public ColumnBuilder text(String value, Consumer<TextBuilder> configure) {
        TextBuilder b = new TextBuilder(value);
        if (configure != null) {
            configure.accept(b);
        }
        items.add(b.build());
        return this;
    }

    public ColumnBuilder text(String value) {
        return text(value, null);
    }

    public ColumnBuilder spacer(double height) {
        Map<String, Object> sp = new LinkedHashMap<>();
        sp.put("type", "spacer");
        sp.put("height", height);
        items.add(sp);
        return this;
    }

    public ColumnBuilder spacer() {
        return spacer(10.0);
    }

    public ColumnBuilder divider(double thickness, String color, double margin) {
        Map<String, Object> div = new LinkedHashMap<>();
        div.put("type", "divider");
        div.put("thickness", thickness);
        div.put("margin", margin);
        if (color != null) div.put("color", color);
        items.add(div);
        return this;
    }

    public ColumnBuilder divider(double thickness, String color) {
        return divider(thickness, color, 5.0);
    }

    public ColumnBuilder divider() {
        return divider(1.0, null, 5.0);
    }

    public ColumnBuilder row(Consumer<RowBuilder> configure, double spacing) {
        RowBuilder b = new RowBuilder(spacing);
        configure.accept(b);
        items.add(b.build());
        return this;
    }

    public ColumnBuilder row(Consumer<RowBuilder> configure) {
        return row(configure, 0.0);
    }

    public ColumnBuilder table(Consumer<TableBuilder> configure) {
        TableBuilder b = new TableBuilder();
        configure.accept(b);
        items.add(b.build());
        return this;
    }

    public ColumnBuilder qr(String value, double size, String fillColor, String backColor) {
        Map<String, Object> qr = new LinkedHashMap<>();
        qr.put("type", "qr");
        qr.put("value", value);
        qr.put("size", size);
        if (fillColor != null) qr.put("fill_color", fillColor);
        if (backColor != null) qr.put("back_color", backColor);
        items.add(qr);
        return this;
    }

    public ColumnBuilder qr(String value, double size) {
        return qr(value, size, null, null);
    }

    public ColumnBuilder qrCode(String value, double size) {
        return qr(value, size);
    }

    public ColumnBuilder barcode(String value, String barcodeType, double width, double height, boolean includeText) {
        Map<String, Object> bc = new LinkedHashMap<>();
        bc.put("type", "barcode");
        bc.put("value", value);
        bc.put("barcode_type", barcodeType);
        bc.put("width", width);
        bc.put("height", height);
        bc.put("include_text", includeText);
        items.add(bc);
        return this;
    }

    public ColumnBuilder barcode(String value) {
        return barcode(value, "code128", 150.0, 40.0, true);
    }

    public ColumnBuilder container(Consumer<ContainerBuilder> configure) {
        ContainerBuilder b = new ContainerBuilder();
        configure.accept(b);
        items.add(b.build());
        return this;
    }

    public ColumnBuilder image(String source, Double width, Double height, String fit, String alignment) {
        Map<String, Object> img = new LinkedHashMap<>();
        img.put("type", "image");
        img.put("source", source);
        if (width != null) img.put("width", width);
        if (height != null) img.put("height", height);
        if (fit != null) img.put("fit", fit);
        if (alignment != null) img.put("alignment", alignment);
        items.add(img);
        return this;
    }

    public Map<String, Object> build() {
        return new LinkedHashMap<>(column);
    }
}
