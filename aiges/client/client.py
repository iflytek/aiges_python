#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: client
@time: 2022/11/13
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


from aiges.client.utils.aipass_client import execute
from aiges.client.utils.ne_utils import build_auth_request_url, get_file_bytes
from aiges.utils.log import log
import base64
import copy
from urllib import parse
import requests
import json
import jsonpath_rw
import os

media_type_list = ["text", "audio", "image", "video"]

config_dict = [
    {
        "model_name": "VOICE2VEC",
        "api_key": "",
        "api_secret": "",
        "app_id": "",
        "method": ""
    }
]




class Client(object):
    def __init__(self, model, api_key, api_secret, app_id, method="POST"):
        self.init_model(model)
        self.api_key = api_key
        self.api_secret = api_secret
        self.app_id = app_id
        self.method = method
        pass

    def init_model(self, model):
        if model not in models:
            raise NoSuchModelError("no such this model: %s" % model)
        self.input_tpl = InputData(model)

        # 初始化client对象 schema输入
        if model == VOICE2VEC:
            self.api_url = VOICE2VEC_URL
            self.res_path_list = ['$..payload.fea_image', '$..payload.fea', '$..payload.fbank_image', ]

        elif model == AV2VEC:
            self.api_url = AV2VEC_URL
            self.res_path_list = ['$..payload.fea_image', '$..payload.feature', ]

    def execute(self, **kwargs):
        request_url = self.api_url
        app_id = self.app_id
        api_secret = self.api_secret
        api_key = self.api_key
        # 获取请求url
        auth_request_url = build_auth_request_url(request_url, self.method, api_key, api_secret)

        url_result = parse.urlparse(request_url)
        headers = {'content-type': "application/json", 'host': url_result.hostname, 'app_id': app_id}
        request_data = self.input_tpl.prepare(**kwargs)
        # 程序启动的时候设置APPID
        request_data['header']['app_id'] = self.app_id
        # 准备待发送的数据
        new_request_data = self.prepare_req_data(request_data)

        # execute(self.api_url, request_data, "POST", APPId, APIKey, APISecret)
        response = requests.post(auth_request_url, data=json.dumps(new_request_data), headers=headers)
        return self.do_response(response)

    # 准备请求数据
    def prepare_req_data(self, request_data):
        new_request_data = copy.deepcopy(request_data)
        media_path2name = {}
        for media_type in media_type_list:
            media_expr = jsonpath_rw.parse("$..payload.*.{}".format(media_type))
            media_match = media_expr.find(new_request_data)
            if len(media_match) > 0:
                for media in media_match:
                    media_path2name[str(media.full_path)] = media.value
        for media_path, media_name in media_path2name.items():
            payload_path_list = media_path.split(".")
            f_data = get_file_bytes(media_name)
            new_request_data['header']['status'] = 3
            new_request_data['payload'][payload_path_list[1]][payload_path_list[2]] = base64.b64encode(f_data).decode()
            new_request_data['payload'][payload_path_list[1]]['status'] = 3
        return new_request_data

    def do_response(self, response):
        res = {"code": 0, "msg": "", "data": None}
        temp_result = json.loads(response.content.decode())
        log.debug("响应数据:{}\n".format(temp_result))
        header = temp_result.get('header')
        if header is None:
            res["code"] = response.status_code
            msg = "header为空:%s " % response.content
            if response.status_code == 401:
                msg += "\n请检查授权apikey,secret,app_id配置"
            res["msg"] = msg
            return res

        code = header.get('code')
        if header is None or code != 0:
            msg = "获取结果失败，请根据code查证问题原因, code: %s" % code
            log.error(msg)
            res["code"] = -1
            res["msg"] = msg
            return res
        log.info("sid:{}".format(header.get('sid')))
        data = {}
        for response_path in self.res_path_list:
            response_expr = jsonpath_rw.parse(response_path)
            response_match = response_expr.find(temp_result)
            if len(response_match) > 0:
                for response_item in response_match:
                    if response_item.value is None:
                        continue
                    encoding = response_item.value.get('encoding')
                    if encoding is None or len(encoding) == 0:
                        continue
                    for media_type in media_type_list:
                        media_value = response_item.value.get(media_type)
                        if media_value is None or len(media_value) == 0:
                            continue
                        real_data = base64.b64decode(media_value)
                        response_path_split_list = response_path.split('.')
                        data[response_path_split_list[-1]] = real_data
        return data