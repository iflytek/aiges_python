#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: server
@time: 2022/10/28
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
from concurrent import futures
import logging

import grpc

from aiges.aiges_inner import aiges_inner_pb2

from aiges.aiges_inner import aiges_inner_pb2_grpc


class WrapperServiceServicer(aiges_inner_pb2_grpc.WrapperServiceServicer):
    """Provides methods that implement functionality of route guide server."""

    def __init__(self):
        pass

    def wrapperInit(self, request, context):
        print(request)
        return aiges_inner_pb2.Ret(ret=1)

    def wrapperOnceExec(self, request, context):
        print(request)
        return aiges_inner_pb2.Response(list=[])
        pass

    def testStream(self, request_iterator, context):
        prev_notes = []
        for new_note in request_iterator:
            print (new_note.data)
            prev_notes.append(new_note)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    aiges_inner_pb2_grpc.add_WrapperServiceServicer_to_server(
        WrapperServiceServicer(), server)
    server.add_insecure_port('[::]:50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()