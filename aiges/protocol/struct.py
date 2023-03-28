#!/usr/bin/env python
# coding:utf-8
"""
@author: nivic ybyang7
@license: Apache Licence
@file: struct.py
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

from xsf_pb2 import *
from google.protobuf import text_format

PEERADDR = "PeerAddr"


class Data(object):
    def __init__(self, dm: DataMeta):
        self.dm = dm

    def append(self, b):
        self.dm.data += b

    def data(self):
        return self.dm.data

    def set_param(self, k, v):
        self.dm.desc[k] = v

    def get_param(self, k):
        return self.dm.desc[k]


class Req(object):
    def __init__(self, rd: ReqData):
        self.rd = rd

    def set_op(self, op):
        self.rd.op = op

    def size(self):
        if self.rd != None:
            return self.rd.Size()
        return -1

    def get_sess(self):
        return self.rd.s

    def get_peer_ip(self):
        sm = self.get_sess()
        if len(sm) == 0:
            return "", False
        return sm[PEERADDR], True

    def set_req(self, rd: ReqData):
        self.rd = rd

    def set_param(self, k, v):
        if self.rd.param == None:
            self.rd.param = {}
        self.rd.param[k] = v

    def get_param(self, k):
        if k in self.rd.param:
            return self.rd.param[k], True
        return None, False

    def get_all_param(self):
        return self.rd.param

    def append(self, b, desc):
        self.rd.data.append(DataMeta(data=b, desc=desc))

    def append_data(self, d: Data):
        self.rd.data.append(d.dm)

    def session(self, s: str):
        sess = Session()
        text_format.Parse(s, sess)
        if self.rd.s != None and len(self.rd.s.t) > 0:
            sess.t = self.rd.s.t
        if self.rd.s.sess != None:
            sess.sess = self.rd.s.sess
        self.rd.S = sess

    # 追加session描述
    def append_session(self, k, v):
        if self.rd.s.sess == None:
            self.rd.s.sess = {}
        self.rd.s.sess[k] = v

    def set_handle(self, handle):
        self.rd.s.h = handle

    def handle(self):
        if self.rd.s == None:
            return ""
        return self.rd.s.h

    def set_trace_id(self,i):
        self.rd.s.t = i

    def trace_id(self):
        if self.rd.s == None:
            return ""
        return self.rd.s.t

    def req(self):
        return self.rd

    def op(self):
        return self.rd.op

    def data(self):
        dm = Data()
        emty = True
    #todo
    #todo

class Res(object):
    def __init__(self, rs: ResData):
        self.rd = rs


def NewReq():
    rd = ReqData(s=Session(sess={}), param={})
    req = Req(rd)
    return req


def NewData():
    dm = DataMeta(desc={})
    d = Data(dm)


def NewRes():
    rd = ResData(s=Session(sess={}), param={})
    rs = Res(rd)
    return rs


if __name__ == '__main__':
    a = NewReq()
    print(a.get_sess())
