#Cheatsheet
# print(x) can show a hex as a number
#hex(x) can show a number as a hex
#divmod(x, y) will give both quotient and remainder
#0xFEFF is stored as FF FE, which tells readers “this file is little-endian.” 
# < is little edian B is x00 H is x0000 I is x00000000
#https://www.3dbrew.org/wiki/BCSTM for more information of the actual BCSTM file

# Libarires
import array, math, wave, struct

def align(value, boundary=0x20):
    remainder = value % boundary
    if remainder == 0:
        return value
    return value + (boundary-remainder)

def pad_to(data, boundary=0x20):
    target = align(len(data), boundary)    # the length we want to end up with
    missing = target - len(data)             # how many bytes short are we?
    return data + bytes(missing)

#reference = type + offset H=type H=padding I=offset
def reference(type_id, offset):
    return struct.pack('<HHI', type_id,0,offset)
    

#sized reference = type + offset + bytes H=type H=padding I=offset I=bytes
def sized_reference(type_id, offset, size):
    return reference(type_id, offset) + struct.pack('<I',size)

def split_channels(raw, channel_count):
    samples = array.array('h')
    samples.frombytes(raw)
    result = []
    for c in range(channel_count):
        result.append(samples[c::channel_count].tobytes())
    return result

def read_wav(path):
    with wave.open(path, 'rb') as w:
        sample_rate = w.getframerate()
        frame_count = w.getnframes()
        channel_count = w.getnchannels()
        sample_width = w.getsampwidth()
        
        if sample_width != 2:
            raise ValueError("Expected 16-bit audio.")
        if frame_count == 0:
            raise ValueError("File has no audio.")

        raw = w.readframes(frame_count)

    channels = split_channels(raw, channel_count)
    return sample_rate, frame_count, channels

def compute_layout(frame_count):
    block_samples = 4096
    block_size = 8192
    full, rest = divmod(frame_count, block_samples)
    if rest == 0:
        block_count = full
        last_samples = 4096
    else:
        block_count = full + 1
        last_samples = rest
    last_size = last_samples*2
    last_padded_size = align(last_size)
    return{
        'block_count'      : block_count,
        'block_size'       : block_size,
        'block_samples'    : block_samples,  
        'last_samples'     : last_samples,
        'last_size'        : last_size,
        'last_padded_size' : last_padded_size
    }

## DATA BLOCK

def build_data_block(channels,layout):
    # defintions
    block_count = layout['block_count']
    block_size = layout['block_size']
    last_size = layout['last_size']
    last_padded_size = layout['last_padded_size']

    # error check channels
    if not channels:
        raise ValueError("No audio channels found.")
   
    expected_channel_bytes=((block_count-1)*block_size+last_size)
    for i, channel in enumerate(channels):
        if len(channel) != expected_channel_bytes:
            raise ValueError(
                f"Channel {i} has {len(channel)} bytes; "
                f"expected {expected_channel_bytes}"
            )
    # main loop
    payload = bytearray()

    for b in range(block_count):
        is_last = b == block_count - 1
        start = b * block_size # This is where the block beings for each channel

        if is_last:
            actual_size = last_size
            stored_size = last_padded_size
        else:
            actual_size = block_size
            stored_size = block_size

        for ch in channels:
            piece = ch[start:start + actual_size]

        payload.extend(piece)
        payload.extend(bytes(stored_size - actual_size))

    data = bytearray(0x20)
    data[0:4] = b'DATA'
    data.extend(payload)

    struct.pack_into('<I', data, 4, len(data))
    offset = 0x20 - 0x08
    return bytes(data), offset

## SEEK BLOCK

def build_seek_block(payload = b''):
    unpadded_size = 0x08 + len(payload)
    block_size = align(unpadded_size, 0x20)

    # creates a block of zeros to fill
    seek = bytearray(block_size)
    seek[0:4] = b'SEEK'

    # move seek into our byte array
    struct.pack_into('<I', seek, 4, block_size)

    #grab seek data into payload
    seek[0x08:0x08 + len(payload)] = payload
    return bytes(seek)

## INFO BLOCK


