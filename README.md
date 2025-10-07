# octvencode-python
> *WARNING!* This project is a work-in-progress. If you choose to use it, prepare to deal with all issues that come with it

This is a Python version of the `octvencode` library that I am working on, in parallel to a research project that heavily utilises binary volumes.

This is an encoding algorithm, not a compression one. The binary volume is encoded as an octree, which is itself encoded in binary.

The volume restrictions are as follows:
* Non-zero size,
* Exactly 3 dimensions,
* Cubic,
* Edge length is a power of 2,
* Only contains data in a form of 0s and 1s, or data convertible to 0s and 1s.

The volume is encoded as follows:
```
00000000  00000100  00000000  00001111  10110000  ...
└───────┬────────┘  └──┬───┘  └┬─┘└─────────┬──┘
        ┆              ┆       ┆            ┆
2 bytes denoting    a zero   extra padding  ┆
the edge length,    byte                    ┆
unsigned integer,                  the encoded octree
little endian
```
