#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: types.py
@time: 2022/09/15
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


STRING = 0
AUDIO = 1
IMAGE = 2
VIDEO = 3

DataText = 0  # 文本数据
DataAudio = 1  # 音频数据
DataImage = 2  # 图像数据
DataVideo = 3  # 视频数据

DataBegin = 0 # 首数据
DataContinue = 1 # 中间数据
DataEnd = 2 # 尾数据
DataOnce = 3 # 非会话单次输入输出

Once = DataOnce

# 并行模式
THREAD_MODE = "thread" # 默认模式，

PROCESS_MODE = "process" # 当前不可用
