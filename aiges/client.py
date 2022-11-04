#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: client
@time: 2022/10/29
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
from __future__ import print_function

import logging
import random

import grpc
from aiges.aiges_inner import aiges_inner_pb2
from aiges.aiges_inner import aiges_inner_pb2_grpc


def init(stub):
    ret = stub.wrapperInit(aiges_inner_pb2.InitRequest(config={"ccc": "ddd"}))
    print(ret.ret)


def generate_request():
    messages = [
        "1", "2", "3"
    ]
    for msg in messages:
        print("Sending %s" % (msg))
        yield aiges_inner_pb2.StreamRequest(data=msg)


def make_msg(value, key):
    return aiges_inner_pb2.Request(params={key: value}
                                   )


def generate_messages():
    messages = [
        make_msg("First message", "1" ),
        make_msg("Second message", "2"),
        make_msg("Third message", "3"),
        make_msg("Fourth message", "4"),
        make_msg("Fifth message", "5"),
    ]
    for msg in messages:
       # print("Sending %s at %s" % (msg.message, msg.location))
        yield msg


def testStream(stub):
    ret = stub.testStream(generate_request())
    for response in ret:
        print("Received message %s " %
              (str(response.list)))


def communicatie(stub):
    responses = stub.communicate(generate_messages())
    for response in responses:
        print(response.list)


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50053') as channel:
        stub = aiges_inner_pb2_grpc.WrapperServiceStub(channel)
        print("-------------- InitConfig --------------")
        init(stub)
        print("------testStream------")
        testStream(stub)
        print("------test 双向Stream------")
        communicatie(stub)

if __name__ == '__main__':
    logging.basicConfig()
    run()
