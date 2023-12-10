#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: audit_service.py
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

from aiges.utils import log
from aiges.utils.audit import build_audit_url, ConfigException
import os
import requests
import json

audit_url = os.getenv("AUDIT_URL")
secret = os.getenv("AUDIT_SECRET")
accessKeyId = os.getenv("AUDIT_KEY")
appid = os.getenv("AUDIT_APPID")


def audit_content(content: str = "台湾法尔+台湾的那些政治家说要打倒国家的右翼势力 ,测试 he1 爸爸台湾是一个国家打倒所有的政治家", biz_type="aity_output") -> (bool,str):
    try:
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
            log.log.error(response)
            return False, response["desc"]
        result = response["data"]["result"]
        suggest = result['suggest']
        log.log.info("request_id: {request_id}, sid: {sid}".format(request_id=response["data"]["request_id"],
                                                                   sid=response['sid']))
        if suggest != "pass":
            msg = "内容审核: 内容不合规!"
            log.log.error(msg)
            return False, msg
        else:
            return True, result["detail"]['content']
    except ConfigException as e:
        log.log.error(result)
        return False, str(e)
    except Exception as e:
        log.log.error(str(e))
        return False, "内容审核错误"


def main():
    c = audit_content("B")
    print(c)
    pass


if __name__ == '__main__':
    main()
