#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: test_class
@time: 2023/12/10
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
import queue
import threading
import multiprocessing as mp
import time


class InputThread(threading.Thread):
    def __init__(self,send_func,conn):
        threading.Thread.__init__(self)
        self.send = send_func
        self.conn = conn

    def run(self) -> None:
        while True:
            input_text = input("请输入: ")
            self.send(input_text, Message(input_text))
            flag = self.conn.recv()
            print("flag", flag)




class Mprocess(threading.Thread):
    def __init__(self, conns_map):
        threading.Thread.__init__(self)
        self.is_stopping = False
        self.in_q = queue.Queue()
        self.conns_map = conns_map

    def infer(self, req, callback):
        raise NotImplementedError

    def register(self, func):
        self.infer = func

    def send(self, handle, req):
        self.in_q.put((handle, req))

    def run(self):
        while not self.is_stopping:
            handle, req = self.in_q.get()
            self.infer(handle, req)
            conn = self.conns_map["handle-1"]
            conn.send("cccc")
            time.sleep(10)
            print("done")


class ChildMessage():
    def __init__(self):
        self.name = "dog"

    def bark(self):
        print("barking")


class Message():
    def __init__(self,sid):
        self.sid = sid
        self.obj_ = ChildMessage()
    def p(self):
        print(f"sid: {self.sid}")

def f(handle, message):
    print(handle, message)
    message.obj_.bark()
    message.p()




if __name__ == '__main__':
    conn_l, conn_r = mp.Pipe()
    hand1 = "handle-1"
    proc = Mprocess( {hand1: conn_r})

    proc.register(f)
    proc.start()
    p2 = InputThread(proc.send,conn_l)
    p2.start()

