using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace FlowPdf.Models
{
    public class TextComponent : ComponentDefinition
    {
        [JsonPropertyName("value")]
        public string Value { get; set; } = string.Empty;

        [JsonPropertyName("style")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Style { get; set; }

        [JsonPropertyName("alignment")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Alignment { get; set; } = "left";

        [JsonPropertyName("color")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Color { get; set; }

        [JsonPropertyName("font_size")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? FontSize { get; set; }

        [JsonPropertyName("bold")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public bool? Bold { get; set; }

        [JsonPropertyName("italic")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public bool? Italic { get; set; }

        [JsonPropertyName("underline")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public bool? Underline { get; set; }

        [JsonPropertyName("strike")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public bool? Strike { get; set; }

        [JsonPropertyName("font")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Font { get; set; }

        public TextComponent() { }

        public TextComponent(string value, string? style = null, string? color = null, double? fontSize = null, string? alignment = null)
        {
            Value = value;
            Style = style;
            Color = color;
            FontSize = fontSize;
            Alignment = alignment;
        }
    }

    public class ContainerComponent : ComponentDefinition
    {
        [JsonPropertyName("child")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public ComponentDefinition? Child { get; set; }

        [JsonPropertyName("width")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? Width { get; set; }

        [JsonPropertyName("height")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? Height { get; set; }

        [JsonPropertyName("padding")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? Padding { get; set; }

        [JsonPropertyName("margin")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? Margin { get; set; }

        [JsonPropertyName("background")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Background { get; set; }

        [JsonPropertyName("border_color")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? BorderColor { get; set; }

        [JsonPropertyName("border_width")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? BorderWidth { get; set; }

        [JsonPropertyName("border_radius")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? BorderRadius { get; set; }

        [JsonPropertyName("alignment")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Alignment { get; set; }
    }

    public class ColumnComponent : ComponentDefinition
    {
        [JsonPropertyName("items")]
        public List<ComponentDefinition> Items { get; set; } = new();

        [JsonPropertyName("spacing")]
        public double Spacing { get; set; } = 0.0;

        public ColumnComponent() { }

        public ColumnComponent(double spacing = 0.0)
        {
            Spacing = spacing;
        }

        public ColumnComponent(IEnumerable<ComponentDefinition> items, double spacing = 0.0)
        {
            Spacing = spacing;
            Items = new List<ComponentDefinition>(items);
        }
    }

    public class RowItemDefinition
    {
        [JsonPropertyName("width")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? Width { get; set; }

        [JsonPropertyName("flex")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? Flex { get; set; } = 1.0;

        [JsonPropertyName("item")]
        public ComponentDefinition Item { get; set; } = null!;

        public RowItemDefinition() { }

        public static RowItemDefinition FromConstant(double width, ComponentDefinition item)
            => new() { Width = width, Flex = null, Item = item };

        public static RowItemDefinition FromRelative(double flex, ComponentDefinition item)
            => new() { Flex = flex, Width = null, Item = item };
    }

    public class RowComponent : ComponentDefinition
    {
        [JsonPropertyName("items")]
        public List<object> Items { get; set; } = new();

        [JsonPropertyName("spacing")]
        public double Spacing { get; set; } = 0.0;

        [JsonPropertyName("vertical_alignment")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? VerticalAlignment { get; set; } = "top";

        public RowComponent() { }

        public RowComponent(double spacing = 0.0)
        {
            Spacing = spacing;
        }
    }

    public class TableColumnDefinition
    {
        [JsonPropertyName("title")]
        public string Title { get; set; } = string.Empty;

        [JsonPropertyName("field")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Field { get; set; }

        [JsonPropertyName("width")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? Width { get; set; }

        [JsonPropertyName("flex")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? Flex { get; set; } = 1.0;

        [JsonPropertyName("format")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Format { get; set; }

        [JsonPropertyName("align")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Align { get; set; }

        /// <summary>
        /// Ancho según el contenido: el motor mide el texto más ancho de la columna (cabecera incluida) con las
        /// métricas reales de Helvetica. Su texto no se parte; las columnas flexibles toman lo que quede.
        /// </summary>
        [JsonPropertyName("auto")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingDefault)]
        public bool Auto { get; set; }

        public TableColumnDefinition() { }

        public TableColumnDefinition(string field, string title)
        {
            Field = field;
            Title = title;
        }
    }

    public class TableComponent : ComponentDefinition
    {
        [JsonPropertyName("columns")]
        public List<TableColumnDefinition> Columns { get; set; } = new();

        [JsonPropertyName("source")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Source { get; set; }

        [JsonPropertyName("data")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public List<Dictionary<string, object>>? Data { get; set; }

        [JsonPropertyName("header_background")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? HeaderBackground { get; set; }

        [JsonPropertyName("zebra")]
        public bool Zebra { get; set; } = true;

        [JsonPropertyName("border_color")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? BorderColor { get; set; }

        [JsonPropertyName("border_width")]
        public double BorderWidth { get; set; } = 0.5;

        [JsonPropertyName("repeat_header")]
        public bool RepeatHeader { get; set; } = true;

        /// <summary>Tamaño de letra de las celdas (pt). Sin él, 9 pt.</summary>
        [JsonPropertyName("font_size")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? FontSize { get; set; }

        [JsonPropertyName("padding_x")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? PaddingX { get; set; }

        [JsonPropertyName("padding_y")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? PaddingY { get; set; }

        [JsonPropertyName("header_color")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? HeaderColor { get; set; }

        [JsonPropertyName("text_color")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? TextColor { get; set; }

        [JsonPropertyName("zebra_color")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? ZebraColor { get; set; }

        /// <summary>
        /// Campo que agrupa las filas: cada vez que cambia su valor se intercala un título a todo el ancho.
        /// Las filas deben venir ordenadas por ese campo.
        /// </summary>
        [JsonPropertyName("group_by")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? GroupBy { get; set; }

        [JsonPropertyName("group_background")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? GroupBackground { get; set; }

        [JsonPropertyName("group_color")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? GroupColor { get; set; }

        public TableComponent() { }

        public TableComponent(string source)
        {
            Source = source;
        }
    }

    public class ImageComponent : ComponentDefinition
    {
        [JsonPropertyName("source")]
        public string Source { get; set; } = string.Empty;

        [JsonPropertyName("width")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? Width { get; set; }

        [JsonPropertyName("height")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? Height { get; set; }

        [JsonPropertyName("fit")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Fit { get; set; } = "contain";

        [JsonPropertyName("alignment")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Alignment { get; set; } = "center";

        public ImageComponent() { }

        public ImageComponent(string source, double? width = null, double? height = null)
        {
            Source = source;
            Width = width;
            Height = height;
        }
    }

    public class ChartComponent : ComponentDefinition
    {
        [JsonPropertyName("chart_type")]
        public string ChartType { get; set; } = "bar";

        [JsonPropertyName("title")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Title { get; set; }

        [JsonPropertyName("labels")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public object? Labels { get; set; }

        [JsonPropertyName("values")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public object? Values { get; set; }

        [JsonPropertyName("series")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public object? Series { get; set; }

        [JsonPropertyName("width")]
        public double Width { get; set; } = 400.0;

        [JsonPropertyName("height")]
        public double Height { get; set; } = 200.0;

        [JsonPropertyName("colors")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public List<string>? Colors { get; set; }

        [JsonPropertyName("theme")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Theme { get; set; }

        [JsonPropertyName("donut")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public bool? Donut { get; set; }
    }

    public class QrComponent : ComponentDefinition
    {
        [JsonPropertyName("value")]
        public string Value { get; set; } = string.Empty;

        [JsonPropertyName("size")]
        public double Size { get; set; } = 80.0;

        [JsonPropertyName("fill_color")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? FillColor { get; set; }

        [JsonPropertyName("back_color")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? BackColor { get; set; }

        public QrComponent() { }

        public QrComponent(string value, double size = 80.0)
        {
            Value = value;
            Size = size;
        }
    }

    public class BarcodeComponent : ComponentDefinition
    {
        [JsonPropertyName("value")]
        public string Value { get; set; } = string.Empty;

        [JsonPropertyName("barcode_type")]
        public string BarcodeType { get; set; } = "code128";

        [JsonPropertyName("width")]
        public double Width { get; set; } = 180.0;

        [JsonPropertyName("height")]
        public double Height { get; set; } = 50.0;

        [JsonPropertyName("include_text")]
        public bool IncludeText { get; set; } = true;

        public BarcodeComponent() { }

        public BarcodeComponent(string value, string barcodeType = "code128")
        {
            Value = value;
            BarcodeType = barcodeType;
        }
    }

    public class SpacerComponent : ComponentDefinition
    {
        [JsonPropertyName("height")]
        public double Height { get; set; } = 10.0;

        public SpacerComponent() { }

        public SpacerComponent(double height)
        {
            Height = height;
        }
    }

    public class DividerComponent : ComponentDefinition
    {
        [JsonPropertyName("thickness")]
        public double Thickness { get; set; } = 1.0;

        [JsonPropertyName("color")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Color { get; set; }

        [JsonPropertyName("margin")]
        public double Margin { get; set; } = 8.0;

        public DividerComponent() { }

        public DividerComponent(string? color = null, double thickness = 1.0, double margin = 8.0)
        {
            Color = color;
            Thickness = thickness;
            Margin = margin;
        }
    }

    public class PageNumberComponent : ComponentDefinition
    {
        [JsonPropertyName("format")]
        public string Format { get; set; } = "Página {page} de {total}";

        [JsonPropertyName("alignment")]
        public string Alignment { get; set; } = "right";

        [JsonPropertyName("style")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Style { get; set; } = "caption";

        public PageNumberComponent() { }

        public PageNumberComponent(string format = "Página {page} de {total}", string alignment = "right")
        {
            Format = format;
            Alignment = alignment;
        }
    }
}
