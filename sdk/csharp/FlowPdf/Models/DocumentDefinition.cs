using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace FlowPdf.Models
{
    public class DocumentDefinition
    {
        [JsonPropertyName("page")]
        public PageSettings Page { get; set; } = new();

        [JsonPropertyName("header")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public ComponentDefinition? Header { get; set; }

        [JsonPropertyName("content")]
        [JsonConverter(typeof(ContentConverter))]
        public object Content { get; set; } = new List<ComponentDefinition>();

        [JsonPropertyName("footer")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public ComponentDefinition? Footer { get; set; }

        [JsonPropertyName("metadata")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public Dictionary<string, object>? Metadata { get; set; }

        [JsonPropertyName("fonts")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public List<CustomFontDefinition>? Fonts { get; set; }
    }

    public class CustomFontDefinition
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("path")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Path { get; set; }

        [JsonPropertyName("data")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Data { get; set; }
    }

    public class ReportPayload
    {
        [JsonPropertyName("template")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public string? Template { get; set; }

        [JsonPropertyName("document")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public DocumentDefinition? Document { get; set; }

        [JsonPropertyName("data")]
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public object? Data { get; set; }

        [JsonPropertyName("format")]
        public string Format { get; set; } = "pdf";

        [JsonPropertyName("response_type")]
        public string ResponseType { get; set; } = "binary";
    }

    public class ReportJobResponse
    {
        [JsonPropertyName("job_id")]
        public string JobId { get; set; } = string.Empty;

        [JsonPropertyName("status")]
        public string Status { get; set; } = string.Empty;

        [JsonPropertyName("format")]
        public string Format { get; set; } = "pdf";

        [JsonPropertyName("download_url")]
        public string? DownloadUrl { get; set; }

        [JsonPropertyName("error_message")]
        public string? ErrorMessage { get; set; }

        [JsonPropertyName("created_at")]
        public string? CreatedAt { get; set; }

        [JsonPropertyName("completed_at")]
        public string? CompletedAt { get; set; }
    }
}