def build_stream_info(sample_rate, frame_count, channel_count, layout, sample_offset):
    header = struct.pack('<BBBB', 1, 0, channel_count, 0)
    stream_info =  header + (
        struct.pack('<IIIIIIIIIII', sample_rate, 0, frame_count, layout['block_count'],
        layout['block_size'], layout['block_samples'], layout['last_size'], 
        layout['last_samples'], layout['last_padded_size'], 0, 0)
        + reference(0x1F00, sample_offset)
    )
    return stream_info

def build_track_info(channel_count):
    header = (struct.pack('<BBH',0x7f, 0x40, 0) + reference(0x0100,0x0C))

    channel_indexes = bytes(range(channel_count))
    byte_table = struct.pack('<I', channel_count) + channel_indexes

    byte_table = pad_to(byte_table, 4)

    track_info = header + byte_table

    return track_info

def build_channel_info(channel_count): return reference(0, 0xFFFFFFFF) * channel_count
    
# Find proper byte positions for writing 
def compute_info_positions(channel_count):
    info_positions = struct.pack('<I', (()))
    return info_positions

def build_info_block(sample_rate, frame_count, channel_count, layout, sample_offset):
    info = 0
    return info



########### TESTING ###############

assert align(0) == 0
assert align(1) == 0x20
assert align(0x20) == 0x20
assert align(0x21) == 0x40
assert pad_to(b'abc', 4) == b'abc' + bytes(1)

assert reference(0x4000, 0x40).hex() == '0040000040000000'
assert reference(0x4001, 0xE0).hex() == '01400000e0000000'
assert sized_reference(0x4000, 0x40, 0x100).hex() == '004000004000000000010000'
assert sized_reference(0x4002, 0x100, 20064).hex() == '0240000000010000604e0000'

raw = struct.pack('<6h', 1, -1, 2, -2, 3, -3)
left, right = split_channels(raw, 2)
assert left == struct.pack('<3h', 1, 2, 3)
assert right == struct.pack('<3h', -1, -2, -3)

rate, frames, channels = read_wav('test_stereo.wav')
assert rate == 32000
assert frames == 5000
assert len(channels) == 2
assert len(channels[0]) == 10000 and len(channels[1]) == 10000

layout = compute_layout(5000)
assert layout['block_count'] == 2
assert layout['last_samples'] == 904
assert layout['last_size'] == 1808
assert layout['last_padded_size'] == 1824

table = [
    (1, 1, 1, 2, 32),
    (4096, 1, 4096, 8192, 8192),
    (4097, 2, 1, 2, 32),
    (5000, 2, 904, 1808, 1824),
    (10000, 3, 1808, 3616, 3616),
]
for frames, blocks, last_samples, last_size, last_padded in table:
    result = compute_layout(frames)
    assert result['block_count'] == blocks
    assert result['last_samples'] == last_samples
    assert result['last_size'] == last_size
    assert result['last_padded_size'] == last_padded

# Build the layout from a known WAV file.
rate, frames, channels = read_wav('test_stereo.wav')
layout = compute_layout(frames)

# Build the two blocks.
seek = build_seek_block()
data, sample_offset = build_data_block(channels, layout)

# Build the metadata that describes the DATA block.
stream_info = build_stream_info(
    rate, frames, len(channels), layout, sample_offset
)

# SEEK 
assert seek[:4] == b'SEEK'
assert len(seek) == 0x20
assert struct.unpack_from('<I', seek, 4)[0] == len(seek)

# DATA 
assert data[:4] == b'DATA'
assert struct.unpack_from('<I', data, 4)[0] == len(data)
assert data[0x20:0x24] == channels[0][:4]

# Stream
assert len(stream_info) == 0x38
assert struct.unpack_from('<I', stream_info, 0x28)[0] == 0
assert struct.unpack_from('<I', stream_info, 0x2C)[0] == 0
assert struct.unpack_from('<I', stream_info, 0x34)[0] == 0x18

print('SEEK size:', hex(len(seek)))
print('DATA size:', hex(len(data)))
print('Sample offset:', hex(sample_offset))
print('Stream Info size:', hex(len(stream_info)))
#frames, rate = 5000, 32000
#with wave.open('test_stereo.wav', 'wb') as w:
#    w.setnchannels(2)
#    w.setsampwidth(2)
#    w.setframerate(rate)
#    data = array.array('h')
#    for i in range(frames):
#        data.append(int(12000*math.sin(2*math.pi*220*i/rate)))
#        data.append(int(12000*math.sin(2*math.pi*330*i/rate)))
#    w.writeframes(data.tobytes())
