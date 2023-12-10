#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: test_pickle5
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
# copy from https://github.com/joblib/joblib/issues/1094


from multiprocessing.shared_memory import SharedMemory

import time
import numpy as np
import pickle
import struct
import copy

def store_shm(obj):
    # Pickle the object using out-of-band buffers, pickle 5
    buffers = []
    data = pickle.dumps(
        obj,
        protocol=pickle.HIGHEST_PROTOCOL,
        buffer_callback=lambda b: buffers.append(b.raw()),
    )  # type: ignore

    # Pack the buffers to be written to memory
    data_sz, data_ls = pack_frames([data] + buffers)

    # Create and write to shared memory
    shared_mem = SharedMemory(create=True, size=data_sz)

    write_offset = 0
    for data in data_ls:
        write_end = write_offset + len(data)
        shared_mem.buf[write_offset:write_end] = data  # type: ignore

        write_offset = write_end

    # Clean up
    shared_mem.close()

    return shared_mem.name, data_sz

def read_shm(shared_mem_name, data_sz):
    # Read the shared memory
    shared_mem = SharedMemory(name=shared_mem_name)
    data = shared_mem.buf[:data_sz]

    # Unpack and un-pickle the data buffers
    buffers = unpack_frames(data)
    obj = pickle.loads(buffers[0], buffers=buffers[1:])  # type: ignore

    # Bring the `obj` out of shared memory
    ret = copy.deepcopy(obj)

    # Clean up
    del data
    del buffers
    del obj
    shared_mem.close()
    shared_mem.unlink()
    return ret





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


class Test:
    def __init__(self,name,age):
        self.name = name
        self.age = age

if __name__ == '__main__':

    start_time = time.time()

    # Our big python data object
    big_array = np.arange(5 * 10**7)
    tst = Test("cccc","ddd")
    shared_mem_name, data_sz = store_shm(tst)
    print(shared_mem_name,data_sz)
    obj = read_shm(shared_mem_name, data_sz)

    print("--- Total %s seconds ---" % (time.time() - start_time))

    print(obj.name) # [       0        1        2 ... 49999997 49999998 49999999]
