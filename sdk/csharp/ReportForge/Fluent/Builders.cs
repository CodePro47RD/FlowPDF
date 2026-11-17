using System;
using System.Collections.Generic;
using ReportForge.Models;

namespace ReportForge.Fluent
{
    public class SingleContainerBuilder
    {
        private ComponentDefinition? _component;

        public SingleContainerBuilder Component(ComponentDefinition component)
        {
            _component = component;
            return this;
        }

        public SingleContainerBuilder Text(string value, Action<TextBuilder>? configure = null)
        {
            var builder = new TextBuilder(value);
            configure?.Invoke(builder);
            _component = builder.Build();
            return this;
        }

        public SingleContainerBuilder Image(string source, double? width = null, double? height = null, string fit = "contain", string alignment = "center")
        {
            _component = new ImageComponent(source, width, height) { Fit = fit, Alignment = alignment };
            return this;
        }

        public SingleContainerBuilder Qr(string value, double size = 80.0, string? fillColor = null, string? backColor = null)
        {
            _component = new QrComponent(value, size) { FillColor = fillColor, BackColor = backColor };
            return this;
        }

        public SingleContainerBuilder QrCode(string value, double size = 80.0, string? fillColor = null, string? backColor = null)
            => Qr(value, size, fillColor, backColor);

        public SingleContainerBuilder Barcode(string value, string barcodeType = "code128", double width = 180.0, double height = 50.0, bool includeText = true)
        {
            _component = new BarcodeComponent(value, barcodeType) { Width = width, Height = height, IncludeText = includeText };
            return this;
        }

        public SingleContainerBuilder PageNumber(string format = "Página {page} de {total}", Action<PageNumberBuilder>? configure = null)
        {
            var builder = new PageNumberBuilder(format);
            configure?.Invoke(builder);
            _component = builder.Build();
            return this;
        }

        public SingleContainerBuilder Table(Action<TableBuilder> configure)
        {
            var builder = new TableBuilder();
            configure(builder);
            _component = builder.Build();
            return this;
        }

        public SingleContainerBuilder Chart(string chartType, Action<ChartBuilder> configure)
        {
            var builder = new ChartBuilder(chartType);
            configure(builder);
            _component = builder.Build();
            return this;
        }

        public SingleContainerBuilder Column(Action<ColumnBuilder> configure)
        {
            var builder = new ColumnBuilder();
            configure(builder);
            _component = builder.Build();
            return this;
        }

        public SingleContainerBuilder Row(Action<RowBuilder> configure)
        {
            var builder = new RowBuilder();
            configure(builder);
            _component = builder.Build();
            return this;
        }

        public SingleContainerBuilder Container(Action<ContainerBuilder> configure)
        {
            var builder = new ContainerBuilder();
            configure(builder);
            _component = builder.Build();
            return this;
        }

        public ComponentDefinition Build() => _component ?? new TextComponent(string.Empty);
    }

    public class ColumnBuilder
    {
        private readonly ColumnComponent _column = new();

        public ColumnBuilder Spacing(double spacing)
        {
            _column.Spacing = spacing;
            return this;
        }

        public ColumnBuilder Add(ComponentDefinition component)
        {
            _column.Items.Add(component);
            return this;
        }

        public ColumnBuilder Text(string value, Action<TextBuilder>? configure = null)
        {
            var builder = new TextBuilder(value);
            configure?.Invoke(builder);
            _column.Items.Add(builder.Build());
            return this;
        }

        public ColumnBuilder Spacer(double height = 10.0)
        {
            _column.Items.Add(new SpacerComponent(height));
            return this;
        }

        public ColumnBuilder Divider(string? color = null, double thickness = 1.0, double margin = 8.0)
        {
            _column.Items.Add(new DividerComponent(color, thickness, margin));
            return this;
        }

        public ColumnBuilder Image(string source, double? width = null, double? height = null, string fit = "contain", string alignment = "center")
        {
            _column.Items.Add(new ImageComponent(source, width, height) { Fit = fit, Alignment = alignment });
            return this;
        }

        public ColumnBuilder Table(Action<TableBuilder> configure)
        {
            var builder = new TableBuilder();
            configure(builder);
            _column.Items.Add(builder.Build());
            return this;
        }

        public ColumnBuilder Row(Action<RowBuilder> configure)
        {
            var builder = new RowBuilder();
            configure(builder);
            _column.Items.Add(builder.Build());
            return this;
        }

        public ColumnBuilder Column(Action<ColumnBuilder> configure)
        {
            var builder = new ColumnBuilder();
            configure(builder);
            _column.Items.Add(builder.Build());
            return this;
        }

        public ColumnBuilder Chart(string chartType, Action<ChartBuilder> configure)
        {
            var builder = new ChartBuilder(chartType);
            configure(builder);
            _column.Items.Add(builder.Build());
            return this;
        }

