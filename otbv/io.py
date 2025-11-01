import numpy as np
import struct

from otbv.encoding import *

__all__ = ['save', 'load']

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
        resolution = struct.unpack("<H", f.read(2))
        pad_len = struct.unpack(">B", f.read(1))
        bits = f.read()
        bits = np.unpackbits(np.frombuffer(bits, dtype=np.uint8))
        data = ''.join(map(str, bits))
        data = data[pad_len[0]:]
        volume = decode(resolution[0], data)
        return volume