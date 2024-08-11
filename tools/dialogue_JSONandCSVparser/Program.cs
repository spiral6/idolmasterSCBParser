using CsvHelper;
using CsvHelper.Configuration;
using dialogue_JSONandCSVparser.Deserialization.CSV;
using dialogue_JSONandCSVparser.Deserialization.Json;
using System.Diagnostics;
using System.Globalization;
using System.Text.Json;

public class Program
{
    public static void Main(string[] args)
    {
        try
        {
            if(args.Length != 1 && !Debugger.IsAttached) 
            {
                throw new Exception("A single path must be inputted");
            }
            else
            {
                var dir = new DirectoryInfo(args[0]);
                //var dir = new DirectoryInfo("C:\\Users\\kentw\\source\\repos\\dialogue_JSONandCSVparser\\InputFiles\\");
                if (!dir.Exists) throw new Exception("directory must exist");

                var dialogueFiles = GetDialogueFiles(dir);
                FormatCSVValues(dialogueFiles);
                WriteCSV(dialogueFiles, dir);
            }

        }catch(Exception ex)
        {
            Console.WriteLine($"Program ran into a fucky wucky: {ex.Message}\n{ex.StackTrace}");
        }
        finally
        {
            Console.WriteLine("Program finished.");
            // Console.ReadKey();
        }
    }
    
    private static void WriteCSV(List<Dialogue> dialogueFiles, DirectoryInfo dir)
    {
        using var writer = new StreamWriter(Path.Combine(dir.FullName, "combineddialogue.csv"));
        //using var writer = new StreamWriter("C:\\Users\\kentw\\source\\repos\\dialogue_JSONandCSVparser\\OutputFiles\\dialogue.csv");
        using var csv = new CsvWriter(writer, new CsvConfiguration(CultureInfo.InvariantCulture)
        {
            ShouldQuote = (field) => true
        });

        csv.WriteHeader<DialogueInformation>();
        csv.NextRecord();

        foreach(Dialogue dialogue in dialogueFiles)
        {
            int i = 0;
            foreach(string line in dialogue.Strings)
            {
                csv.WriteField(dialogue.FileName);
                csv.WriteField(i++);
                csv.WriteField($@"{line}");
                csv.WriteField(line.Length);

                csv.NextRecord();
            }
        }
    }

    private static void FormatCSVValues(List<Dialogue> dialogueFiles)
    {
        foreach (Dialogue dialogue in dialogueFiles)
        {
            dialogue.FileName = dialogue.FileName.Substring(0, dialogue.FileName.IndexOf(".dec.culledIV"));
            dialogue.Strings = dialogue.Strings.Select(s => s.Replace("\0", string.Empty)).ToList().ToList();
            dialogue.Strings = dialogue.Strings.Select(s => s.Replace("\n", "\\n")).ToList().ToList();
        }
    }

    private static List<Dialogue> GetDialogueFiles(DirectoryInfo dir)
    {
        var files = dir.GetFiles("*culledIV.json");
        var result = new List<Dialogue>();

        foreach ( var file in files)
        {
            using var reader = new StreamReader(file.FullName);

            result.Add(JsonSerializer.Deserialize<Dialogue>(reader.ReadToEnd()));
        }

        return result;
    }
}