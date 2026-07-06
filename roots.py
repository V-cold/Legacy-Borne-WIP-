# This is the official LegacyBorne-BetaTest source code. Please feel free to report any bugs or suggestions to the repository or vtgavigan@gmail.com
# Smile, drink water, stretch, and take a deep breath

# File name: roots.py
# Purpose:
# Date created: 2026/06/22 2:30am JST
# Mood: I need a redbull

#TODO: somehow a random leagacy borne file is made on run. as u can tell I ish sleepyu from where this todo comment is

# Libraries
import os
import subprocess
import shutil
import sys
from pathlib import Path

# Paths
# main path
# --- Paths ---
BASE_DIR = Path(__file__).parent.resolve()
DELTARUNE = BASE_DIR / "DELTARUNE"
GLOBAL_MUS = DELTARUNE / "mus"
GLOBAL_DATA = Path("DELTARUNE/data.win")

# chapters: I opted to make this a dictionary so we can cycle through each chapter sequentially when loading. Part of me wonders if there is a more optimized way
CHAPTERS = {
"CH1": DELTARUNE / "chapter1_windows", # "The heroes defeat the king and stop the dragon."
"CH2": DELTARUNE / "chapter2_windows", # "The heroes do battle in chariots to save the Queen."
"CH3": DELTARUNE / "chapter3_windows", # "The heroes travel among the islands and catch a glimpse of a lost land."
"CH4": DELTARUNE / "chapter4_windows", # "A great smith gives the heroes a terrible weapon."
"CH5": DELTARUNE / "chapter5_windows", # "The vast garden is charred in an inferno of jealousy."
"CH6": DELTARUNE / "chapter6_windows", # "...What happens next? Geheheh! Who knows?"
"CH7": DELTARUNE / "chapter7_windows"  # "There was only one more chapter... After that, It all stopped. That next book, it never did get written."
}


#The ones who could write the next, the youth, the pen was lying there for them to pick up.
#To make the next page.
#They never did

# products
EXPORTS = Path("../rawExports")
ROMFS = Path("romfs")
qualityCheck = []

# ---------------------------------------------------------------------------------------------------------------------------------------------------

# Build Directories: From here the code will build the file system necessary to contain the program.
ROMFS.mkdir(parents=True, exist_ok=True)
(ROMFS / "gfx").mkdir(exist_ok=True)
(ROMFS / "audio").mkdir(exist_ok=True)

#----------------------------------------------------------------------------------------------------------------------------------------------------
# part 1 and part 2 algorithms: Let me address what exactly these are here. Part one algorithms are crtical rules that are setup early on to optimize the creation of our rom.
#                               think of them like a processor's op codes but instead it will lay out how exactly each asset gets loaded or de loaded, how will we load sfk, 
#                               what will trigger a legacyBorne side load screen. Because the 3ds can't handle a large majority of what a PC can, the part one algorithms are
#                               needed to ensure smooth runtime and user experience.
#                               Part two algorithms are passed the skeleton part one creates and takes our converted assets to add muscles(game scripts) and fats(assets) to our 
#                               program. After that, it primes the rom to be used and passes it to the qualityCheck to make sure it was create properly.

