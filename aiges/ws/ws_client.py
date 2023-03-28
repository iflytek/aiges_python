#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: ws_client
@time: 2023/03/04
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

import json
import base64
import hashlib
import time

import websocket


def readb64(index, encoded_data):
    # img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # return img
    b = base64.b64decode(encoded_data)
    print(hashlib.md5(b).hexdigest())
    print(len(b))
    # a = open(str(index) + ".jpg", "wb")
    # a.write(b)
    # a.close()
    return b.decode("utf-8")


def on_error(wsapp, err):
    print("EXAMPLE error encountered: ", err)


# 收到websocket消息的处理
def on_message(ws, message):
    if message == "":
        return
    temp_result = json.loads(message)
    print(temp_result)
    # print("响应数据:{}\n".format(temp_result))
    header = temp_result.get('header')
    if header is None:
        return 2, "失败"
    code = header.get('code')
    if header is None or code != 0:
        print("获取结果失败，请根据code查证问题原因:, %s" % code)
        return 2, "失败"
    text = ''
    if "payload" in temp_result:
        i = temp_result['payload']['response']['text']
        index = temp_result['payload']['response']['seq']
        text = readb64(index, i)
        print(text)

    # print("sid:{}".format(header.get('sid')))
    status = header.get('status')
    if status == 1:
        print("dddcccc")
        ws.send(construct_req(1))

    # print('status:{}\n'.format(status))
    return int(status), text


count = 0
max_count = 30


def construct_req(status=1):
    request_data_str = open("sample.json", 'rb').read()
    r = json.loads(request_data_str)
    r['header']['status'] = status
    global count, max_count
    count += 1
    print(count)
    if count >= 180:
        r['header']['status'] = 2
        r['payload']['message']['status'] = 2
    return json.dumps(r)


def on_open(ws):
    ws.send(construct_req(1))


def on_close(ws, code, reason):
    print("code", code, reason)


def request(request_url, APIKey=None, APISecret=None):
    # request_data_str = json.load(a)
    # auth_request_url = build_auth_request_url(request_url, "GET", APIKey, APISecret)
    ws = websocket.WebSocketApp(request_url, on_open=on_open, on_message=on_message, on_error=on_error,
                                on_close=on_close)
    # ws.connect(request_url)
    ws.run_forever(ping_interval=2)
    status = None
    # while status != 2 :
    #    status = on_message(ws, ws.recv())


if __name__ == '__main__':
    url = "ws://localhost:1888/backup.0/private/chatgpt"
    request(url)