        public ColumnBuilder Qr(string value, double size = 80.0, string? fillColor = null, string? backColor = null)
        {
            _column.Items.Add(new QrComponent(value, size) { FillColor = fillColor, BackColor = backColor });
            return this;
        }

        public ColumnBuilder QrCode(string value, double size = 80.0, string? fillColor = null, string? backColor = null)
            => Qr(value, size, fillColor, backColor);

        public ColumnBuilder Barcode(string value, string barcodeType = "code128", double width = 180.0, double height = 50.0, bool includeText = true)
        {
            _column.Items.Add(new BarcodeComponent(value, barcodeType) { Width = width, Height = height, IncludeText = includeText });
            return this;
        }

        public ColumnBuilder PageNumber(string format = "Página {page} de {total}", Action<PageNumberBuilder>? configure = null)
        {
            var builder = new PageNumberBuilder(format);
            configure?.Invoke(builder);
            _column.Items.Add(builder.Build());
            return this;
        }

        public ColumnBuilder Container(Action<ContainerBuilder> configure)
        {
            var builder = new ContainerBuilder();
            configure(builder);
            _column.Items.Add(builder.Build());
            return this;
        }

        public ColumnComponent Build() => _column;
    }

    public class RowBuilder
    {
        private readonly RowComponent _row = new();

        public RowBuilder Spacing(double spacing)
        {
            _row.Spacing = spacing;
            return this;
        }

        public RowBuilder VerticalAlignment(string alignment)
        {
            _row.VerticalAlignment = alignment;
            return this;
        }

        public RowBuilder ConstantItem(double width, ComponentDefinition component)
        {
            _row.Items.Add(RowItemDefinition.FromConstant(width, component));
            return this;
        }

        public RowBuilder ConstantItem(double width, Action<SingleContainerBuilder> configure)
        {
            var builder = new SingleContainerBuilder();
            configure(builder);
            _row.Items.Add(RowItemDefinition.FromConstant(width, builder.Build()));
            return this;
        }

        public RowBuilder RelativeItem(double flex, ComponentDefinition component)
        {
            _row.Items.Add(RowItemDefinition.FromRelative(flex, component));
            return this;
        }

        public RowBuilder RelativeItem(double flex, Action<SingleContainerBuilder> configure)
        {
            var builder = new SingleContainerBuilder();
            configure(builder);
            _row.Items.Add(RowItemDefinition.FromRelative(flex, builder.Build()));
            return this;
        }

        public RowComponent Build() => _row;
    }

    public class TextBuilder
    {
        private readonly TextComponent _text;

        public TextBuilder(string value)
        {
            _text = new TextComponent(value);
        }

        public TextBuilder Style(string style) { _text.Style = style; return this; }
        public TextBuilder H1() => Style("h1");
        public TextBuilder H2() => Style("h2");
        public TextBuilder H3() => Style("h3");
        public TextBuilder Body() => Style("body");
        public TextBuilder Caption() => Style("caption");

        public TextBuilder Color(string hexColor) { _text.Color = hexColor; return this; }
        public TextBuilder FontSize(double size) { _text.FontSize = size; return this; }
        public TextBuilder Align(string align) { _text.Alignment = align; return this; }
        public TextBuilder AlignLeft() => Align("left");
        public TextBuilder AlignCenter() => Align("center");
        public TextBuilder AlignRight() => Align("right");
        public TextBuilder Justify() => Align("justify");

        public TextBuilder Bold(bool bold = true) { _text.Bold = bold; return this; }
        public TextBuilder Italic(bool italic = true) { _text.Italic = italic; return this; }
        public TextBuilder Underline(bool underline = true) { _text.Underline = underline; return this; }
        public TextBuilder Strike(bool strike = true) { _text.Strike = strike; return this; }
        public TextBuilder Font(string fontName) { _text.Font = fontName; return this; }

        public TextComponent Build() => _text;
    }

    public class TableBuilder
    {
        private readonly TableComponent _table = new();

        public TableBuilder Source(string source)
        {
            _table.Source = source;
            return this;
        }

        public TableBuilder Zebra(bool zebra = true)
        {
            _table.Zebra = zebra;
            return this;
        }

        public TableBuilder HeaderBackground(string color)
        {
            _table.HeaderBackground = color;
            return this;
        }

        public TableBuilder Border(string color = "#E2E8F0", double width = 0.5)
        {
            _table.BorderColor = color;
            _table.BorderWidth = width;
            return this;
        }

        public TableBuilder RepeatHeader(bool repeat = true)
        {
            _table.RepeatHeader = repeat;
            return this;
        }

        public TableBuilder Columns(Action<TableColumnsBuilder> configure)
        {
            var builder = new TableColumnsBuilder();
            configure(builder);
            _table.Columns = builder.Build();
            return this;
        }

        public TableBuilder Rows(System.Collections.IEnumerable rows)
        {
            var json = System.Text.Json.JsonSerializer.Serialize(rows);
            _table.Data = System.Text.Json.JsonSerializer.Deserialize<List<Dictionary<string, object>>>(json);
            return this;
        }

