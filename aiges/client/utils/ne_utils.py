#! /usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/04/29 08:54:04
# @Author  : daocoder
# @Email   : daocoder@foxmail.com


import json
import math
import os
import hashlib
import hmac
import base64
import time
import zipfile
import aipass_client
import chardet
import struct
from io import BytesIO
from urllib.parse import urlparse


def get_file_path(dir_path, file_name):
    """
    根据文件路径和文件名进行相对路径的拼接
    :param dir_path: 文件路径
    :param file_name: 文件名
    :return: 相对文件路径
    """
    file_path = os.path.join(dir_path, file_name)
    return file_path


def get_file_bytes(fd):
    """
    根据文件路径（一般相对）获取二进制数据
    :param fd: 文件路径
    :return: 二进制数据，不存在时为 None供后续判断
    """
    if fd is None:
        return b""
    if isinstance(fd, bytes):
        f_data = fd
        return f_data
    if os.path.exists(fd):
        with open(fd, "rb") as f:
            wav_maker = f.read(4)
            if b'RIFF' == wav_maker:
                f.seek(44, 0)
            else:
                f.seek(0, 0)
            f_data = f.read()
        f.close()
    else:
        f_data = fd.encode()
    return f_data


def get_wav_header(fd, nchannel=1, sampwidth=2, framerate=16000):
    """
    wave package. 自定义插入wav头44字节。
    :param fd:
    :param nchannel: 声道数
    :param sampwidth: 量化位数
    :param framerate: 采样率
    :return: 44 bytes header
    """
    fd_len = len(fd)
    hb = bytes()
    hb = hb + b'RIFF'
    framerate = int(round(framerate))
    nframes = fd_len // (nchannel * sampwidth)
    datalength = nframes * nchannel * sampwidth
    hb = hb + struct.pack('<L4s4sLHHLLHH4s', 36 + datalength, b'WAVE', b'fmt ', 16,
                          0x0001, nchannel, framerate, nchannel * framerate * sampwidth,
                          nchannel * sampwidth, sampwidth * 8, b'data')
    hb = hb + struct.pack('<L', datalength)
    return hb


def build_stream_data(audio_data, read_len=1280, ws=False):
    """
     构造流式数据，[content, data_status, wav_length]
     fixme yield 文件读取较少内存占用，和发送数据耦合，考虑实现
    :param audio_data: 多媒体二进制数据 每次读取长度 2333 一次读取完毕，::>_<::
    :param read_len: 每次读取长度
    :param ws: 流式方式上传数据
    :return: [[content, data_status, wav_length]]
    """
    stream_list = []
    # 防止死循环
    if len(audio_data) == 0:
        if ws:
            data_status = 2
        else:
            data_status = 4
        stream_list.append([bytes(), data_status, 0])
        return stream_list

    wav_length = len(audio_data)
    input_length = 0
    if read_len == 2333:
        content = audio_data[input_length:]
        if ws:
            data_status = 2
        else:
            data_status = 4
        stream_list.append([content, data_status, wav_length - input_length])
    else:
        # 修复read_len > wav_length时 2333失效
        if read_len > wav_length:
            read_len = wav_length
        num = 1
        while input_length + read_len <= wav_length:
            if num == 1:
                if ws:
                    data_status = 0
                else:
                    data_status = 1
            else:
                if ws:
                    data_status = 1
                else:
                    data_status = 2
            if input_length + read_len == wav_length:
                if ws:
                    data_status = 2
                else:
                    data_status = 4
            content = audio_data[input_length: input_length + read_len]
            stream_list.append([content, data_status, read_len])
            num = num + 1
            input_length = input_length + read_len
        if wav_length > input_length:
            content = audio_data[input_length:]
            if ws:
                data_status = 2
            else:
                data_status = 4
            stream_list.append([content, data_status, wav_length - input_length])
    return stream_list


def build_stream_data_text(text_data, ws=False):
    """
     文本按行读取，构造流式数据，[content, data_status, wav_length]
    :param text_data: 二进制数据
    :param ws: 流式方式上传数据
    :return: [[content, data_status, wav_length]]
    """
    glb_log_obj = helper.init_log()
    stream_list = []

    if len(text_data) == 0:
        if ws:
            data_status = 2
        else:
            data_status = 4
        stream_list.append([bytes(), data_status, 0])
        return stream_list

    try:
        charset = chardet.detect(text_data)
        data_str_list_tmp = text_data.decode(charset['encoding']).splitlines()
        data_str_list = [x for x in data_str_list_tmp if x.strip()]
    except Exception as e:
        glb_log_obj.error("build_stream_data_text decode fail: {}".format(str(e)))
        raise Exception(e)

    for index, line in enumerate(data_str_list):
        if index == len(data_str_list) - 1:
            if ws:
                data_status = 2
            else:
                data_status = 4
        elif index == 0:
            if ws:
                data_status = 0
            else:
                data_status = 1
        else:
            if ws:
                data_status = 1
            else:
                data_status = 2
        content = line.encode(charset['encoding'])
        stream_list.append([content, data_status, len(content)])
    return stream_list


