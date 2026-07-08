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
import csv
from pathlib import Path

# Used in Texture sheet conversion
from PIL import Image

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
EXPORTS = Path(BASE_DIR / "rawExports")
ROMFS = Path("romfs")
qualityCheck = []

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
    # Probably the most straight forward function.
    # TODO: String extraction may not be neccessary.
    # TODO: Video extraction for tenna cutscene and flowery cutscene(can grab this straight from deltarune file)
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

            destinationCSV.parent.mkdir(parents=True, exist_ok=True)

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
        print(f"Unpacking mus from {c}, ")
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
        gDestinationCSV = BASE_DIR / "LegacyBorne" / exportFiles / "GLOBAL" / "texture_metadata_map.csv"

        gDestinationCSV.parent.mkdir(parents=True, exist_ok=True)

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
    globalScriptExport = "LegacyBorne" / exportFiles / "GLOBAL" / "scripts"
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
    globalStringExport = "LegacyBorne" / exportFiles / "GLOBAL" / "strings"
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
    globalTextureExport = "LegacyBorne" / exportFiles / "GLOBAL" / "textures"
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
    print("Unpacking global mus, ")
   
    globalMusExport = "LegacyBorne" / exportFiles / "GLOBAL" / "mus"
    globalMusExport.mkdir(parents=True, exist_ok=True)

    for audio in GLOBAL_MUS.glob("*.ogg"):
        shutil.copy2(audio, globalMusExport / audio.name)
    
    pass