        public TableBuilder Data(List<Dictionary<string, object>> data)
        {
            _table.Data = data;
            return this;
        }

        public TableComponent Build() => _table;
    }

    public class TableColumnsBuilder
    {
        private readonly List<TableColumnDefinition> _columns = new();

        public TableColumnsBuilder Add(string field, string title, Action<TableColumnBuilder>? configure = null)
        {
            var col = new TableColumnDefinition(field, title);
            var builder = new TableColumnBuilder(this, col);
            configure?.Invoke(builder);
            _columns.Add(col);
            return this;
        }

        public TableColumnBuilder Column(string field, string title)
        {
            var col = new TableColumnDefinition(field, title);
            _columns.Add(col);
            return new TableColumnBuilder(this, col);
        }

        public List<TableColumnDefinition> Build() => _columns;
    }

    public class TableColumnBuilder
    {
        private readonly TableColumnsBuilder _parent;
        private readonly TableColumnDefinition _col;

        public TableColumnBuilder(TableColumnsBuilder parent, TableColumnDefinition col)
        {
            _parent = parent;
            _col = col;
        }

        public TableColumnBuilder Width(double width) { _col.Width = width; return this; }
        public TableColumnBuilder Flex(double flex) { _col.Flex = flex; return this; }
        public TableColumnBuilder Format(string format) { _col.Format = format; return this; }
        public TableColumnBuilder Currency() => Format("currency");
        public TableColumnBuilder Number() => Format("number");
        public TableColumnBuilder Percentage() => Format("percentage");
        public TableColumnBuilder Date() => Format("date");
        public TableColumnBuilder Uppercase() => Format("uppercase");

        public TableColumnBuilder Align(string align) { _col.Align = align; return this; }
        public TableColumnBuilder AlignLeft() => Align("left");
        public TableColumnBuilder AlignCenter() => Align("center");
        public TableColumnBuilder AlignRight() => Align("right");

        public TableColumnBuilder Column(string field, string title) => _parent.Column(field, title);
    }

    public class ChartBuilder
    {
        private readonly ChartComponent _chart;

        public ChartBuilder(string chartType)
        {
            _chart = new ChartComponent { ChartType = chartType };
        }

        public ChartBuilder Title(string title) { _chart.Title = title; return this; }
        public ChartBuilder Labels(params string[] labels) { _chart.Labels = new List<string>(labels); return this; }
        public ChartBuilder Values(params double[] values) { _chart.Values = new List<double>(values); return this; }
        public ChartBuilder Size(double width, double height) { _chart.Width = width; _chart.Height = height; return this; }
        public ChartBuilder Colors(params string[] colors) { _chart.Colors = new List<string>(colors); return this; }
        public ChartBuilder Theme(string theme) { _chart.Theme = theme; return this; }
        public ChartBuilder Light() => Theme("light");
        public ChartBuilder Dark() => Theme("dark");
        public ChartBuilder Donut(bool donut = true) { _chart.Donut = donut; return this; }

        public ChartComponent Build() => _chart;
    }

    public class ContainerBuilder
    {
        private readonly ContainerComponent _container = new();

        public ContainerBuilder Width(double width) { _container.Width = width; return this; }
        public ContainerBuilder Height(double height) { _container.Height = height; return this; }
        public ContainerBuilder Padding(double padding) { _container.Padding = padding; return this; }
        public ContainerBuilder Margin(double margin) { _container.Margin = margin; return this; }
        public ContainerBuilder Background(string color) { _container.Background = color; return this; }
        public ContainerBuilder BorderColor(string color) { _container.BorderColor = color; return this; }
        public ContainerBuilder BorderWidth(double width) { _container.BorderWidth = width; return this; }
        public ContainerBuilder BorderRadius(double radius) { _container.BorderRadius = radius; return this; }
        public ContainerBuilder Align(string alignment) { _container.Alignment = alignment; return this; }

        public ContainerBuilder Child(ComponentDefinition component)
        {
            _container.Child = component;
            return this;
        }

        public ContainerBuilder Child(Action<SingleContainerBuilder> configure)
        {
            var builder = new SingleContainerBuilder();
            configure(builder);
            _container.Child = builder.Build();
            return this;
        }

        public ContainerComponent Build() => _container;
    }

    public class PageNumberBuilder
    {
        private readonly PageNumberComponent _pageNumber;

        public PageNumberBuilder(string format)
        {
            _pageNumber = new PageNumberComponent(format);
        }

        public PageNumberBuilder Align(string align) { _pageNumber.Alignment = align; return this; }
        public PageNumberBuilder AlignLeft() => Align("left");
        public PageNumberBuilder AlignCenter() => Align("center");
        public PageNumberBuilder AlignRight() => Align("right");
        public PageNumberBuilder Style(string style) { _pageNumber.Style = style; return this; }
        public PageNumberBuilder Color(string hexColor) { return this; }

        public PageNumberComponent Build() => _pageNumber;
    }
}
