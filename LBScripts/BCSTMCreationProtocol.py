# Libarires

import struct
from pathlib import Path

class BCSTMproto:
    def __init__(self,wavPath,outPath):
        self.wavPath = Path(wavPath)
        self.outPath = Path(outPath)

    def creationProto(self):
        # Formulas / Math
        # Info

        # Seek
        
        # Data

        #WAV Conversion

        # Using https://www.3dbrew.org/wiki/BCSTM as referenece
        # Write section
        try:
            with open(self.outPath, 'wb') as f:
                # HEADER 
                f.write(b"CSTM")
                f.write(struct.pack("<H",0xFEFF))
                f.write(struct.pack("<H", header_size))
                f.write(struct.pack("<I", 0x02000000))
                f.write(struct.pack("<I", total_file_size))
                f.write(struct.pack("<H", 0x0003))   
                f.write(struct.pack("<H", 0x0000))  

                # Info Block offset relative to start file
                self.write_sized_reference(f, 0x4000, info_offset, info_size)
                
                # Seek Block offset relative to start file
                self.write_sized_reference(f, 0x4001, seek_offset, seek_size)
                
                # Data Block offset relative to start file
                self.write_sized_reference(f, 0x4002, data_offset, data_size)

                # INFO
                # SEEK
                # DATA 
            return True

        except Exception as e: #This will be intercepted by our quality check
            raise RuntimeError(f"Binary creation failed! {str(e)}")