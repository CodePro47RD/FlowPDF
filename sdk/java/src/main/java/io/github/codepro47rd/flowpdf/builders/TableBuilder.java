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

    public TableBuilder repeatHeader(boolean enabled) {
        table.put("repeat_header", enabled);
        return this;
    }

    /** Tamaño de letra de las celdas (pt). Por defecto 9. */
    public TableBuilder fontSize(double size) {
        table.put("font_size", size);
        return this;
    }

    /** Relleno de cada celda (pt): horizontal y vertical. Por defecto 8 y 5.5. */
    public TableBuilder padding(double horizontal, double vertical) {
        table.put("padding_x", horizontal);
        table.put("padding_y", vertical);
        return this;
    }

    /** Color del texto de la cabecera. */
    public TableBuilder headerColor(String color) {
        table.put("header_color", color);
        return this;
    }

    /** Color del texto de las celdas. */
    public TableBuilder textColor(String color) {
        table.put("text_color", color);
        return this;
    }

    /** Filas alternas con fondo de este color (activa zebra). */
    public TableBuilder zebraColor(String color) {
        table.put("zebra", true);
        table.put("zebra_color", color);
        return this;
    }

    /**
     * Agrupa las filas por un campo: cada vez que cambia su valor se intercala un título a todo el ancho
     * (las filas deben venir ordenadas por ese campo).
     */
    public TableBuilder groupBy(String field, String background, String color) {
        table.put("group_by", field);
        if (background != null) {
            table.put("group_background", background);
        }
        if (color != null) {
            table.put("group_color", color);
        }
        return this;
    }

    public TableBuilder groupBy(String field) {
        return groupBy(field, null, null);
    }

    public Map<String, Object> build() {
        return new LinkedHashMap<>(table);
    }
}
