# This is the official LegacyBorne-BetaTest source code. Please feel free to report any bugs or suggestions to the repository or vtgavigan@gmail.com
# Smile, drink water, stretch, and take a deep breath

# File name: roots.py
# Purpose:
# Date created: 2026/06/22 2:30am JST
# Mood: I need a redbull

# Libraries
import os
import subprocess
import shutil
import sys
from pathlib import Path

# Paths
# main path
# --- Paths ---
DELTARUNE = Path("DELTARUNE")
GLOBAL_MUS = DELTARUNE / "mus"
GLOBAL_DATA = Path("/DELTARUNE/data.win")

# chapters: I opted to make this a dictionary so we can cycle through each chapter sequentially when loading. Part of me wonders if there is a more optimized way
CHAPTERS = {
"CH1": DELTARUNE / "chapter1_windows", # "The heroes defeat the king and stop the dragon."
"CH2": DELTARUNE/  "chapter2_windows", # "The heroes do battle in chariots to save the Queen."
"CH3": DELTARUNE/  "chapter3_windows", # "The heroes travel among the islands and catch a glimpse of a lost land."
"CH4": DELTARUNE / "chapter4_windows"#,# "A great smith gives the heroes a terrible weapon." 
#"CH5": DELTARUNE / "chapter5_windows",  "The vast garden is charred in an inferno of jealousy."
#"CH6": DELTARUNE / "chapter6_windows",  "...What happens next? Geheheh! Who knows?"
#"CH7": DELTARUNE / "chapter7_windows"   "There was only one more chapter... After that, It all stopped. That next book, it never did get written."
}

#The ones who could write the next, the youth, the pen was lying there for them to pick up.
#To make the next page.
#They never did

# products
EXPORTS = Path("rawExports")
ROMFS = Path("romfs")

# ---------------------------------------------------------------------------------------------------------------------------------------------------

# Build Directories: From here the code will build the file system necessary to contain the program.
ROMFS.mkdir(parents=True, exist_ok=True)
(ROMFS / "gfx").mkdir(exist_ok=True)
(ROMFS / "audio").mkdir(exist_ok=True)

EXPORTS.mkdir(parents=True, exist_ok=True)

#----------------------------------------------------------------------------------------------------------------------------------------------------

# part 1 and part 2 algorithms: Let me address what exactly these are here. Part one algorithms are crtical rules that are setup early on to optimize the creation of our rom.
#                               think of them like a processor's op codes but instead it will lay out how exactly each asset gets loaded or de loaded, how will we load sfk, 
#                               what will trigger a legacyBorne side load screen. Because the 3ds can't handle a large majority of what a PC can, the part one algorithms are
#                               needed to ensure smooth runtime and user experience.
#                               Part two algorithms are passed the skeleton part one creates and takes our converted assets to add muscles(game scripts) and fats(assets) to our 
#                               program. After that, it primes the rom to be used and passes it to the qualityCheck to make sure it was create properly.

# Functions
def extractionProtocol(chapters, dataMain, exportFiles):
    # Utilizes Undermod to dump assets for each chapter
    print("\nRunning Extraction Protocol...")
    #Chapter Extraction --------------------------------------------------
    for c, chapterPath in chapters.items():
        if not chapterPath.exists():
            print(f"Skipping {c}, data.win not found.")
            continue

        chDataPath = chapterPath / "data.win"
        chExports = exportFiles / c

        #Sprite Extraction------------------------------------------------
        print(f"Unpacking sprites from {c}, ")
        chSpriteExport = chExports / "sprites"
        chSpriteExport.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run([
                "wine","UndertaleModTool.exe", str(chDataPath),
                "Scripts/Resource Exporters/ExportAllSprites.csx",
                "-o", str(chSpriteExport)
            ], check=True, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
             print(f"Error in {c} sprite extraction: {e}.")

        #Tileset Extraction-----------------------------------------------
        print(f"Unpacking tilesets from {c}, ")
        chTilesetExport = chExports / "tilesets"
        chTilesetExport.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run([
                "wine","UndertaleModTool.exe", str(chDataPath),
                "Scripts/Resource Exporters/ExportAllTilesets.csx",
                "-o", str(chTilesetExport)
            ], check=True, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
             print(f"Error in {c} tileset extraction: {e}.")

        #Music Extraction-------------------------------------------------
        print(f"Unpacking Mus from {c}, ")
        if  chapterPath.exists():
            chapterMusExport = chExports / "chMus"
            chapterMusExport.mkdir(parents=True, exist_ok=True)

            for audio in chapterPath.glob("*.ogg"):
                shutil.copy2(audio, chapterMusExport / audio.name)

        

    #Global Music Extraction-------------------------------------------------
    print("Unpacking global Mus, ")
    if  GLOBAL_MUS.exists():
        globalMusExport = exportFiles / "gMus"
        globalMusExport.mkdir(parents=True, exist_ok=True)

        for audio in GLOBAL_MUS.glob("*.ogg"):
            shutil.copy2(audio, globalMusExport / audio.name)

    else:
        print("Error in global music extraction.")
        sys.exit(1)

    #Global Sprite Extraction------------------------------------------------
    print("Unpacking global sprites, ")
    spriteExport = exportFiles / "sprites"
    spriteExport.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([
            "wine","UndertaleModTool.exe", str(dataMain),
            "Scripts/Resource Exporters/ExportAllSprites.csx",
            "-o", str(spriteExport)

        ], check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Error in global sprite extraction: {e}.")

    #Global Tileset Extraction-----------------------------------------------
    print("Unpacking global tilesets, ")
    tilesetExport = exportFiles / "tilesets"
    tilesetExport.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([
            "wine","UndertaleModTool.exe", str(dataMain),
            "Scripts/Resource Exporters/ExportAllTilesets.csx",
            "-o", str(tilesetExport)
        ], check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
            print(f"Error in global tileset extraction: {e}.")

#TODO: grab the client version of undermod

def conversionProtocol():
    # Converts all assets into usable assets
    pass
def compilationProtocol():
    # Compiles assets and scripts and passes it all through part 1 algorithms who's products are handed off to part 2 in packaging
    pass
def packagingProtocol():
    # Creates the rom file via part 2 algorithms and cleans the file space to improve user experience. 
    pass
def qualityCheckProtocol():
    # Creates a log file and records any tripped errors. Ensures rom integrity as well as making sure all tests passed
    pass

if __name__ == "__main__":
    # Test execution to verify directory construction works smoothly
    extractionProtocol(CHAPTERS, GLOBAL_DATA, EXPORTS)
    print("Roots framework successfully loaded. Ready for pipeline integration.")