def conversionProtocol(exportFiles):
    print("\nRunning Conversion Protocol ...")

    if not exportFiles.exists():
        print("Fatal: Master exports directory missing!")
        qualityCheck.append({ 
            "task": "Conversion Protocol",
            "command": " ".join(e.cmd), 
            "error_msg": "Fatal: Master exports directory missing!"
        })
        return

    for targetPath in exportFiles.iterdir():

        if not targetPath.is_dir():
            continue
        
        print(f"\nConverting textures and maps in {targetPath.stem} exports...")
        # Texture conversion. The goal here is to take the 2048 gml texture sheets with the TPI and feed it into 3ds standard 1024 quadrants after this we slap it so hard it becomes
        # a RGBA4444 file that is 2MB large which is perfect for the vram in a 3DS... This is done in the compilation protocol
        textureDir = Path(targetPath / "textures" / "EmbeddedTextures")
        csvPath = Path(targetPath / "texture_metadata_map.csv")
        spriteMappings = []

        if csvPath.exists():
            with open(csvPath, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                spriteMappings = list(reader)
        else:
            print("Fatal: texture_metadata_map.csv missing!")
            qualityCheck.append({ 
                "task": f"Conversion Protocol in {targetPath}",
                "command": " ".join(e.cmd), 
                "error_msg": "Fatal: texture_metadata_map.csv missing! Check that TPI extraction ran properly."
            })
            continue


        new3dsMappings = [] # Behold our first look at a finished product within all the code
        straddleSprites = [] # This will hold sprites to be extracted to lost n' found sheets
        new3dsTextureSheets = [] # This will hold all of our pngs to be quantized to rgba4444

        if textureDir.exists():
            for imgFile in textureDir.glob("*.png"):
                baseName = imgFile.stem

                with Image.open(imgFile) as img:
                    width, height = img.size

                    # There is a slight variance to the texture map size of some files so we need to handle that
                    if width != 2048 and height != 2048:

                        # We fill it with black space to make it 2048. There is a chance for optimization here if we want to cut certain quadrats out and focus on what
                        # has sprite data.
                        paddedImg = Image.new("RGBA", (2048, 2048), (0, 0, 0, 0))
                        paddedImg.paste(img, (0, 0))
                        img = paddedImg

                    quadrants = {
                        "Q1": img.crop((0, 0, 1024, 1024)),
                        "Q2": img.crop((1024, 0, 2048, 1024)),
                        "Q3": img.crop((0, 1024, 1024, 2048)),
                        "Q4": img.crop((1024, 1024, 2048, 2048))
                    }

                    # Now we need to fix any loose sprites so that the 3DS doesn't choke if we have to feed it multiple sprite sheets to churn a sprite.
                    # TODO: Toby Fox's sprite sheets are not in neat quadrants sooooo there is gonna be a ton for slicing and I may need to make new lost 
                    # and found texture maps containing extra space for sprites. Keep in mind how to optimize lost and found sprite sheets.
                    for row in spriteMappings:
                        pageName = row["TexturePage"].replace(".png", "").replace(".PNG", "").strip()

                        if pageName == baseName:
                            try:
                                srcX = int(row["SourceX"])
                                srcY = int(row["SourceY"])
                                width = int(row["Width"])
                                height = int(row["Height"])

                                rightEdge = srcX + width
                                bottomEdge = srcY + height

                                if rightEdge <= 1024 and bottomEdge <= 1024:
                                    quad, ox, oy = "Q1", 0, 0
                                elif srcX >= 1024 and bottomEdge <= 1024:
                                    quad, ox, oy = "Q2", 1024, 0
                                elif rightEdge <= 1024 and srcY >= 1024:
                                    quad, ox, oy = "Q3", 0, 1024
                                elif srcX >= 1024 and srcY >= 1024:
                                    quad, ox, oy = "Q4", 1024, 1024
                                else:
                                    # grab sprite for lost n' found
                                    straddleSprites.append({
                                        "imgFile": imgFile,
                                        "row": row,
                                        "srcX": srcX, "srcY": srcY,
                                        "width": width, "height":height
                                    })
                                    continue


                                # Finally, we append the remapped coordinates to our final map and loop
                                new3dsMappings.append({
                                    "SpriteName": row["SpriteName"],
                                    "FrameIndex": row["FrameIndex"],
                                    "TexturePage": f"{baseName}_{quad}",
                                    "SourceX": srcX - ox,
                                    "SourceY": srcY - oy,
                                    "Width": row["Width"],
                                    "Height": row["Height"],
                                    "OffsetX": row["OffsetX"],
                                    "OffsetY": row["OffsetY"]
                                })
                            except ValueError:
                                continue

                    print(f"\nQuantizing and saving final quadrants for {baseName}...")
                    for qName, qImg in quadrants.items():
        
                        rgba_img = qImg.convert("RGBA")
                        rgba4444_spec = rgba_img.quantize(colors=256)
                        
                        try:
                            rgba4444_spec.save(targetPath / f"{baseName}_{qName}.png")
                            print(f"Quantized image of {baseName}_{qName} saved successfully!")
                        except Exception as e:
                            print(f"Error saving {baseName}_{qName}: {e}")
                            qualityCheck.append({ 
                            "task": f"Conversion Protocol in {targetPath}",
                            "command": " ".join(e.cmd), 
                            "error_msg": f"Error saving {baseName}_{qName}: {e}"})
        else:
            print(f"Fatal: {targetPath} texture directory missing!")
            qualityCheck.append({ 
                "task": f"Conversion Protocol in {targetPath}",
                "command": " ".join(e.cmd), 
                "error_msg": f"Fatal: {targetPath} texture directory missing! Check that texture extraction ran properly."
            })
            continue

        if straddleSprites:
            print(f"Processing {len(straddleSprites)} sprites into Lost n' Found sheets...")
            LFIndex = 0
            LFName = f"lostNFound{LFIndex}"
            LFCanvas = Image.new("RGBA", (1024,1024), (0,0,0,0))

            currX, currY = 0, 0
            maxRowHeight = 0

            for lostSprite in straddleSprites:
                # Drop to next row when x is full
                if currX + lostSprite["width"] > 1024:
                    currX = 0
                    currY += maxRowHeight
                    maxRowHeight = 0
                    
                # Save and create new sheet when no more y is left (for further space optimization, cycle sprites)
                if currY + lostSprite["height"] > 1024:
                        LFCanvas.save(textureDir / f"3ds{LFName}.png")
                        LFIndex += 1
                        LFName = f"lostNFound{LFIndex}"
                        LFCanvas = Image.new("RGBA", (1024,1024), (0,0,0,0))
                        currX, currY = 0, 0
                        maxRowHeight = 0

                with Image.open(lostSprite["imgFile"]) as master:
                    #This line is disgusting :(
                    cropBox = (lostSprite["srcX"], lostSprite["srcY"], 
                            lostSprite["srcX"] + lostSprite["width"], lostSprite["srcY"] + lostSprite["height"])
                    spriteBox = master.crop(cropBox)
                    LFCanvas.paste(spriteBox, (currX, currY))
                
                # Log the brand new 3DS mapping rules
                new3dsMappings.append({
                    "SpriteName": lostSprite["row"]["SpriteName"],
                    "FrameIndex": lostSprite["row"]["FrameIndex"],
                    "TexturePage": LFName,
                    "SourceX": currX,
                    "SourceY": currY,
                    "Width": lostSprite["width"],
                    "Height": lostSprite["height"],
                    "OffsetX": lostSprite["row"]["OffsetX"],
                    "OffsetY": lostSprite["row"]["OffsetY"]
                })

                maxRowHeight = max(maxRowHeight, lostSprite["height"])
                currX += lostSprite["width"]
            
            # Save the LF sheet and continue
            LFCanvas.save(textureDir / f"{LFName}.png")

        # We lastly print our new mappings and assets
        if new3dsMappings:
            outputCSVPath = targetPath / "texture_metadata_map_3ds.csv"
            with open(outputCSVPath, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "SpriteName", "FrameIndex", "TexturePage", 
                    "SourceX", "SourceY", "Width", "Height", "OffsetX", "OffsetY"
                ])
                writer.writeheader()
                writer.writerows(new3dsMappings)
            print(f"Successfully created the {targetPath.stem} texture_metadata_map_3ds.csv")       

        # With our new quadrants and lost n' founds, 
        # we wanna prep them for downsampling but not scale them just yet.
        # So we will quantize them and hold them as PNGs for compilation 
        # for qName, qImg in quadrants.items():
        #    print(f"Quantizing {qName} in {targetPath.stem} exports...")
        #    rgba4444_spec = qImg.convert("RGBA").quantize(colors=256)
        #    if(rgba4444_spec.save(targetPath / f"{baseName}_{qName}.png")):
        #        print(f"Quantized image of {qName} saved!")
        #    else
        #        print(f"Error saving the image.")   
        

        # Video conversion. We are just down scaling and converting to a nice pre-rendered format the 3ds will accept
        videoDir = Path(targetPath / "videos")
        if videoDir.exists():
            for videoFile in videoDir.glob("*"):
                pass # TODO: downscaling

        # Music conversion. Near same as videos
        musDir = Path(targetPath / "mus")
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
    extractionProtocol(CHAPTERS, GLOBAL_DATA, EXPORTS)
    conversionProtocol(EXPORTS)
    qualityCheckProtocol(qualityCheck, exportRoot="rawExports")
    print("Reached end of execution!")


#TODO: quantize lost and found