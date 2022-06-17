#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: wrapper.py
@time: 2022/06/16
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
import sys

if not hasattr(sys, 'argv'):
    sys.argv = ['']

'''
服务初始化
@param config:
    插件初始化需要的一些配置，字典类型
    key: 配置名
    value: 配置的值
@return
    ret: 错误码。无错误时返回0
'''


def wrapperInit(config: {}) -> int:
    return 0


'''
服务逆初始化

@return
    ret:错误码。无错误码时返回0
'''


def wrapperFini() -> int:
    return 0


'''
非会话模式计算接口,对应oneShot请求,可能存在并发调用

@param usrTag 句柄
#param params 功能参数
@param  reqData     写入数据实体
@param  respData    返回结果实体,内存由底层服务层申请维护,通过execFree()接口释放
@param psrIds 需要使用的个性化资源标识列表
@param psrCnt 需要使用的个性化资源个数

@return 接口错误码
    reqDat
    ret:错误码。无错误码时返回0
'''


def wrapperOnceExec(usrTag: str, params: {}, reqData: [], respData: [], psrIds: [], psrCnt: int) -> int:
    print("hello world")
    print(usrTag)
    print(params)
    print(reqData)
    print(psrIds)
    print(psrCnt)
    return 100


def wrapperCreate(usrTag: str, params: [], psrIds: [], psrCnt: int) -> str:
    return ""


def wrapperWrite(handle: str, datas: []) -> int:
    return 0


def wrapperRead(handle: str) -> []:
    return []


def wrapperDestroy(handle: str) -> int:
    return 0


def wrapperError(ret: int) -> str:
    if ret == 100:
        return "this is a tese error return"
    return ""


class InputField(object):
    def __init__(self, key, dataType="string", max=None, min=None, choices=[]):
        self.data_type = dataType
        self.key = key
        if max != None:
            self.max = None
        if min != None:
            self.min = None
        if choices != []:
            self.choices = None


from proto import  AseProto,StringField

class UserRequest(object):
    input1 = StringField("image", key="data", path="./1xml")
    input2 = StringField("string", key="switch")


class UserResponse(object):
    accept1 = StringField("string", key="boxes")


class Metadata(AseProto):
    serviceId = "mmocr"
    version = "v2.0"
    call = "atmos"
    requestCls = UserRequest()
    responseCls = UserResponse()

def run():
    exec()

if __name__ == '__main__':
    m = Metadata()
    print(m.schema())
