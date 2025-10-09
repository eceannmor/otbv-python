"""!
@package octvencode
@file octvencode.py
"""

import numpy as np
import struct

__ALLOWED_TYPES = (int, float, np.number, bool, np.bool)
__LATEST_FORMAT_VERSION = "0.0.1"

def __convert_or_throw(o) -> np.ndarray:
    """!
    @brief Attempts to convert \p o into a non-empty NumPy array. \n For detailed data conversion rules, check docs 
    @throws TypeError if the conversion is not possible
    @return \p o represented as a numpy array, if possible
    """
    if isinstance(o, np.ndarray) and o.dtype in __ALLOWED_TYPES:
        return o
    if isinstance(o, __ALLOWED_TYPES):
        return np.array(o)
    try:
        arr = np.asarray(o)
        if arr.dtype == object and all([isinstance(x, __ALLOWED_TYPES) for x in arr.flat]):
            return arr
        else:
            raise TypeError(f"Provided data is of an unsupported type (received {arr.dtype}, expected {__ALLOWED_TYPES})")
    except:
        raise TypeError("Provided object is not a valid NumPy array and cannot be converted to a NumPy array")
        
        

def _reshape_volume_to_cubic(volume: np.ndarray) -> np.ndarray:
    """!
    @brief Reshapes a NumPy array into a cube. \n Returns a copy of the data, \p volume remains unchanged
    @throws ValueError if \p volume cannot be reshaped into a cubic array
    @returns A cubic NumPy array with the same data as volume
    """
    volume = __convert_or_throw(volume)
    
    size = volume.size
    new_edge_len = np.cbrt(size)
    if not int(new_edge_len) == new_edge_len:
        raise ValueError(f"Could not reshape a volume with dimensions {volume.shape} into a cubic 3d volume")
    new_edge_len = int(new_edge_len)
    return np.reshape(volume, (new_edge_len, new_edge_len, new_edge_len))   
    

def _is_volume_homogeneous(subvolume: np.ndarray) -> bool:
    """!
    @returns True if all elements in \p subvolume are the same
    @returns False otherwise, or if \p subvolume is empty
    """
    subvolume = __convert_or_throw(subvolume)
    if subvolume.size < 2:
        return True
    return np.all(subvolume == subvolume.flat[0])


