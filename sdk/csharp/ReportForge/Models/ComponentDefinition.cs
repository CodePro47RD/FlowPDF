using System.Text.Json.Serialization;

namespace ReportForge.Models
{
    [JsonPolymorphic(TypeDiscriminatorPropertyName = "type")]
    [JsonDerivedType(typeof(TextComponent), "text")]
    [JsonDerivedType(typeof(ContainerComponent), "container")]
    [JsonDerivedType(typeof(ColumnComponent), "column")]
    [JsonDerivedType(typeof(RowComponent), "row")]
    [JsonDerivedType(typeof(TableComponent), "table")]
    [JsonDerivedType(typeof(ImageComponent), "image")]
    [JsonDerivedType(typeof(ChartComponent), "chart")]
    [JsonDerivedType(typeof(QrComponent), "qr")]
    [JsonDerivedType(typeof(BarcodeComponent), "barcode")]
    [JsonDerivedType(typeof(SpacerComponent), "spacer")]
    [JsonDerivedType(typeof(DividerComponent), "divider")]
    [JsonDerivedType(typeof(PageNumberComponent), "page_number")]
    public abstract class ComponentDefinition
    {
    }
}