def build_stream_data_image(img_zip_data, ws=False):
    """
     直接解压，不保存成文件，图片集按张读取，构造流式数据，[content, data_status, wav_length]
    :param img_zip_data: 二进制数据
    :param ws: 流式方式上传数据
    :return: [[content, data_status, wav_length]]
    """
    stream_list = []

    if len(img_zip_data) == 0:
        if ws:
            data_status = 2
        else:
            data_status = 4
        stream_list.append([bytes(), data_status, 0])
        return stream_list

    try:
        fio = BytesIO(img_zip_data)
        img_zip = zipfile.ZipFile(file=fio)
        img_name_list = img_zip.namelist()
        # 过滤img_name_list中的文件夹
        img_name_list_no_dir = [i for i in img_name_list if not i.endswith('/')]
        img_num = len(img_name_list_no_dir)
        # sorted(img_name_list_no_dir)
        img_name_list_no_dir.sort(key=lambda x: x.split("/")[-1])
        # print("origin img_name_list: {}, len: {}".format(img_name_list, len(img_zip.namelist())))
        # print("img_name_list_no_dir: {}, len: {}".format(img_name_list_no_dir, len(img_name_list_no_dir)))
    except Exception as e:
        # print(str(e))
        if ws:
            data_status = 2
        else:
            data_status = 4
        stream_list.append([bytes(), data_status, 0])
        return stream_list

    for index in range(img_num):
        if index == img_num - 1:
            if ws:
                data_status = 2
            else:
                data_status = 4
        elif index == 0:
            if ws:
                data_status = 0
            else:
                data_status = 1
        else:
            if ws:
                data_status = 1
            else:
                data_status = 2
        content = img_zip.read(img_name_list_no_dir[index])
        stream_list.append([content, data_status, len(content)])
    return stream_list


def get_file_md5(filename, wav_head=True):
    if not os.path.isfile(filename):
        return
    md5_hash = hashlib.md5()
    f = open(filename, 'rb')
    # wav 44字节头文件剥离
    if filename.endswith("wav") and wav_head:
        f.read(44)
    while True:
        b = f.read(8096)
        if not b:
            break
        md5_hash.update(b)
    f.close()
    return md5_hash.hexdigest()


def get_b_md5(b):
    """
    获取字符 md5 值
    :param b: 字符串或字节码
    :return:
    """
    md5_hash = hashlib.md5()
    if type(b) not in [str, bytes]:
        return ""
    if not isinstance(b, bytes):
        b = b.encode()
    md5_hash.update(b)
    return md5_hash.hexdigest()


def get_formate_date():
    t = time.time()
    time_tuple = time.gmtime(t)  # UTC时间
    return time.strftime("%a, %d %b %Y %H:%M:%S UTC", time_tuple)


def get_hmac_str(msg, key, digest=hashlib.sha256):
    """
    HMAC (Hash-based Message Authentication Code) 接口签名验证
    :param msg: 加密信息
    :param key: hash key
    :param digest: md5、sha1、sha256、sha512、adler32、crc32等。
    :return: digest msg
    """
    key_bytes = key.encode()
    msg_bytes = msg.encode()
    h = hmac.new(key_bytes, msg_bytes, digestmod=digest)
    digest = h.digest()
    # 如果消息很长，可以多次调用h.update(msg)
    return digest


def get_kong_auth(url, date, method="GET", **opt):
    """
    aiaas kong 校验，适用（http:wuup/iat 、ws）http-iat 需要验证body
    :param url: 请求域名地址
    :param date: 请求UTC格式时间
    :param method: 请求方法，ws用GET，http用POST
    :param opt: 一些参数选项 key secret http body_digest
    :return:
    """
    # http kong的原生http校验不用base64加密
    key = opt.pop("key", "")
    secret = opt.pop("secret", "")
    http = opt.pop("http", False)
    u = urlparse(url)
    body_digest = opt.pop("body_digest", None)
    if body_digest is None:
        h_sign_str = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(u.netloc, date, method, u.path)
    else:
        h_sign_str = "host: {}\ndate: {}\n{} {} HTTP/1.1\ndigest: {}".format(u.netloc, date, method, u.path,
                                                                             body_digest)
    digest = get_hmac_str(h_sign_str, secret)
    base64_digest = base64.b64encode(digest).decode()
    if http:
        api_key = "hmac username"
        # api_key = "api_key"
    else:
        api_key = "api_key"
    if body_digest is None:
        h_auth_str = "{}=\"{}\", algorithm=\"hmac-sha256\", headers=\"host date request-line\", " \
                     "signature=\"{}\"".format(api_key, key, base64_digest)
    else:
        h_auth_str = "{}=\"{}\", algorithm=\"hmac-sha256\", headers=\"host date request-line digest\", " \
                     "signature=\"{}\"".format(api_key, key, base64_digest)
    if http:
        return h_auth_str
    else:
        h_auth_base64_digest = base64.b64encode(h_auth_str.encode()).decode()
        return h_auth_base64_digest


def get_check_body(b_data):
    pdata_bin = json.dumps(b_data)
    sha256_pdata = hashlib.sha256(pdata_bin.encode()).digest()
    body_digest_str = base64.b64encode(sha256_pdata)
    body_digest = body_digest_str.decode()
    return body_digest


def do_aipaas_http_request(r_d, **kw):
    service_address = r_d['service_address']
    header = kw.pop('header', {})
    h_client = aipass_client.HttpClient(service_address, r_d, **kw)
    h_client.do_request(header=header)
    res = h_client.get_result()
    return res


def do_aipaas_ws_request(r_d, **kw):
    """
    :param r_d 请求数据
    :param kw 其它控制参数，考虑合并r_d
    """
    service_add = r_d['service_address']
    header = kw.pop("header", {})
    w_client = aipass_client.WsClient(service_add, r_d, **kw)
    media_path2data = w_client.prepare_req_data()
    ws_handle = w_client.connect(header=header)
    if ws_handle is None:
        return {"error_code": w_client.error_code,
                "error_info": "create ws connection failed, {}".format(w_client.msg),
                "service_address": r_d['service_address']}
    w_client.send_data(w_client.write_ws_stream, (media_path2data, ), kw)
    res = w_client.get_result()
    return res
