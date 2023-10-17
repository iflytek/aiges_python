#! /usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2023/04/29 09:04:12
# @Author  : daocoder
# @Email   : daocoder@foxmail.com

import json
import utils.ne_utils as ne_utils


# todo: change to your request data
app_key = "your app_key"
app_secret = "your app_secret"
s_addr = "input your service address"

req_data = {
    "header": {
        "app_id": app_key
    },
    "parameter": {
        "s2a1fc20c": {
            "result": {
                "encoding": "utf8",
                "compress": "raw",
                "format": "plain"
            }
        }
    },
    "payload": {
        "data1": {
            "encoding": "png",
            # todo: change to your image path
            "image": "../resource/mfv/test.png",
            "status": 3
        }
    }
}


def test_aipaas():
    print(f"service address is {s_addr}")
    r_d = req_data["service_address"] = s_addr
    if s_addr.startswith("ws"):
        res = ne_utils.do_aipaas_ws_request(r_d)
    else:
        res = ne_utils.do_aipaas_http_request(r_d)
    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_aipaas()
