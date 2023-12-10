#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: pick_utils
@time: 2023/10/31
@contact: ybyang7@iflytek.com
@site:  
@software: PyCharm 

# code is far away from bugs with the god animal protecting
    I love animals. They taste delicious.
              ┏┓      ┏┓
            ┏┛┻━━━┛┻┓
            ┃      ☃      ┃
            ┃  ┳┛  ┗┳  ┃
            ┃      ┻      ┃
            ┗━┓      ┏━┛
                ┃      ┗━━━┓
                ┃  神兽保佑    ┣┓
                ┃　永无BUG！   ┏┛
                ┗┓┓┏━┳┓┏┛
                  ┃┫┫  ┃┫┫
                  ┗┻┛  ┗┻┛ 
"""

#  Copyright (c) 2022. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.
# The original code was taken from the Dask serialization code base.
import struct


def nbytes(frame, _bytes_like=(bytes, bytearray)):
    """Extract number of bytes of a frame or memoryview."""
    if isinstance(frame, _bytes_like):
        return len(frame)
    else:
        try:
            return frame.nbytes
        except AttributeError:
            return len(frame)


def pack_frames_prelude(frames):
    """Pack the `frames` metadata."""
    lengths = [struct.pack("Q", len(frames))] + [
        struct.pack("Q", nbytes(frame)) for frame in frames
    ]
    return b"".join(lengths)


def pack_frames(frames):
    """Pack frames into a byte-like object.

    This prepends length information to the front of the bytes-like object

    See Also
    --------
    unpack_frames
    """
    prelude = [pack_frames_prelude(frames)]

    if not isinstance(frames, list):
        frames = list(frames)

    data_ls = prelude + frames
    data_sz = sum(map(lambda b: len(b), data_ls))
    return data_sz, data_ls


def unpack_frames(b):
    """Unpack bytes into a sequence of frames.

    This assumes that length information is at the front of the bytestring,
    as performed by pack_frames

    See Also
    --------
    pack_frames
    """
    (n_frames,) = struct.unpack("Q", b[:8])

    frames = []
    start = 8 + n_frames * 8
    for i in range(n_frames):
        (length,) = struct.unpack("Q", b[(i + 1) * 8 : (i + 2) * 8])
        frame = b[start : start + length]
        frames.append(frame)
        start += length

    return frames