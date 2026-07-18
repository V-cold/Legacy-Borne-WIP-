# Libarires

import struct
from pathlib import Path

class BCSTMproto:
    def __init__(self,wavPath,outPath):
        self.wavPath = Path(wavPath)
        self.outPath = Path(outPath)

    def creationProto(self):

        # We need a strict Big-Edian File Header
        try:
            with open(self.outPath, 'wb') as f:
                f.write(b"CSTM")
                f.write(struct.pack("<H",0xFEFF))
                f.write(struct.pack("<H", 0x0040))
                f.write(struct.pack("<I", 0x02000000))
             #  f.write(struct.pack("<I", fileSize))
                f.write(struct.pack("<H", 0x0003))   
                f.write(struct.pack("<H", 0x0000))  

                # 1. Info
                f.write(struct.pack("<H", 0x4000))
                f.write(struct.pack("<H", 0x0000))
             #  f.write(struct.pack("<I", infoOffset)) 
             #  f.write(struct.pack("<I", infoSize))

                # 2. Seek
                f.write(struct.pack("<H", 0x4001))
                f.write(struct.pack("<H", 0x0000))
             #  f.write(struct.pack("<I", seekOffset))
             #  f.write(struct.pack("<I", seekSize))

                # 3. Data
                f.write(struct.pack("<H", 0x4002))
                f.write(struct.pack("<H", 0x0000))
             #  f.write(struct.pack("<I", dataOffset))
             #  f.write(struct.pack("<I", dataSize))

            return True

        except Exception as e: #This will be intercepted by our quality check
            raise RuntimeError(f"Binary creation failed! {str(e)}")