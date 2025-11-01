"""!
@package otbv
@file converter.py
"""

import numpy as np

__all__ = ['_reshape_volume_to_cubic', '_is_volume_homogeneous']

__ALLOWED_TYPES = (int, float, np.number, bool, np.bool)

def __dtypecheck(dtype) -> bool:
    return dtype in __ALLOWED_TYPES or any([np.issubdtype(dtype, x) for x in __ALLOWED_TYPES])

def __object_typecheck(obj) -> bool:
    return isinstance(obj, __ALLOWED_TYPES)


def __convert_or_throw(o) -> np.ndarray:
    """!
    @brief Attempts to convert \p o into a non-empty NumPy array. \n For detailed data conversion rules, check docs 
    @throws TypeError if the conversion is not possible
    @return \p o represented as a numpy array, if possible
    """
    if isinstance(o, np.ndarray) and __dtypecheck(o.dtype):
        return o
    if __object_typecheck(o):
        return np.array(o)
    try:
        arr = np.asarray(o)
    except:
        raise TypeError("Provided object is not a valid NumPy array and cannot be converted to a NumPy array")
    if arr.dtype == object and all([__object_typecheck(x) or x for x in arr.flat]):
        return arr
    else:
        raise TypeError(f"Provided data is of an unsupported type (received {arr.dtype}, expected {__ALLOWED_TYPES})")
    


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