# Functions
def extractionProtocol(chapters, dataMain, exportFiles):
    # Probably the most straight forward function.
    # TODO: String extraction may not be neccessary.
    # TODO: Video extraction for tenna cutscene and flowery cutscene
    BASE_DIR = Path(__file__).parent.resolve()
    CLIENT_PATH = BASE_DIR / "UndermodCLI" / "UndertaleModCli"
    script_path = BASE_DIR / "LBScripts" / "extract_texture_map.csx"

    # Utilizes Undermod to dump assets for each chapter and then global
    print("\nRunning Extraction Protocol...")
    #Chapter Extraction --------------------------------------------------
    for c, chapterPath in chapters.items():
        rawChapterDir = Path(chapterPath).resolve()
        chDataPath = rawChapterDir / "data.win"
        if not chapterPath.exists():
            print(f"Skipping {c}, data.win not found.")
            continue

        chDataPath = Path(chapterPath / "data.win")
        chExports = BASE_DIR / "LegacyBorne" / exportFiles / c

        #Texture Map (TPI) Extraction----------------------------------------
        print(f"Unpacking texture maps from {c}... ")
        
        try:
            subprocess.run([
                str(CLIENT_PATH), "load", str(chDataPath), "-s", str(script_path)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

            # Move the csv to exports
            sourceCSV = rawChapterDir / "texture_metadata_map.csv"
            destinationCSV = chExports / "texture_metadata_map.csv"
            if sourceCSV.exists():
                shutil.move(str(sourceCSV), str(destinationCSV))
        
        except subprocess.CalledProcessError as e:
            print(f"Error in {c} texture map extraction: {e}")
            qualityCheck.append({
                "chapter": c, 
                "task": "TPI Extraction",
                "command": " ".join(e.cmd), 
                "error_msg": e.stderr.strip() if e.stderr else "Unknown CLI Error"
            })
                

        # Script Extraction------------------------------------------------
        print(f"Unpacking scripts from {c}... ")
        chScriptExport = chExports / "scripts"
        chScriptExport.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run([
                str(CLIENT_PATH), "dump", str(chDataPath), "--code", "UMT_DUMP_ALL", "-v", "-o", str(chScriptExport)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error in {c} script extraction: {e}.")
            qualityCheck.append({
                "chapter": c, 
                "task": "Script Extraction",
                "command": " ".join(e.cmd), 
                "error_msg": e.stderr.strip() if e.stderr else "Unknown CLI Error"
            })

        # String Extraction------------------------------------------------
        print(f"Unpacking strings from {c}... ")
        chStringExport = chExports / "strings"
        chStringExport.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run([
                str(CLIENT_PATH), "dump", str(chDataPath), "--strings", "-v", "-o", str(chStringExport)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error in {c} string extraction: {e}.")
            qualityCheck.append({
                "chapter": c, 
                "task": "String Extraction",
                "command": " ".join(e.cmd), 
                "error_msg": e.stderr.strip() if e.stderr else "Unknown CLI Error"
            })

        # Texture Extraction--------------------------------------------------
        print(f"Unpacking textures from {c}... ")
        chTextureExport = chExports / "textures"
        chTextureExport.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run([
                str(CLIENT_PATH), "dump", str(chDataPath), "--textures", "-v", "-o", str(chTextureExport)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error in {c} texture extraction: {e}.")
            qualityCheck.append({
                "chapter": c, 
                "task": "Texture Extraction",
                "command": " ".join(e.cmd), 
                "error_msg": e.stderr.strip() if e.stderr else "Unknown CLI Error"
            })


        #Music Extraction-------------------------------------------------
        chMusExport = Path(chExports / "mus")
        chMusExport.mkdir(parents=True, exist_ok=True)
        print(f"Unpacking Mus from {c}, ")
        for audio in chapterPath.glob("*.ogg"):
            shutil.copy2(audio, chMusExport / audio.name)

    #Global Texture Map (TPI) Extraction----------------------------------------
    print(f"Unpacking global texture maps... ")
    
    try:
        subprocess.run([
            str(CLIENT_PATH), "load", str(dataMain), "-s", str(script_path)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

        # Move the csv to exports
        gSourceCSV = DELTARUNE / "texture_metadata_map.csv"
        gDestinationCSV = exportFiles / "texture_metadata_map.csv"
        if gSourceCSV.exists():
            shutil.move(str(gSourceCSV), str(gDestinationCSV))
    
    except subprocess.CalledProcessError as e:
        print(f"Error in global texture map extraction: {e}")
        qualityCheck.append({
            "chapter": "Global", 
            "task": "TPI Extraction",
            "command": " ".join(e.cmd), 
            "error_msg": e.stderr.strip() if e.stderr else "Unknown CLI Error"
        })

    # Global Script Extraction ------------------------------------------------
    print("Unpacking global scripts... ")
    globalScriptExport = "LegacyBorne" / exportFiles / "scripts"
    globalScriptExport.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([
            str(CLIENT_PATH), "dump", str(dataMain), "--code", "UMT_DUMP_ALL", "-v", "-o", str(globalScriptExport)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error in global script extraction: {e}.")
        qualityCheck.append({
            "chapter": "Global", 
            "task": "Script Extraction",
            "command": " ".join(e.cmd), 
            "error_msg": e.stderr.strip() if e.stderr else "Unknown CLI Error"
        })

    # Global String Extraction ------------------------------------------------
    print("Unpacking global strings... ")
    globalStringExport = "LegacyBorne" / exportFiles / "strings"
    globalStringExport.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([
            str(CLIENT_PATH), "dump", str(dataMain), "--strings", "-v", "-o", str(globalStringExport)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error in global string extraction: {e}.")
        qualityCheck.append({
            "chapter": "Global", 
            "task": "String Extraction",
            "command": " ".join(e.cmd), 
            "error_msg": e.stderr.strip() if e.stderr else "Unknown CLI Error"
        })

    # Global Texture Extraction --------------------------------------------------
    print("Unpacking global textures... ")
    globalTextureExport = "LegacyBorne" / exportFiles / "textures"
    globalTextureExport.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run([
            str(CLIENT_PATH), "dump", str(dataMain), "--textures", "-v", "-o", str(globalTextureExport)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error in global texture extraction: {e}.")
        qualityCheck.append({
            "chapter": "Global", 
            "task": "Texture Extraction",
            "command": " ".join(e.cmd), 
            "error_msg": e.stderr.strip() if e.stderr else "Unknown CLI Error"
        })

        #Global Music Extraction-------------------------------------------------
    print("Unpacking global Mus, ")
   
    globalMusExport = "LegacyBorne" / exportFiles / "mus"
    globalMusExport.mkdir(parents=True, exist_ok=True)

    for audio in GLOBAL_MUS.glob("*.ogg"):
        shutil.copy2(audio, globalMusExport / audio.name)

    EXPORTS_LOCALES = { # Used by conversion for the next step
    "GLOBAL": EXPORTS,
    "CH1": EXPORTS / "CH1",
    "CH2": EXPORTS / "CH2",
    "CH3": EXPORTS / "CH3",
    "CH4": EXPORTS / "CH4",
    "CH5": EXPORTS / "CH5",
    "CH6": EXPORTS / "CH6",
    "CH7": EXPORTS / "CH7"
    }

    return EXPORTS_LOCALES

def conversionProtocol(exportFiles):
    print("\nRunning Conversion Protocol...")
    for c, targetPath in exportFiles.items():
        targetPath = Path(targetPath)
        if not targetPath.exists():
            continue
            
        # Texture conversion. The goal here is to take the 2048 gml texture sheets with the TPI and feed it into 3ds standard 1024 quadrants
        textureDir = targetPath / "textures"
        if textureDir.exists():
            for imgFile in textureDir.glob("*.png"):
                pass # TODO: Pillow quadrant-slicing and UV map adjustments

        # Video conversion. We are just down scaling and converting to a nice pre-rendered format the 3ds will accept
        videoDir = targetPath / "videos"
        if videoDir.exists():
            for videoFile in videoDir.glob("*"):
                pass # TODO: downscaling

        # Music conversion. Near same as videos
        musDir = targetPath / "mus"
        if musDir.exists():
            for audioFile in musDir.glob("*.ogg"):
                pass # TODO: downscaling

        #POSSIBLE ROADBLOCKS: 
        #File size won't be an issue on static storage, but ram wise it will be
    pass

def compilationProtocol():
    # Compiles assets and scripts and passes it all through part 1 algorithms who's products are handed off to part 2 in packaging
    pass
def packagingProtocol():
    # Creates the rom file via part 2 algorithms and cleans the file space to improve user experience. 
    pass
def qualityCheckProtocol(errors, exportRoot="rawExports"):
    # Analyzes and records any tripped errors. Ensures rom integrity as well as making sure all tests passed
    logPath = Path("pipelineQualityCheck.log")

    #TODO 1. Integrity

    # 2. Logging
    logLines = [ 
        "V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V",
        f"                           Legacy Borne Quality Check                           ",
        "V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V^V",
        f"Integrity check results: WARNING [Unimplimented]", #TODO integrity check
        f"Error check results: {'ERROR' if errors else 'No errors detected'}",
        "---------------------------------------------------------------------------------",
    ]
    if errors:
        logLines.append(f"{len(errors)} have been detected!\n")
        for index, err in enumerate(errors, 1):
            logLines.extend([
            f"[{index}] Location:{err['chapter']} Task: {err['task']}",
            f"          Command: {err['command']}",
            f"DIAGNOSIS:\n {err['error_msg']}",
            ])
    else:
        logLines.append("No errors flagged during asset extraction.")
    # Write report out to disk
    with open(logPath, "w", encoding="utf-8") as logFile:
        logFile.write("\n".join(logLines))
    
    pass

if __name__ == "__main__":
    # Test execution to verify directory construction works smoothly
    conversionProtocol(extractionProtocol(CHAPTERS, GLOBAL_DATA, EXPORTS))
    qualityCheckProtocol(qualityCheck, exportRoot="rawExports")
    print("Reached end of execution!")