def __encode_subvolume_recursive(volume: np.ndarray, x_start: int, x_end: int,
                           y_start: int, y_end: int, z_start: int,
                           z_end: int) -> str:
    """!
    @brief Helper function. Encodes a subvolume. If the subvolume is homogeneous, returns a leaf bit and a value bit, else reterns a split bit as well as the concatenated encodings of all subvolumes of its own. \n The concatenation order is defined by the format.
    @return The encoding of the subvolume
    """

    subvolume = volume[x_start:x_end, y_start:y_end, z_start:z_end]
    assert subvolume.size > 0, f"Encountered a subvolume with a size of 0 when encoding the volume. This should never happen. Parameters: {x_start} {x_end} {y_start} {y_end} {z_start} {z_end}. Please open a new issue and attach the data you are trying to encode. https://github.com/eceannmor/octvencode-python/issues"
    if is_volume_homogeneous(subvolume):
        # leaf
        return f"0{int(subvolume.flat[0])}"

    x_split = [x_start, (x_start + x_end) // 2, x_end]
    y_split = [y_start, (y_start + y_end) // 2, y_end]
    z_split = [z_start, (z_start + z_end) // 2, z_end]

    subvolumes = []

    # order:
    # (0, 0, 0)
    # (1, 0, 0)
    # (0, 1, 0)
    # (1, 1, 0)
    # (0, 0, 1)
    # (1, 0, 1)
    # (0, 1, 1)
    # (1, 1, 1)
    for z in (0, 1):
        for y in (0, 1):
            for x in (0, 1):
                subvolumes.append(
                    encode_subvolume_recursive(volume, x_split[x], x_split[x + 1],
                                           y_split[y], y_split[y + 1],
                                           z_split[z], z_split[z + 1]))
    # slice
    return f"1{"".join(subvolumes)}"


def encode(volume: np.ndarray, format_version = __LATEST_FORMAT_VERSION) -> str:
    """
    Encode a bit volume as an octree and convert it to a string.
    """
    volume = __convert_or_throw(volume)

    shape = volume.shape
    if len(shape) != 3:
        raise ValueError(
            f"Passed volume with invalid dimensions. Expected 3, received {dimensions}."
        )

    resolution = shape[0]
    if shape != (resolution, resolution, resolution):
        raise ValueError(
            f"Dimension mismatch. Expected ({resolution},{resolution},{resolution}), received {shape}"
        )

    depth = np.log2(resolution)
    if int(depth) != depth:
        raise ValueError(
            f"Passed volume with invalid resolution. Expected a power of 2, received {resolution}."
        )

    string = encode_subvolume_recursive(volume, 0, resolution, 0, resolution, 0,
                                    resolution)
    return f"{resolution} {string}"


def __decode_subvolume_recursive(tokens, idx, volume, x_start, x_end, y_start, y_end,
                           z_start, z_end):
    if idx >= len(tokens):
        raise ValueError("Unexpected end of encoding")

    token = tokens[idx]
    idx = idx + 1

    # leaf, read the next value
    if token == '1':
        val = int(tokens[idx])
        volume[x_start:x_end, y_start:y_end, z_start:z_end] = val
        return idx + 1

    # split
    if token == '0':
        x_split = [x_start, (x_start + x_end) // 2, x_end]
        y_split = [y_start, (y_start + y_end) // 2, y_end]
        z_split = [z_start, (z_start + z_end) // 2, z_end]
        for z in (0, 1):
            for y in (0, 1):
                for x in (0, 1):
                    idx = decode_subvolume_recursive(tokens, idx, volume,
                                                 x_split[x], x_split[x + 1],
                                                 y_split[y], y_split[y + 1],
                                                 z_split[z], z_split[z + 1])
        return idx

    raise ValueError(f"Invalid token '{token}' at position {idx-1}")


def decode(resolution: int, data: str, format_version = __LATEST_FORMAT_VERSION) -> np.ndarray:
    """
    Decode a string representing an octree and save it as a bit volume
    """
    if not isinstance(data, str):
        raise TypeError("Provided encoding is not a valid string")

    split_encoding = data.split(" ", 1)
    if len(split_encoding) != 2:
        raise ValueError(
            "The encoding is not properly formatted. See the file format definition https://github.com/eceannmor/octvencode-python."
        )

    resolution, tokens = split_encoding
    try:
        resolution = int(resolution)
    except ValueError:
        raise ValueError(
            f"Passed encoding with invalid resolution. Expected a positive number, received {resolution}."
        )

    if resolution < 1:
        raise ValueError(
            f"Passed encoding with invalid resolution. Expected a positive number, received {resolution}."
        )

    volume = np.zeros((resolution, resolution, resolution), dtype=np.uint8)

    final_idx = decode_subvolume_recursive(tokens, 0, volume, 0, resolution, 0,
                                       resolution, 0, resolution)
    return volume


def to_file(data: str, format_version = __LATEST_FORMAT_VERSION):
    size, data = data.split(" ", 1)
    pad_len = len(data) % 8
    if pad_len:
        pad = '0' * (8 - pad_len)
        data = pad + data
    
    int_data = [int(data[i:i+8], 2) for i in range(0, len(data), 8)]
    byte_data = bytes(int_data)
    
    with open("file.dat", "wb") as f:
        f.write(struct.pack("<H", int(size)))
        f.write(b'\x00')
        f.write(byte_data)

def from_file(filename, format_version = __LATEST_FORMAT_VERSION):
    pass