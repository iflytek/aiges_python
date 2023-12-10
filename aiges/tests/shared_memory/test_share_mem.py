#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: test_share_mem
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
import multiprocessing as mp
import time

shared_value = mp.Value('i', 0)

def process1(val):
    val.value = 100

def process2(val):
    print(val.value)


def test_vaslue():
    p1 = mp.Process(target=process1, args=(shared_value,))
    p2 = mp.Process(target=process2, args=(shared_value,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()


## manager基本用法

def worker1(d, l):
    d[1] = '1'
    d['2'] = 2
    l.reverse()


def worker2(d, l):
    time.sleep(0.1)
    stop= False
    while not stop:
        print(d)
        print(l)


def test_manager():
    manager = mp.Manager()

    d = manager.dict()
    l = manager.list(range(10))
    f = manager.E


    p1 = mp.Process(target=worker1, args=(d, l))
    p2 = mp.Process(target=worker2, args=(d, l))

    p1.start()

    p2.start()
    p1.join()
    p2.join()

# Event




def wait_for_event(e):
    print("等待事件...")
    e.wait()
    print("收到事件!")



def test_event():
    event = mp.Manager().Event()

    p = mp.Process(target=wait_for_event, args=(event,))
    p.start()

    event.set()  # 触发事件
    p.join()




if __name__ == "__main__":
    # test_vaslue()
    #test_manager()
    test_event()

