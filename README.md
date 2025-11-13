# python-otbv
Module for reading/writing `.otbv` files. 

OTBV is a file format for compressed binary volumes. <br/>
See formal specifications at [eceannmor.com/OTBV_specification.html](https://eceannmor.com/OTBV_specification.html).

This is a python wrapper around [libotbv](https://github.com/eceannmor/libotbv).

To build, run `install.sh`

To load a given file, use `otbv.load`. The volume is automatically decompressed and reshaped. 
You will receive a 3d array.
```python
>>> volume = otbv.load('samples/test_file.otbv')
>>> volume
[[[False, False], [False, True], [True, False]],
 [[True, True], [True, True], [True, True]],
 [[True, True], [True, True], [True, False]]]
```

To save a 3d volume to a file, use `otbv.save`. The metadata about the volume is stored within the same file for future loads.
```cpp
>>> otbv.save('test.otbv', volume)
```

If you are using flattened volumes, you can pass a 1d data array and the desired resolution. The volume will be automatically reshaped.
```cpp
>>> otbv.save('test_test2.otbv', [0,0,0,0,1,1,1,0], (2,2,2))
```