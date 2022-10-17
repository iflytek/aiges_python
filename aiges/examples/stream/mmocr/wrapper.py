#!/usr/bin/env python
# coding:utf-8
"""
@license: Apache License2
@file: wrapper.py
@time: 2022-08-03 09:41:20.346690
@project: mmocr_v2
@project: ./
"""

import sys
import hashlib
import time

try:
    from aiges_embed import ResponseData, Response, DataListNode, DataListCls, SessionCreateResponse, callback  # c++
except:
    from aiges.dto import Response, ResponseData, DataListNode, DataListCls

from aiges.sdk import WrapperBase, \
    StringParamField, \
    ImageBodyField, \
    StringBodyField

from aiges.stream import StreamHandleThread

from aiges.utils.log import log
from aiges.types import *

########
# 请在此区域导入您的依赖库

# Todo
# for example: import numpy
import numpy as np
from PIL import Image
import io
from mmocr.utils.ocr import MMOCR
import json

########


"""
定义请求类:
 params:  params 开头的属性代表最终HTTP协议中的功能参数parameters部分，
          params Field支持 StringParamField，
          NumberParamField，BooleanParamField,IntegerParamField，每个字段均支持枚举
          params 属性多用于协议中的控制字段，请求body字段不属于params范畴

 input:    input字段多用与请求数据段，即body部分，当前支持 ImageBodyField, StringBodyField, 和AudioBodyField
"""


class UserRequest(object):
    # StringParamField多用于控制参数
    # 指明 enums, maxLength, required有助于自动根据要求配置协议schema
    # params1 = StringParamField(key="p1", enums=["3", "eee"], value='3')
    # params2 = StringParamField(key="p2", maxLength=44, required=True)
    # params3 = StringParamField(key="p3", maxLength=44, required=False)

    # imagebodyfield 指明path，有助于本地调试wrapper.py
    input1 = ImageBodyField(key="data", path="demo/demo_text_det.jpg")
    # input3 = ImageBodyField(key="data2", path="test_data/test.png")
    # stringbodyfiled 指明 value，用于本地调试时的测试值
    # input2 = StringBodyField(key="switch", value="ctrl")


"""
定义响应类:
 accepts:  accepts代表响应中包含哪些字段, 以及数据类型

 input:    input字段多用与请求数据段，即body部分，当前支持 ImageBodyField, StringBodyField, 和AudioBodyField
"""


class UserResponse(object):
    # 此类定义响应返回数据段，请务必指明对应key
    # 支持 ImageBodyField， AudioBodyField,  StringBodyField
    # 如果响应是json， 请使用StringBodyField
    accept1 = StringBodyField(key="boxes")


