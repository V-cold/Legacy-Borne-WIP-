//This is an auxilary scrip that pulls TPI data from data.win which is used to mark sprites on texture maps
//It is called in the Extracting Texteure Map section of roots.py
//This code was written heavily assisted by AI. If you could understandingly check for errors before including it in your
//reused code, then send me a message if issues persist, I would be grateful. If you can additionally message me
//if you find any errors, I will happily update the code.

//Librarbys :)
using System;
using System.IO;
using System.Text;
using UndertaleModLib;
using UndertaleModLib.Models;


//Error handling
if (Data?.Sprites == null)
{
    throw new InvalidDataException("GameMaker data tree is loaded but the Sprites collection is empty or null."); //to be captured by stderr=subprocess.PIPE
}

string directory = Path.GetDirectoryName(FilePath);
if (string.IsNullOrEmpty(directory))
{
    throw new DirectoryNotFoundException("Could not resolve target directory from data.win file path."); //to be captured by stderr=subprocess.PIPE
}

string outputPath = Path.Combine(directory, "texture_metadata_map.csv");

StringBuilder csvData = new StringBuilder();

//Main code
// Write the CSV header defining our layout geometry
csvData.AppendLine("SpriteName,FrameIndex,TexturePage,SourceX,SourceY,Width,Height,OffsetX,OffsetY");

int exportedCount = 0;

// Iterate through every sprite in the GameMaker data tree
foreach (var sprite in Data.Sprites)
{
    if (sprite?.Textures == null || string.IsNullOrEmpty(sprite.Name?.Content)) continue;

    // A sprite can have multiple frames (textures) for animations
    for (int i = 0; i < sprite.Textures.Count; i++)
    {
        var tpi = sprite.Textures[i]?.Texture; 
        if (tpi == null) continue;

        // Fetch the name of the texture sheet page this frame belongs to
        string tPageName = tpi.TexturePage?.Name?.Content ?? "UnknownPage";
        string spriteName = sprite.Name.Content;

        // Append the exact boundary coordinates to our map
        csvData.AppendLine($"{spriteName},{i},{tPageName},{tpi.SourceX},{tpi.SourceY},{tpi.SourceWidth},{tpi.SourceHeight},{tpi.TargetX},{tpi.TargetY}");
        exportedCount++;
    }
}

//Save file while checking for errors to send to quality check
try
{
    File.WriteAllText(outputPath, csvData.ToString());
    ScriptMessage($"Silent extraction complete! Mapped {exportedCount} frame profiles.");
}
catch (Exception ex)
{
    Console.Error.WriteLine($"[INTERNAL C# DISK ERROR]: Failed to write CSV. {ex.Message}");
    Environment.Exit(1);
}