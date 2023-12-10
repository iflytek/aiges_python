#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: audit
@time: 2023/10/30
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
import base64
import hmac
import hashlib
import datetime
import json
from urllib import parse
import uuid
import requests
import pytz


class ConfigException(Exception):
    pass


def build_audit_url(audit_url, secret, accessKeyId, appid):
    if not audit_url or not secret or not accessKeyId or not appid:
        raise ConfigException("请配置内容审核鉴权")

    fmt = "%Y-%m-%dT%H:%M:%S%z"
    uid = uuid.uuid4()

    timestamp = datetime.datetime.now(tz=pytz.utc).timestamp()

    aware_datetime = datetime.datetime.fromtimestamp(timestamp, pytz.utc)

    ts = aware_datetime.strftime(fmt)
    params = {
        "appId": appid,
        "accessKeyId": accessKeyId,
        "utc": ts,
        "uuid": str(uid),
    }
    params = dict(sorted(params.items()))
    string = parse.urlencode(params)
    signature_sha = hmac.new(secret.encode('utf-8'), string.encode('utf-8'), digestmod=hashlib.sha1).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    sg_base = parse.urlencode({
        "signature": signature_sha
        }
    )
    s = string + "&" +sg_base
    request_url = audit_url + "?" + s
    return request_url


def test_audit_content(content: str = "台湾法尔+台湾的那些政治家说要打倒国家的右翼势力 ,测试 he1 爸爸台湾是一个国家打倒所有的政治家", biz_type="aity_output") -> (
        bool, str):
    import os
    try:

        audit_url = os.getenv("AUDIT_URL")
        secret = os.getenv("AUDIT_SECRET")
        accessKeyId = os.getenv("AUDIT_KEY")
        appid = os.getenv("AUDIT_APPID")
        u = build_audit_url(audit_url, secret, accessKeyId, appid)
        body = {
            "is_match_all": 0,
            "biz_type": biz_type,
            "content": content
        }
        res = requests.post(u, data=json.dumps(body), headers={"Content-Type": "application/json"})
        if res.status_code != 200:
            return False, "内容审核失败, http code: %s" % (str(res.status_code))

        response = json.loads(res.content)
        if response["code"] != "000000":
            print(response)
            return False, response["desc"]
        result = response["data"]["result"]
        suggest = result['suggest']
        print("request_id: {request_id}, sid: {sid}".format(request_id=response["data"]["request_id"],
                                                            sid=response['sid']))
        if suggest != "pass":
            msg = "内容审核: 内容不合规!"
            print(msg)
            return False, msg
        else:
            return True, result['detail']['content']
    except ConfigException as e:
        print(str(e))
        return False, str(e)
    except Exception as e:
        print(str(e))
        return False, "内容审核错误"


def main():
    c = test_audit_content("B")
    print(c)
    pass


if __name__ == '__main__':
    main()
