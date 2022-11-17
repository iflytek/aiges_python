import base64
import copy
import json

import requests
import jsonpath_rw

from aiges.client.utils import ne_utils
from aiges.utils.log import log
# from data import response_path_list
from urllib import parse

media_type_list = ["text", "audio", "image", "video"]


# 准备请求数据
def prepare_req_data(request_data):
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
        f_data = ne_utils.get_file_bytes(media_name)
        new_request_data['header']['status'] = 3
        new_request_data['payload'][payload_path_list[1]][payload_path_list[2]] = base64.b64encode(f_data).decode()
        new_request_data['payload'][payload_path_list[1]]['status'] = 3
    return new_request_data


# 执行http请求
def execute(request_url, request_data, method, app_id, api_key, api_secret, callback=lambda x: x):
    # 清除文件
    ne_utils.del_file('./resource/output')

    # 获取请求url
    auth_request_url = ne_utils.build_auth_request_url(request_url, method, api_key, api_secret)

    url_result = parse.urlparse(request_url)
    headers = {'content-type': "application/json", 'host': url_result.hostname, 'app_id': app_id}
    # 准备待发送的数据
    new_request_data = prepare_req_data(request_data)
    log.debug("请求数据:{}\n".format(new_request_data))
    response = requests.post(auth_request_url, data=json.dumps(new_request_data), headers=headers)
    callback(response)
