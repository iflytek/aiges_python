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
import multiprocessing
from multiprocessing.shared_memory import SharedMemory

import time
import numpy as np
import pickle
import pick_utils
import copy

def sender(obj):
    # Pickle the object using out-of-band buffers, pickle 5
    buffers = []
    data = pickle.dumps(
        obj,
        protocol=pickle.HIGHEST_PROTOCOL,
        buffer_callback=lambda b: buffers.append(b.raw()),
    )  # type: ignore

    # Pack the buffers to be written to memory
    data_sz, data_ls = pick_utils.pack_frames([data] + buffers)

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

def receiver(shared_mem_name, data_sz):
    # Read the shared memory
    shared_mem = SharedMemory(name=shared_mem_name)
    data = shared_mem.buf[:data_sz]

    # Unpack and un-pickle the data buffers
    buffers = pick_utils.unpack_frames(data)
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

class Test:
    def __init__(self,name,age):
        self.name = name
        self.age = age

def read(sh,s):
    obj = receiver(sh,s)
    print(obj)

def test2():
    start_time = time.time()

    # Our big python data object
    big_array = np.arange(5 * 10**7)
    tst = Test("cccc","ddd")
    shared_mem_name, data_sz = sender(tst)
    proc = multiprocessing.Process(target=read, args=(shared_mem_name,data_sz))
    proc.start()
    proc.join()
    print("--- Total %s seconds ---" % (time.time() - start_time))

def test1():
    start_time = time.time()

    # Our big python data object
    big_array = np.arange(5 * 10 ** 7)
    tst = Test("cccc", "ddd")
    shared_mem_name, data_sz = sender(tst)
    obj = receiver(shared_mem_name, data_sz)

    print("--- Total %s seconds ---" % (time.time() - start_time))

    print(obj.name)  # [       0        1        2 ... 49999997 49999998 49999999]


if __name__ == '__main__':
    test2()
    test1()
