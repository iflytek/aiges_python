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
from typing import Dict, Tuple, List, AnyStr
import json

from aiges.types import *



class DataListNode:
    def __init__(self):
        self.key: AnyStr = ''
        self.data: AnyStr = ''
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
        self.data = data
        self.len = length
        self.type = type
        self.status = status

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

if __name__ == '__main__':
    t = Response()
    d = ResponseData()
    d.len = 1
    t.list = [d]
    print(t.toJSON())
