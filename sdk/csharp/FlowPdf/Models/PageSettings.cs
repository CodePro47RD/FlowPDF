using System.Text.Json.Serialization;

namespace FlowPdf.Models
{
    public class PageSettings
    {
        [JsonPropertyName("size")]
        public string Size { get; set; } = "A4";

        [JsonPropertyName("orientation")]
        public string Orientation { get; set; } = "portrait";

        [JsonPropertyName("margin")]
        public double Margin { get; set; } = 20.0;

        [JsonPropertyName("margin_top")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? MarginTop { get; set; }

        [JsonPropertyName("margin_bottom")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? MarginBottom { get; set; }

        [JsonPropertyName("margin_left")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? MarginLeft { get; set; }

        [JsonPropertyName("margin_right")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public double? MarginRight { get; set; }

        public PageSettings() { }

        public PageSettings(string size, string orientation = "portrait", double margin = 20.0)
        {
            Size = size;
            Orientation = orientation;
            Margin = margin;
        }
    }
}
