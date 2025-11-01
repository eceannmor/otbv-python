import numpy as np
import struct

from otbv.encoding import *
from otbv.exceptions import SignatureException

__all__ = ['save', 'load']

__VALID_SIGNATURE = "\x4f\x54\x42\x56\x96" # OTBV/x96

def save(volume: np.ndarray, filename: str):
    """!
    @brief Encodes and saves the volume to a file
    @param filename File name for the encoded volume. Must end with \p .octv
    """
    if not filename.endswith('.octv'):
        raise ValueError(f"Provided filename \"{filename}\" does not end with .octv")
    
    resolution, encoding = encode(volume)
    pad_len = 8 - len(encoding) % 8
    if pad_len:
        pad = '0' * pad_len
        encoding = pad + encoding
    encoding = [int(encoding[i:i+8], 2) for i in range(0, len(encoding), 8)]
    encoding = bytes(encoding)
    
    with open(filename, "wb") as f:
        f.write(struct.pack("<H", int(resolution)))
        f.write(struct.pack(">B", int(pad_len)))
        f.write(encoding)

def load(filename) -> np.ndarray:
    """!
    @brief Loads and decodes the data from a provided file
    """
    with open(filename, "rb") as f:
        ### signature ###
        signature = f.read(5)
        if signature != __VALID_SIGNATURE:
            raise SignatureException(f"Could not validate file signature for {filename}")
        
        ### metadata ###
        # first bit
        first = f.read(1)
        padding_length = ((first >> 5) & 0b111) | 0
        cubic = bool((first >> 4) & 0b1)

        # resolution
        X = struct.unpack('!I', f.read(4))
        if (cubic):
            f.seek(8, 1)
            Y = Z = X
        else:
            Y = struct.unpack('!I', f.read(4))
            Z = struct.unpack('!I', f.read(4))
        
        edge_length_to_read = max(X, Y, Z)

        data_length = struct.unpack('!I', f.read(4))

        ### data ###
        read_data = f.read(data_length)
        if (data_length > len(read_data)):
            print(f"File contains less data than declared. Expected {data_length} bytes, but got {len(read_data)}. The decoder may throw")

        bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
        data = ''.join(map(str, bits))
        data = data[padding_length:]
        volume = decode(edge_length_to_read, data)
        volume = volume[:X, :Y, :Z]
        return volume