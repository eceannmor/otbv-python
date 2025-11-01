"""!
@package otbv
@file encoding.py
"""

import numpy as np

from otbv.converter import _is_volume_homogeneous, __convert_or_throw

__all__ = ['encode', 'decode']

def __encode_subvolume_recursive(volume: np.ndarray, x_start: int, x_end: int,
                           y_start: int, y_end: int, z_start: int,
                           z_end: int) -> str:
    """!
    @brief Helper function. Encodes a subvolume. If the subvolume is homogeneous, returns a leaf bit and a value bit, else reterns a split bit as well as the concatenated encodings of all subvolumes of its own. \n The concatenation order is defined by the format.
    @return The encoding of the subvolume
    """

    subvolume = volume[x_start:x_end, y_start:y_end, z_start:z_end]
    assert subvolume.size > 0, f"Encountered a subvolume with a size of 0 when encoding the volume. This should never happen. Parameters: {x_start} {x_end} {y_start} {y_end} {z_start} {z_end}. Please open a new issue and attach the data you are trying to encode. https://github.com/eceannmor/otbv-python/issues"
    if _is_volume_homogeneous(subvolume):
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
                    __encode_subvolume_recursive(volume, x_split[x], x_split[x + 1],
                                           y_split[y], y_split[y + 1],
                                           z_split[z], z_split[z + 1]))
    # slice
    return f"1{"".join(subvolumes)}"


def encode(volume: np.ndarray) -> (int, str):
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

    string = __encode_subvolume_recursive(volume, 0, resolution, 0, resolution, 0,
                                    resolution)
    return resolution, string


def __decode_subvolume_recursive(tokens, idx, volume, x_start, x_end, y_start, y_end,
                           z_start, z_end):
    if idx >= len(tokens):
        raise ValueError("Unexpected end of encoding")
    
    token = tokens[idx]
    idx = idx + 1

    # leaf, read the next value
    if token == '0':
        val = int(tokens[idx])
        volume[x_start:x_end, y_start:y_end, z_start:z_end] = val
        return idx + 1

    # split
    if token == '1':
        x_split = [x_start, (x_start + x_end) // 2, x_end]
        y_split = [y_start, (y_start + y_end) // 2, y_end]
        z_split = [z_start, (z_start + z_end) // 2, z_end]
        for z in (0, 1):
            for y in (0, 1):
                for x in (0, 1):
                    idx = __decode_subvolume_recursive(tokens, idx, volume,
                                                 x_split[x], x_split[x + 1],
                                                 y_split[y], y_split[y + 1],
                                                 z_split[z], z_split[z + 1])
        return idx

    raise ValueError(f"Invalid token '{token}' at position {idx-1}")


def decode(resolution: int, data: str) -> np.ndarray:
    """
    Decode a string representing an octree and save it as a bit volume
    """
    if not isinstance(data, str):
        raise TypeError("Provided encoding is not a valid string")

    if resolution < 1:
        raise ValueError(
            f"Passed encoding with invalid resolution. Expected a positive number, received {resolution}."
        )

    volume = np.zeros((resolution, resolution, resolution), dtype=np.uint8)

    final_idx = __decode_subvolume_recursive(data, 0, volume, 0, resolution, 0,
                                       resolution, 0, resolution)
    return volume

