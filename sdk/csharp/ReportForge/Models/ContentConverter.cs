using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace ReportForge.Models
{
    /// <summary>
    /// Serializa <see cref="DocumentDefinition.Content"/> (declarado como object) siempre como
    /// <see cref="ComponentDefinition"/>, para que lleve su discriminador "type". Con el tipo declarado
    /// como object, System.Text.Json solo lo escribía según su caché de tipos: si el encabezado ya había
    /// serializado el mismo tipo de componente (p. ej. una columna), el contenido salía sin "type" y el
    /// motor no podía leer el documento.
    /// </summary>
    public sealed class ContentConverter : JsonConverter<object>
    {
        public override object? Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
            => JsonSerializer.Deserialize<JsonElement>(ref reader, options);

        public override void Write(Utf8JsonWriter writer, object value, JsonSerializerOptions options)
        {
            switch (value)
            {
                case ComponentDefinition component:
                    JsonSerializer.Serialize(writer, component, typeof(ComponentDefinition), options);
                    break;
                case IEnumerable<ComponentDefinition> components:
                    JsonSerializer.Serialize(writer, components.ToList(), typeof(List<ComponentDefinition>), options);
                    break;
                default:
                    JsonSerializer.Serialize(writer, value, value.GetType(), options);
                    break;
            }
        }
    }
}
