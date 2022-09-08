#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: flask_utils
@time: 2022/08/06
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
import os


def getenv_as_bool(*env_vars, default=False):
    """
    Read environment variable, parsing it to a boolean.
    """

    val = getenv(*env_vars)

    if val is None:
        return default

    return val.lower() in ["1", "true", "t"]

def getenv(*env_vars, default=None):
    """
    Overload of os.getenv() to allow falling back through multiple environment
    variables. The environment variables will be checked sequentially until one
    of them is found.

    Parameters
    ------
    *env_vars
        Variadic list of environment variable names to check.
    default
        Default value to return if none of the environment variables exist.

    Returns
    ------
        Value of the first environment variable set or default.
    """
    for env_var in env_vars:
        if env_var in os.environ:
            return os.environ.get(env_var)

    return default


class AigesMicroserviceException(Exception):
    status_code = 400

    def __init__(
        self, message, status_code=None, payload=None, reason="MICROSERVICE_BAD_DATA"
    ):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        self.reason = reason

    def to_dict(self):
        rv = {
            "status": {
                "status": 1,
                "info": self.message,
                "code": -1,
                "reason": self.reason,
            }
        }
        return rv
