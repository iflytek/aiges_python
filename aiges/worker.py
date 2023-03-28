#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: workers
@time: 2023/03/02
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
import abc
import threading
from abc import ABC
from typing import Any
import queue


class InferClass(ABC):
    @abc.abstractmethod
    def predict(self, *args, **kwargs) -> (object, bool):
        pass

    def setHandle(self, hdl):
        self.handle = hdl


class Worker(threading.Thread):
    def __init__(self, name=None, _type="thread", nums=1,
                 context={}):
        threading.Thread.__init__(self)
        self.name = name
        self._type = _type
        self.nums = nums
        self.context = context
        self.in_q = queue.Queue()
        self.out_q = queue.Queue()
        self.infer_class = None
        self.infer_func = None
        self.callback_fn = None
        self.is_stopping = False

    def stop(self):
        self.is_stopping = True

    def register_infer_class(self, instance):
        if not isinstance(isinstance, InferClass):
            pass
        self.infer_class = instance

    def register_infer_func(self, infer):
        self.infer_func = infer

    def register_callback(self, cb):
        self.callback_fn = cb

    def setHandle(self, hdl):
        self.infer_class.setHandle(hdl)

    def create(self, params={}):
        pass

    def run(self):
        if self.infer_class == None:
            print("not register infer class yet")
        else:
            print("infer class ready")

        while not self.is_stopping:
            try:
                req = self.in_q.get(timeout=3)
            except Exception as e:
                continue
            output, all_done = self.infer_class.predict(req=req)
            if all_done:
                print(" this thread completed...")
                break
            # 一旦这个数据推理完
