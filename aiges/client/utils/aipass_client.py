#! /usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/04/29 08:52:23
# @Author  : daocoder
# @Email   : daocoder@foxmail.com


import jsonpath
import base64
import threading
import copy
import chardet
import requests
import os
import hashlib
import time
import json
import ne_utils, h26x_client
import logging
import exception
from websocket import create_connection
from urllib.parse import urlparse, urlencode
from jsonpath_rw.parser import parse


app_key = "app_key"
app_secret = "app_secret"

class WsClient:
    def __init__(self, url, r_data, **options):
        if options.get('log'):
            self.log = options['log']
        else:
            self.log = logging
        self.req_param = copy.deepcopy(r_data)
        self.req_data = {
            "header": r_data['header'],
            "parameter": r_data['parameter'],
            "payload": r_data['payload'],
        }
        self.opt = options
        self.r_url = url
        stream_mode = options.pop("stream_mode", False)
        self.stream_mode = stream_mode
        self.key = options.pop("key", None)
        if self.key is None:
            self.key = app_key
        self.secret = options.pop("secret", None)
        if self.secret is None:
            self.secret = app_secret
        self.r_url_dict = urlparse(url)
        self.r_date = ne_utils.get_formate_date()
        self.sid = ""
        self.result_list = []
        self.origin_result_list = []
        self.error_code = 0
        self.uid = options.get("uid", None)
        self.msg = "success"
        # 写入音频总时间
        self.write_data_time = 0
        # 写第一块音频时间
        self.write_1_time = 0
        self.consume_1_time = 0
        # 写最后一块音频时间
        self.write_4_time = 0
        self.consume_4_time = 0
        self.save_path = {}
        self.file_md5 = {}
        self.save_to_file = options.get("save_to_file", True)
        self.extra = r_data.get("extra", {})
        # 设置视频帧率：
        self.frame_rate = None
        if jsonpath.jsonpath(self.req_data, "$.payload.*.frame_rate"):
            self.frame_rate = jsonpath.jsonpath(self.req_data, "$.payload.*.frame_rate")[0]
        # 设置时间间隔，毫秒，优先级：extra.time_interval > $.payload.*.frame_rate > 默认值40
        # 时间间隔暂不由用户传入，故注释如下部分：
        if self.frame_rate:
            self.time_interval = round((1 / self.frame_rate) * 1000)
        else:
            self.time_interval = 40
        self.time_interval_audio = self.time_interval
        self.log.info("time_interval: {}ms".format(self.time_interval))
        exist_audio = jsonpath.jsonpath(self.req_data, "$.payload.*.audio")
        exist_video = jsonpath.jsonpath(self.req_data, "$.payload.*.video")
        self.multimode = True if exist_audio and exist_video else False
        self.log.info("multimode: {}".format(self.multimode))

    def get_connect_url(self):
        auth_digest = ne_utils.get_kong_auth(self.r_url, self.r_date, key=self.key, secret=self.secret)
        handshake_params = {
            "authorization": auth_digest,
            "date": self.r_date,
            "host": self.r_url_dict.netloc
        }
        if self.stream_mode:
            handshake_params['stream_mode'] = "multiplex"
        handshake_url = self.r_url + "?" + urlencode(handshake_params)
        return handshake_url

    def connect(self, **opt):
        c_url = self.get_connect_url()
        self.ws = None
        try:
            self.ws = create_connection(c_url, **opt)
        except Exception as error:
            shake_error = "handshake error: {}".format(str(error))
            self.log.error(shake_error)
            self.set_message(shake_error)
            self.error_code = exception.WebCode.RemoteReqError
        return self.ws

    def send_data(self, func_name, argv, kw):
        """
        利用多线程，后台发送数据，不等待，直接下步循环获取结果
        单放出来，避免与业务逻辑参杂，其它业务可复用
        错误出现时，线程退出，主线程进行获取结果等待
        :param func_name: method name
        :param argv: (arg1, arg2)
        :param kw: {"key": "name"}
        :return: None
        """
        if type(func_name).__name__ == "str" and hasattr(self, func_name):
            func = getattr(self, func_name)
        else:
            func = func_name
        t = threading.Thread(target=func, args=argv, kwargs=kw)
        t.start()
        # t.join()

    def prepare_req_data(self):
        """
            读取多通道数据
            media_path2data = {
                "payload.txt.text": "/sb3f8a020/1584670207/language.txt"
            }
        """
        media_type_list = ["text", "audio", "image", "video"]
        media_path2name = media_path2data = {}
        for media_type in media_type_list:
            media_expr = parse("$..payload.*.{}".format(media_type))
            media_match = media_expr.find(self.req_param)
            if len(media_match) > 0:
                for media in media_match:
                    media_path2name[str(media.full_path)] = media.value
        self.log.debug(media_path2name)
        for media_path, media_name in media_path2name.items():
            media_var_name = media_path.split(".")[1]
            media_status = jsonpath.jsonpath(self.req_param, expr="$..payload.{}.status".format(media_var_name))
            if media_status and media_status[0] == 3:
                media_path2data[media_path] = self.prepare_ws_data_once(media_path, media_name)
            else:
                media_path2data[media_path] = self.prepare_ws_data(media_path, media_name)
        return media_path2data

    def prepare_ws_data(self, media_name, payload_path):
        """
        准备数据 目标 media_list 形式 为写数据做准备 wav_length 单位 字节 Byte
         {
            "payload.*.audio": [[centent, audio_status_py, wav_length], [...]],
            "payload.*.text": [[centent, audio_status_py, wav_length], [...]],
                ...
        }
        """
        if self.stream_mode:
            cid = self.req_data["header"].get("cid", 0)
            self.req_data["header"]['cid'] = str(int(cid) + 1)
        media_data_list = []
        payload_path_list = media_name.split(".")
        try:
            # fixme 根据请求数据获取对应的发包策略
            payload = ne_utils.get_file_bytes(payload_path)
            var_name = payload_path_list[1]
            var_info = jsonpath.jsonpath(self.req_data, "$.payload.{}".format(var_name))[0]
            encoding = var_info.get("encoding")
            if payload_path_list[2] in ["audio"]:
                frame_size_tmp = var_info.get("frame_size")
                if encoding is not None and encoding.startswith("speex"):
                    if frame_size_tmp is None or frame_size_tmp <= 0:
                        self.log.info("[aipaas client] update frame_size: {} -> 60".format(frame_size_tmp))
                        self.req_data["payload"][var_name]["frame_size"] = 60
                        var_info["frame_size"] = 60
                if encoding in ["opus", "opus-wb"]:
                    media_data_list = ne_utils.build_stream_data(payload, 122, True)
                elif encoding in ["ico"]:
                    media_data_list = ne_utils.build_stream_data(payload, 120, True)
                else:
                    media_data_list = ne_utils.build_stream_data(payload, 1280, True)
                self.time_interval_audio = media_data_list[0][3]
                self.log.info("audio media_data_list len: {}".format(len(media_data_list)))
                self.log.info("time_interval_audio: {}".format(self.time_interval_audio))
            elif payload_path_list[2] in ["text"]:
                media_data_list = ne_utils.build_stream_data_text(payload, True)
                self.log.info("text media_data_list len: {}".format(len(media_data_list)))
            elif payload_path_list[2] in ["image"]:
                media_data_list = ne_utils.build_stream_data_image(payload, True)
            elif payload_path_list[2] in ["video"]:
                payload = ne_utils.get_file_bytes(payload_path)
                ex = h26x_client.H26xParser(None, use_bitstream=payload)
                media_data_list = ex.h264_data_list()
                self.log.info("video media_data_list len: {}".format(len(media_data_list)))
        except Exception as e:
            self.set_message(str(e))
            self.error_code = exception.WebCode.RemoteReqError
        return media_data_list

    def prepare_ws_data_once(self, media_name, payload_path):
        """
        准备数据 目标 media_list 形式 为写数据做准备 wav_length 单位 字节 Byte
         {
            "payload.*.audio": [[centent, audio_status_py, wav_length]],
            "payload.*.text": [[centent, audio_status_py, wav_length]],
                ...
        }
        """
        if self.stream_mode:
            cid = self.req_data["header"].get("cid", 0)
            self.req_data["header"]['cid'] = str(int(cid) + 1)
        media_data_list = []
        payload_path_list = media_name.split(".")
        try:
            # 一次性读取，pop出write_len
            payload = ne_utils.get_file_bytes(payload_path)
            self.req_data[payload_path_list[0]][payload_path_list[1]].pop("write_len", 122)
            media_data_list = ne_utils.build_stream_data(payload, 2333, True)
            # 修改payload status为3
            for media_data in media_data_list:
                media_data[1] = 3
        except Exception as e:
            self.set_message(str(e))
            self.error_code = exception.WebCode.RemoteReqError
        return media_data_list

    def write_ws_stream(self, *args, **kw):
        """
        多通道流媒体写入
        :param args:
            {
                "payload.*.audio": [[centent, audio_status_py, wav_length], [...]],
                "payload.*.text": [[centent, audio_status_py, wav_length], [...]],
                ...
            }
            audio_status_py == -1 时，视频为协议帧，不进行时间戳同步
        :param kw: kwargs 其它参数：
            time_interval 写数据频率
            multimode 多模态与否
        :return:
        """
        media_list = args[0]
        # fixme 根据条件进行发包策略调整
        # time_interval = kw.get("time_interval", 40)
        # multimode = kw.get("multimode", False)
        length_list = [len(media) for media in media_list.values()]
        max_length = max(length_list)
        write_str = "media list length {}, begin write media.".format(len(length_list))
        self.log.info(write_str)
        syn_video_timestamp = syn_audio_timestamp = int(time.time() * 1e3)
        for i in range(max_length):
            header_status = []
            for media_path, media_content_list in media_list.items():
                payload_path_list = media_path.split(".")
                # 多通道分别进行数据填充
                media_content_loop = len(media_content_list) - 1
                if i <= media_content_loop:
                    f_content = media_content_list[i][0]
                    f_status = media_content_list[i][1]
                    header_status.append(f_status)
                    f_len = media_content_list[i][2]
                    # fixme 按照音视频进行时间戳对齐
                    if payload_path_list[2] in ["audio", "video"]:
                        self.req_data['payload'][payload_path_list[1]][payload_path_list[2]] = base64.b64encode(
                            f_content).decode()
                        self.req_data['payload'][payload_path_list[1]]['status'] = f_status
                        if payload_path_list[2] == "video":
                            # fixme 获取帧率 取得时间戳
                            # syn_video_timestamp = syn_video_timestamp + 40
                            if self.req_data['payload'][payload_path_list[1]].get("seq", None) is not None:
                                self.req_data['payload'][payload_path_list[1]]['seq'] = i
                            tm = jsonpath.jsonpath(self.req_data, "$.payload.{}.timestamp".format(payload_path_list[1]))
                            if self.multimode or tm:
                                syn_video_timestamp = syn_video_timestamp + self.time_interval
                                self.req_data['payload'][payload_path_list[1]]['timestamp'] = str(syn_video_timestamp)
                                self.log.debug("video timestamp: {}".format(syn_video_timestamp))
                                self.log.debug("video seq: {}, len: {}".format(i, f_len))
                        else:
                            # fixme 音频固定时间戳
                            # syn_audio_timestamp = syn_audio_timestamp + 40
                            if self.req_data['payload'][payload_path_list[1]].get("seq", None) is not None:
                                self.req_data['payload'][payload_path_list[1]]['seq'] = i
                            tm = jsonpath.jsonpath(self.req_data, "$.payload.{}.timestamp".format(payload_path_list[1]))
                            if self.multimode or tm:
                                syn_audio_timestamp = syn_audio_timestamp + self.time_interval_audio
                                self.req_data['payload'][payload_path_list[1]]['timestamp'] = str(syn_audio_timestamp)
                                self.log.debug("audio timestamp: {}".format(syn_audio_timestamp))
                    else:
                        charset_dict = chardet.detect(f_content)
                        self.req_data['payload'][payload_path_list[1]][payload_path_list[2]] = base64.b64encode(
                            f_content).decode()
                        self.req_data['payload'][payload_path_list[1]]['status'] = f_status
                        if self.req_data['payload'][payload_path_list[1]].get("seq", None) is not None:
                            self.req_data['payload'][payload_path_list[1]]['seq'] = i
                else:
                    # 发送完毕后进行单通道数据剔除
                    media_channel = self.req_data['payload'].pop(payload_path_list[1], None)
                    if media_channel is not None:
                        self.log.debug("fucking debug, media_channel key is %s.", payload_path_list[1])
            i = i + 1
            self.log.debug("fucking debug, header_status and i: %s %s.", header_status, i)
            # 头状态位以多通道数据状态位保持一致，取最小值。[0, 1, 2]
            self.req_data['header']['status'] = min(header_status)
            # payload status为3 修改header status为2
            if self.req_data['header']['status'] == 3:
                self.req_data['header']['status'] = 2
            req_params_str = json.dumps(self.req_data)
            if self.error_code != 0:
                return
            try:
                # 发送成功会返回数据总长度，必要可进行数据长度观测
                write_length = self.ws.send(req_params_str)
                if i % 10 == 0:
                    self.log.debug(self.req_data)
            except Exception as e:
                self.log.error("some thing wrong in write data: %s.", str(e))
                self.set_message(str(e))
                return
            # 首音频0 中间音频1 尾音频2
            header_status = self.req_data['header']['status']
            if header_status == 0:
                # 会话发送数据开始时间
                self.write_1_time = time.time()
            # payload status为3 一次性发送完
            if i == 1 and header_status == 2:
                self.write_1_time = time.time()
            if header_status == 2:
                # 会话发送数据结束时间
                self.write_4_time = time.time()
                self.log.info("write data end: write the last %d data.", i)
            # fixme 帧率不同，发送等待时间不同
            if self.multimode:
                sleep_time = max(self.time_interval, self.time_interval_audio) / 1000
                self.log.debug("sleep: {}s".format(sleep_time))
                time.sleep(sleep_time)
            elif self.time_interval != self.time_interval_audio:
                sleep_time = self.time_interval_audio / 1000
                self.log.debug("sleep: {}s".format(sleep_time))
                time.sleep(sleep_time)
            else:
                time.sleep(0.04)

    def do_ws_request(self):
        media_path2data = self.prepare_req_data()
        self.log.debug(media_path2data)
        self.write_ws_stream(media_path2data)

    def handle_result(self):
        if not jsonpath.jsonpath(self.origin_result_list, '$..payload'):
            self.log.info("There have no payload info in the origin result list.")
            return

        media_type_list = ["text", "audio", "image", "video"]
        media_name2data = {}
        # {'value_name1': {'data': [XX, XX...], 'media_type': XX, 'encoding': XX}}, 'value_name2': {......}}
        try:
            for media_type in media_type_list:
                media_expr = parse("$..payload.*.{}".format(media_type))
                media_match = media_expr.find(self.origin_result_list)
                if len(media_match) > 0:
                    for media in media_match:
                        path = str(media.full_path)
                        data = media.value
                        value_name = path.split(".")[-2]
                        if media_name2data.get(value_name, None):
                            media_name2data[value_name]['data'].append(data)
                        else:
                            media_name2data[value_name] = {}
                            media_name2data[value_name]['data'] = [data]
                            media_name2data[value_name]['media_type'] = media_type
                            encoding = jsonpath.jsonpath(self.origin_result_list,
                                                         '$..payload.{}.encoding'.format(value_name))
                            # 编排场景下输入数据不规范，不能强依赖用户输入
                            if encoding:
                                media_name2data[value_name]['encoding'] = encoding[0]
                            else:
                                media_name2data[value_name]['encoding'] = "utf8"
            self.log.debug(media_name2data)
        except Exception as e:
            self.log.error("get payload data from result fail: %s", str(e))
            self.set_message(str(e))

        try:
            for value_name, data_info in media_name2data.items():
                md5_hash = hashlib.md5()
                feh_res = bytes()
                encoding = data_info['encoding']
                media_type = data_info['media_type']
                for data in data_info['data']:
                    date_byte = base64.b64decode(data)
                    md5_hash.update(date_byte)
                    feh_res = feh_res + date_byte
                file_md5 = md5_hash.hexdigest()

                media_path = "../resource/aipaas/{}".format(media_type)
                if not os.path.isdir(media_path):
                    os.makedirs(media_path)
                save_path = "{}/{}.{}".format(media_path, file_md5, encoding)
                fp = open(save_path, 'wb')
                fp.write(feh_res)
                fp.close()
                self.file_md5[value_name] = file_md5
                self.save_path[value_name] = save_path
                self.log.info("The payload data is saved in this path: {}".format(save_path))
        except Exception as e:
            self.log.error("some thing wrong with save file: %s.", str(e))
            self.set_message(str(e))

    def get_result(self):
        i = 0
        while True:
            try:
                if self.ws is None:
                    break
                result = self.ws.recv()
                res_json = json.loads(result)
                self.origin_result_list.append(res_json)
                if self.sid == "":
                    sid = jsonpath.jsonpath(res_json, expr="$.header.sid")
                    if sid is not None:
                        self.sid = sid[0]
                code = jsonpath.jsonpath(res_json, expr="$.header.code")

                if code is not None and code[0] != 0:
                    self.error_code = code[0]
                    msg = jsonpath.jsonpath(res_json, expr="$.header.message")
                    self.set_message(msg[0])
                    break
                else:
                    status = jsonpath.jsonpath(res_json, expr="$.header.status")
                    if status is not None and status[0] == 2:
                        result_arrive_time = time.time()
                        self.write_data_time = self.write_4_time - self.write_1_time
                        self.consume_4_time = result_arrive_time - self.write_4_time
                        self.consume_1_time = result_arrive_time - self.write_1_time
                        break
            except Exception as e:
                self.log.error("get result error: %s", str(e))
                self.set_message(str(e))
                break
        if not self.stream_mode:
            self.close_ws()

        if self.error_code == 0 and self.save_to_file is True:
            self.handle_result()

        return_res = {
            "service_address": self.r_url,
            "params": self.req_param,
            "origin_result_list": self.origin_result_list,
            "sid": self.sid,
            "during_time": self.consume_4_time,
            "error_code": self.error_code,
            "message": self.msg,
            "file_md5": self.file_md5,
            "save_path": self.save_path,
        }
        return return_res

    def set_message(self, msg):
        # 保留第一次错误日志
        if self.msg == "success":
            self.msg = "{0!s}".format(msg)

    def close_ws(self):
        if self.error_code != 0:
            return
        self.ws.close()


