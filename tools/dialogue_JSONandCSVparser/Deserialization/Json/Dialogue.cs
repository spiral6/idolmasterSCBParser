using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace dialogue_JSONandCSVparser.Deserialization.Json
{
    public class Dialogue
    {
        [JsonPropertyName("filename")]
        public string FileName { get; set; }

        [JsonPropertyName("strings")]
        public List<string> Strings { get; set; }

    }
}
