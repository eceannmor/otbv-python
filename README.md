# octvencode-python
> *WARNING!* This project is a work-in-progress. If you choose to use it, prepare to deal with all issues that come with it

This is a Python version of the `octvencode` library that I am working on, in parallel to a research project that heavily utilises binary volumes.

This is an encoding algorithm, not a compression one. The binary volume is encoded as an octree, which is itself encoded in binary.

Requires `numpy`

The volume restrictions are as follows:
* Either a cubic volume, OR resizable to a cubic volume.
* The edge length of the final volume is a power of 2
* Only contains data in a form of 0s and 1s, OR data convertible to 0s and 1s (see conversions below).


This project defines the `.octv` (octree volume) file format for encoding the volumes. 
The `0.0.1` version of the `.octv` file format is structured in the following way:
```
00000000  00000000  00000100  00001111  10110000  ...
└──┬───┘  └───────┬────────┘  └┬─┘└─────────┬────────
   ┆              ┆            ┆            ┆
1 byte denoting   ┆       extra padding     ┆
the format      2 bytes denoting      the encoded data
version         the edge length
         (unsigned integer, little endian) 
```
