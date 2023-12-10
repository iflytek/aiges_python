#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: test_shm
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
# !/usr/bin/env python
# coding: utf-8
import sys
import os
import threading
import numpy as np
import multiprocessing as mp
from multiprocessing.shared_memory import SharedMemory,ShareableList
import pickle

class Test:
    def __init__(self,name,age):
        self.name = name
        self.age = age

class Answer:
    def __init__(self,ans):
        self.ans = ans

# https://docs.python.org/3/library/multiprocessing.shared_memory.html

def producer(conn):
    # os.environ["PYTHONWARNINGS"] = "ignore"
    feed_shm_name = '{}_{}_{}'.format(
        'test', os.getpid(), threading.currentThread().ident)
    print('input shm name : {}'.format(feed_shm_name))


    feeds = pickle.dumps(Test('hhccc', 100))
    #fb = bytearray(feeds)
    #feed_shm = SharedMemory( name=feed_shm_name, create=True, size=len(fb))
    feed_shm = ShareableList(feeds,name=feed_shm_name)
    #print("fb: ", len(fb))
    #occupied_size = len(bytes(feed_shm.buf))
    #da#ta_size = feed_shm.buf.itemsize * feed_shm.buf.shape[0]
    #print(occupied_size)

    #f#eed_shm.buf[:feed_shm.size] = fb

    conn.send(feed_shm_name)
    result_shm_name = conn.recv()
    result_shm = ShareableList(name=result_shm_name)
    #result_shm_arr = np.ndarray((1, 2), dtype=np.float32, buffer=result_shm.buf)

    print(result_shm.shm.buf)
    print('Output array : {}'.format(result_shm))

    conn.send('exit')
    #del result_shm_arr
    result_shm.shm.close()

    conn.recv()
    #del feed_shm_arr
    feed_shm.shm.close()
    feed_shm.shm.unlink()

    print('clean and exit')

    return


def consumer(conn):
    # os.environ["PYTHONWARNINGS"] = "ignore"
    result_shm_name = '{}_{}_{}'.format(
        'test', os.getpid(), threading.currentThread().ident)
    print('output shm name : {}'.format(result_shm_name))

    rb =  pickle.dumps(Answer("okkcckkk"))
    bb = bytearray(rb)
    result_shm = mp.shared_memory.ShareableList(rb, name=result_shm_name)

    feed_shm_name = conn.recv()
    feed_shm = mp.shared_memory.ShareableList(name=feed_shm_name)

    print('Input array : {}'.format(feed_shm))

    #result_shm_arr[:] = feed_shm_arr[:]  # fake inference ...
    conn.send(result_shm_name)

    conn.recv()
    #del feed_shm_arr
    feed_shm.shm.close()

    conn.send('exit')
    #del result_shm_arr
    result_shm.shm.close()
    result_shm.shm.unlink()

    print('clean and exit')

    return


def main():
    conn_c, conn_p = mp.Pipe()
    produce_proc = mp.Process(target=producer, args=(conn_p,), daemon=True)
    consume_proc = mp.Process(target=consumer, args=(conn_c,), daemon=True)

    produce_proc.start()
    consume_proc.start()

    produce_proc.join()
    consume_proc.join()


if __name__ == '__main__':
    main()