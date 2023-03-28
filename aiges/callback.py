#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: callback
@time: 2023/03/03
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

from aiges.utils.log import getFileLogger
from aiges.dto import Response
from aiges.aiges_inner import aiges_inner_pb2

q: queue.Queue = None
log = getFileLogger()

def set_up(_q):
    log.debug("seting up the response queue")
    global q
    q = _q


def callback(user_resp: Response, handle: str, sid: str):
    global q

    d_list = []
    for ur in user_resp.list:
        d = aiges_inner_pb2.ResponseData(key=ur.key, data=ur.data, len=ur.len, status=ur.status)
        d_list.append(d)
    r = aiges_inner_pb2.Response(list=d_list, tag=handle)
    if q == None:
        log.error("response queue must be initialize... ")
        return
    q.put(r)
