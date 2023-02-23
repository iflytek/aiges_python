#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: types
@time: 2023/01/11
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
from enum import Enum
from pydantic import BaseModel, Field, create_model
from typing import Optional


from pydantic import BaseModel as PydanticBaseModel


# class BaseModel(PydanticBaseModel):
#     class Config:
#         arbitrary_types_allowed = True

# class BaseModel(BaseModel):
#     class Config:
#         arbitrary_types_allowed = True


class TextEncoding(str, Enum):
    utf8 = "utf8"
    gb2312 = "gb2312"
    gbk = "gbk"


class ImageEncoding(str, Enum):
    jpg = "jpg"
    png = "png"


class AudioEncoding(str, Enum):
    h264 = "h.264"


class Compress(str, Enum):
    raw = "raw"
    gzip = "gzip"


class TextFormat(str, Enum):
    xml = "xml"
    plain = "plain"
    json = "json"


class DataStatus(int, Enum):
    First = 0
    Continue = 1
    Last = 2
    Once = 3

class StrParamField(BaseModel):
    maxLength: Optional[int]
    minLength: Optional[int]
    title :Optional[str]


class TextField(BaseModel):
    encoding: TextEncoding = Field(..., alias="encoding")
    compress: Compress = Field(..., alias="compress")
    format: TextFormat = Field(..., alias="format")
    status: DataStatus = Field(..., alias="status")
    text: str = Field(None, min_length=1, max_length=10485760)
    data_type: Optional[str] = Field("text")


class ImageField(BaseModel):
    encoding: ImageEncoding = Field(None, alias="encoding")
    status: DataStatus = Field(None, alias="status")
    image: str = Field(None, min_length=1, max_length=10485760)
    data_type: Optional[str] = Field("image")


class AudioField(BaseModel):
    encoding: AudioEncoding = Field(None, alias="encoding")
    status: DataStatus = Field(None, alias="status")
    audio: str = Field(None, min_length=1, max_length=10485760)
    data_type: Optional[str] = Field("audio")


class BoolParam(BaseModel):
    pass


class StringParam(BaseModel):
    pass
