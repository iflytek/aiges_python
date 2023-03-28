#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: dto
@time: 2022/07/26
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
from typing import Dict, Tuple, List, AnyStr
import json

from aiges.core.types import *


class DataListNode:
    def __init__(self):
        self.key: AnyStr = ''
        self.data: AnyStr = ''
        self.status = Once
        self.len = 0
        self.type = DataText


class DataListCls:
    def __init__(self):
        self.list: List[DataListNode]

    def get(self, key: str):
        for d in self.list:
            if d.key == key:
                return d
        return None


class ResponseData:
    def __init__(self, key='', data='', length=0, type=DataText, status=Once):
        self.key = key
        self._len = 0
        self.type = type
        self.status = status
        self._data = b""

    @property
    def data(self):
        return self._data

    @property
    def len(self):
        return self._len

    def setDataType(self, t):
        if not t in [DataText, DataAudio, DataImage, DataVideo]:
            raise Exception("Please specify the correct data type...")
        self.type = t

    def setData(self, d):
        self._data = d
        self._len = len(d)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class Response:
    def __init__(self):
        self.list: List[ResponseData] = [ResponseData()]
        self.error_code = 0

    def response_err(self, error_code: int):
        self.error_code = error_code
        return self

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class SessionCreateResponse:
    def __init__(self):
        self.handle = ""
        self.error_code = 0

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


result_Queue = None


def init_rq():
    global result_Queue
    result_Queue = queue.Queue()
    return result_Queue


def callback(r: Response, sid: str):
    global result_Queue
    if not result_Queue:
        raise Exception("you should execute init_rq first")
    for nod in r.list:
        print("sid %s, get callback: %s: len %d, type: %s, status: %s" % (
            sid, nod.key, nod.len, Types[nod.type], Status[nod.status]))
    result_Queue.put(r)


if __name__ == '__main__':
    t = Response()
    d = ResponseData()
    d.len = 1
    t.list = [d]
    print(t.toJSON())
