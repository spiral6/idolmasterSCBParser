using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CsvHelper.Configuration.Attributes;

namespace dialogue_JSONandCSVparser.Deserialization.CSV
{
    public class DialogueInformation
    {
        [Name("File")]
        public string FileName { get; set; }

        [Name("Message ID")]
        public int FileID { get; set; }

        [Name("Message (raw)")]
        public string DialogueLine { get; set; }

        [Name("Char Count")]
        public int CharCount { get; set; }

    }
}