class Wrapper(WrapperBase):
    """
    用户实现， 名称必须为Wrapper, 必须继承SDK中的 WrapperBase类
    """
    serviceId = "mmocr"
    version = "backup.0"
    requestCls = UserRequest()
    responseCls = UserResponse()

    mode = None
    session_total = 0  # 单进程总会话数量控制，过大会影响效率，请合理控制

    def wrapperInit(self, config: {}) -> int:
        """
        服务初始化
        @param config:
            插件初始化需要的一些配置，字典类型
            key: 配置名
            value: 配置的值
        @return
            ret: 错误码。无错误时返回0
        """
        log.info(config)
        Wrapper.model = MMOCR()
        log.info("Initializing ...")
        Wrapper.session_total = config.get("common.lic", 10)
        self.session.init_wrapper_config(config)
        self.session.init_handle_pool("thread", 10, MyReqDataThread)
        return 0

    def wrapperOnceExec(cls, params: {}, reqData: DataListCls) -> Response:
        """
        非会话模式计算接口,对应oneShot请求,可能存在并发调用
        @param params 功能参数
        @param  reqData     请求数据实体字段 DataListCls,可通过 aiges.dto.DataListCls查看
        @return
            响应必须返回 Response类，非Response类将会引起未知错误
        """
        return None

    def wrapperFini(cls) -> int:
        """
        服务逆初始化

        @return
            ret:错误码。无错误码时返回0
        """
        log.info("fini success")
        return 0

    def wrapperError(cls, ret: int) -> str:

        if ret == 10013:
            return "reqData is empty"
        elif ret == 10001:
            return "load onnx model failed"
        else:
            return "other error code"

    def wrapperCreate(self, params: {}, sid: str) -> SessionCreateResponse:
        """
        非会话模式计算接口,对应oneShot请求,可能存在并发调用
        @param ret wrapperOnceExec返回的response中的error_code 将会被自动传入本函数并通过http响应返回给最终用户
        @return
            SessionCreateResponse类, 如果返回不是该类会报错
        """
        s = SessionCreateResponse()
        # 这里是取 handle
        handle = self.session.get_idle_handle()
        if not handle:
            s.error_code = -1
            s.handle = ""
            return s

        _session = self.session.get_session(handle=handle)
        if _session == None:
            log.info("can't create this handle:" % handle)
            return -1
        _session.setup_sid(sid)
        _session.setup_params(params)
        _session.setup_callback_fn(callback)

        print(sid)
        s = SessionCreateResponse()
        s.handle = handle
        s.error_code = 0
        return s

    def wrapperWrite(self, handle: str, req: DataListCls, sid: str) -> int:
        """
        会话模式下: 上行数据写入接口

        :param handle: 会话handle 字符串
        :param req:  请求数据结构
        :param sid:  请求会话ID
        :return:
        """
        _session = self.session.get_session(handle=handle)
        if _session == None:
            log.info("can't get this handle:" % handle)
            return -1
        _session.in_q.put(req)
        return 0

    def wrapperRead(self, handle: str, sid: str) -> Response:
        """
        会话模式: 当前此接口在会话模式且异步取结果时下不会被调用！！！！！返回数据由callback返回
        同步取结果模式时，下行数据返回接口
                  如果为异步返回结果时，需要设置加载器为asyncMode=true [当前默认此模式],
        :param handle: 请求数据结构
        :param sid: 请求会话ID
        :return: Response类
        """
        _session = self.session.get_session(handle=handle)
        r = Response()
        l = ResponseData()
        if _session.out_q.empty():
            l.status = 1
            l.len = 0
            l.data = b''
            l.key = "boxes"
            r.list = [l]
            return r
        rs = _session.out_q.get()
        if rs.list[0].status == DataEnd:
            print("########Done")
            _session.reset()
        if not isinstance(rs, Response):
            raise Exception("check response")

        return rs

    def wrapperTestFunc(cls, data: [], respData: []):
        """
        此函数保留测试用，不可删除
        :param data:
        :param respData:
        :return:
        """

        r = Response()
        l = ResponseData()
        l.key = "boxes"
        l.status = 1
        d = open("pybind11/docs/pybind11-logo.png", "rb").read()
        l.len = len(d)
        l.data = d
        r.list = [l, l, l]

        print(r.list)
        print(444)
        return r


class MyReqDataThread(StreamHandleThread):
    """
    流式示例 thread，
    """

    def __init__(self, session_thread, in_q, out_q):
        super().__init__(session_thread, in_q, out_q)

    def run(self):
        while True:
            req = self.in_q.get()
            print(self.session_thread.params)
            self.infer(req)

    def infer(self, req: DataListCls):
        print("data list size,", len(req.list))
        print(req.list[0].len)
        print(req.list[0].status)
        r = Response()
        l = ResponseData()
        l.key = "boxes"
        l.status = req.list[0].status
        d = open("/home/mmocr/resources/mmocr-logo.png", "rb").read()
        # d = b"ccccccc"
        l.len = len(d)
        l.data = d
        r.list = [l]
        self.session_thread.callback_fn(r, self.session_thread.sid)
        if l.status == DataEnd:
            self.session_thread.reset()  # 最后一帧数据后 释放会话
        # self.out_q.put(r)

    def init_model(self, *args, **kwargs):
        model = None
        return model


if __name__ == '__main__':
    m = Wrapper()
    # m.schema()
    m.run()
