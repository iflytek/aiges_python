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

DataText = 0  # 文本数据
DataAudio = 1  # 音频数据
DataImage = 2  # 图像数据
DataVideo = 3  # 视频数据

Once = 3


class DataListNode:
    def __init__(self):
        self.key: AnyStr
        self.data: AnyStr
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
    def __init__(self):
        self.key: AnyStr
        self.data: AnyStr
        self.len = 0
        self.type = DataText
        self.status = Once


class Response:
    def __init__(self):
        self.list: List[ResponseData]
        self.errCode = 0

    def response_err(self, errCode: int):
        self.errCode = errCode
        return self
