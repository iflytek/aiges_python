#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: log.py
@time: 2022/07/27
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
import logging
import os
import sys

fmt = '%(asctime)s - %(name)s:%(funcName)s:%(lineno)s - %(levelname)s:  %(message)s'
level = logging.DEBUG
ch = logging.StreamHandler()
formatter = logging.Formatter(fmt)
ch.setFormatter(formatter)
ch.setLevel(logging.INFO)
log = logging.getLogger()
log.setLevel(level)
log.addHandler(ch)

logpath = "/log/app"


def getLogger(fmt=fmt, level=level, name="root"):
    global log
    ch = logging.StreamHandler()
    formatter = logging.Formatter(fmt)
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    log.setLevel(level)
    for handler in log.handlers:
        log.removeHandler(handler)
    log.addHandler(ch)
    return log


def getFileLogger(fmt=fmt, level=level, name="wrapper"):
    global logpath
    pt = sys.platform
    print('system platform: ', pt)
    if pt.lower() == "darwin":
        logpath = "/tmp/log/app"
    else:
        logpath = "./log/"


    log = logging.getLogger(name)
    if not os.path.isdir(logpath) or not os.path.exists(logpath):
        os.makedirs(logpath)

    lfname = os.path.join(logpath, name + ".log")
    ch = logging.FileHandler(lfname)
    formatter = logging.Formatter(fmt)
    ch.setFormatter(formatter)
    ch.setLevel(level)
    for handler in log.handlers:
        log.removeHandler(handler)
    log.addHandler(ch)
    return log