class HttpClient:
    def __init__(self, url, r_data, **options):
        if options.get('log'):
            self.log = options['log']
        else:
            self.log = logging
        eng_ip = r_data.get("eng_ip", "")
        if isinstance(eng_ip, str) and len(eng_ip) > 0:
            r_data['header']['directEngIp'] = eng_ip
        self.req_param = copy.deepcopy(r_data)
        self.req_data = {
            "header": r_data['header'],
            "parameter": r_data['parameter'],
            "payload": r_data['payload'],
        }
        self.opt = options
        self.r_url = url
        stream_mode = options.pop("stream_mode", False)
        self.stream_mode = stream_mode
        self.key = options.pop("key", "54a131e661fef1b1227fa9d7f06e618d")
        if self.key is None:
            self.key = "54a131e661fef1b1227fa9d7f06e618d"
        self.secret = options.pop("secret", "jE0ETbQ0BgOA8IDsXRdtWSYXbUGsl4T7")
        if self.secret is None:
            self.secret = "jE0ETbQ0BgOA8IDsXRdtWSYXbUGsl4T7"
        self.r_url_dict = urlparse(url)
        self.r_date = ne_utils.get_formate_date()
        self.sid = ""
        self.origin_result_list = []
        self.error_code = 0
        self.msg = "success"
        self.write_1_time = 0
        self.consume_1_time = 0
        self.write_4_time = 0
        self.consume_4_time = 0
        self.res = None
        self.save_path = {}
        self.file_md5 = {}
        self.save_to_file = options.get("save_to_file", True)

    def get_headers(self, **op):
        http = op.pop("http", False)
        body_digest = op.pop("body_digest", None)
        # hmac 加密需要digest字段，但是不必要校验body体
        body_digest = op.pop("body_digest", body_digest)
        auth_digest = ne_utils.get_kong_auth(self.r_url, self.r_date, method="POST", key=self.key, secret=self.secret,
                                             http=http, body_digest=body_digest)
        headers = {
            # "Accept": "application/json;version=1.0",
            "authorization": auth_digest,
            "date": self.r_date,
            "host": self.r_url_dict.netloc,
        }
        return headers

    def callback(self, future):
        pass

    def set_message(self, msg):
        # 保留第一次错误日志
        if self.msg == "success":
            self.msg = "{0!s}".format(msg)

    def prepare_req_data(self):
        media_type_list = ["text", "audio", "image", "video"]
        media_path2name = {}
        # {'payload.txt.text': '/sb3f8a020/1584670207/language.txt'}
        for media_type in media_type_list:
            media_expr = parse("$..payload.*.{}".format(media_type))
            media_match = media_expr.find(self.req_param)
            if len(media_match) > 0:
                for media in media_match:
                    media_path2name[str(media.full_path)] = media.value
        for media_path, media_name in media_path2name.items():
            self.prepare_oneshot_data(media_name, media_path)

    def prepare_oneshot_data(self, f_name, payload_path):
        # fixme 文本类型外，编码方式或许会改变
        payload_path_list = payload_path.split(".")
        try:
            f_data = ne_utils.get_file_bytes(f_name)
            self.req_data['header']['status'] = 3
            if payload_path_list[2] in ["audio", "image", "video"]:
                self.req_data['payload'][payload_path_list[1]][payload_path_list[2]] = base64.b64encode(f_data).decode()
                self.req_data['payload'][payload_path_list[1]]['status'] = 3
            elif payload_path_list[2] == "text":
                self.req_data['payload'][payload_path_list[1]][payload_path_list[2]] = base64.b64encode(f_data).decode()
                self.req_data['payload'][payload_path_list[1]]['status'] = 3
        except Exception as e:
            self.set_message(str(e))
            self.error_code = exception.WebCode.RemoteReqError

    def do_request(self, method="POST", **kw):
        self.prepare_req_data()
        try:
            # aipaas 不做body校验
            body_digest = "SHA-256=" + ne_utils.get_check_body(self.req_data)
            headers = self.get_headers()
            req_url = self.r_url + "?" + urlencode(headers)
            headers['Digest'] = body_digest
            header_other = kw.get("header", {})
            if header_other:
                headers.update(header_other)
            self.write_1_time = time.time()
            # self.log.info("the request headers is %s.", header)
            # 默认传递为json格式
            self.log.debug(self.req_data)
            if method == "POST":
                self.res = requests.post(req_url, json=self.req_data, headers=headers, verify=False)
            else:
                self.res = requests.get(req_url, headers=headers, verify=False)
            self.write_4_time = time.time()
            return self.res
        except Exception as e:
            debug_info = "aipaas do_request fail: {}".format(str(e))
            self.log.error(debug_info)
            self.set_message(debug_info)
            self.error_code = exception.WebCode.RemoteReqError

    def handle_result(self):
        if not jsonpath.jsonpath(self.origin_result_list, '$..payload'):
            self.log.info("There have no payload info in the origin result list.")
            return

        media_type_list = ["text", "audio", "image", "video"]
        media_name2data = {}
        # {'value_name1': {'data': [XX, XX...], 'media_type': XX, 'encoding': XX}}, 'value_name2': {......}}
        try:
            for media_type in media_type_list:
                media_expr = parse("$..payload.*.{}".format(media_type))
                media_match = media_expr.find(self.origin_result_list)
                if len(media_match) > 0:
                    for media in media_match:
                        path = str(media.full_path)
                        data = media.value
                        value_name = path.split(".")[-2]
                        if media_name2data.get(value_name, None):
                            media_name2data[value_name]['data'].append(data)
                        else:
                            media_name2data[value_name] = {}
                            media_name2data[value_name]['data'] = [data]
                            media_name2data[value_name]['media_type'] = media_type
                            encoding = jsonpath.jsonpath(self.origin_result_list,
                                                         '$..payload.{}.encoding'.format(value_name))
                            media_name2data[value_name]['encoding'] = encoding[0]
            self.log.debug(media_name2data)
        except Exception as e:
            self.log.error("get payload data from result fail: %s", str(e))
            self.set_message(str(e))

        try:
            for value_name, data_info in media_name2data.items():
                md5_hash = hashlib.md5()
                feh_res = bytes()
                encoding = data_info['encoding']
                media_type = data_info['media_type']
                for data in data_info['data']:
                    date_byte = base64.b64decode(data)
                    md5_hash.update(date_byte)
                    feh_res = feh_res + date_byte
                file_md5 = md5_hash.hexdigest()

                media_path = "../resource/aipaas/{}".format(media_type)
                if not os.path.isdir(media_path):
                    os.makedirs(media_path)
                save_path = "{}/{}.{}".format(media_path, file_md5, encoding)
                fp = open(save_path, 'wb')
                fp.write(feh_res)
                fp.close()
                self.file_md5[value_name] = file_md5
                self.save_path[value_name] = save_path
                self.log.info("The payload data is saved in this path: {}".format(save_path))
        except Exception as e:
            self.log.error("some thing wrong with save file: %s.", str(e))
            self.set_message(str(e))

    def get_result(self):
        try:
            if self.res.status_code != 200:
                self.set_message(self.res.text)
                self.error_code = self.res.status_code
                self.origin_result_list.append(self.res.json())
            else:
                res_json = self.res.json()
                sid = jsonpath.jsonpath(res_json, expr="$.header.sid")
                if sid:
                    self.sid = sid[0]
                msg = jsonpath.jsonpath(res_json, expr="$.header.message")
                if msg:
                    self.set_message(msg[0])
                error_code = jsonpath.jsonpath(res_json, expr="$.header.code")
                if error_code:
                    self.error_code = error_code[0]
                self.origin_result_list.append(res_json)
                self.consume_4_time = self.write_4_time - self.write_1_time
        except Exception as e:
            debug_info = "aipaas_client h_client get_result tail: {}".format(str(e))
            self.log.error(debug_info)

        if self.error_code == 0 and self.save_to_file is True:
            self.handle_result()

        return_res = {
            "service_address": self.r_url,
            "params": self.req_param,
            "origin_result_list": self.origin_result_list,
            "sid": self.sid,
            "during_time": self.consume_4_time,
            "error_code": self.error_code,
            "message": self.msg,
            "file_md5": self.file_md5,
            "save_path": self.save_path,
        }
        return return_res
