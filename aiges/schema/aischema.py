#!/usr/bin/env python
# coding:utf-8
"""
@author: nivic ybyang7
@license: Apache Licence
@file: aischema.py
@time: 2022/11/17
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
import copy
import json
from json import JSONEncoder
from collections.abc import Callable, Mapping
from flask_restx import Api, Resource, Namespace, Model, OrderedModel, fields, swagger
from flask import Flask
import jsonref
from enum import Enum
from pydantic import BaseModel, Field, create_model
from typing import Optional, Dict
from pydantic.fields import ModelField
import pprint
from aiges.schema.utils.schemaUtils import resolve_schema
from aiges.schema.types import *

class AIModel(BaseModel):
    class Config:
        allow_mutation = True
        extra = 'allow'

    def __init__(self, *args, **kwargs):
        super(AIModel, self).__init__(*args, **kwargs)

    @classmethod
    def add_key_datatype(cls, f_key, f_type):
        new_fields: Dict[str, ModelField] = {}
        new_annotations: Dict[str, Optional[type]] = {}
        f_annotation = None
        if f_annotation:
            new_annotations[f_key] = f_annotation

        f_value = {"dataType": f_type}
        new_fields[f_key] = ModelField.infer(name=f_key, value=f_value, annotation=f_annotation, class_validators=None,
                                             config=cls.__config__)

        cls.__fields__.update(new_fields)
        # cls.__annotations__.update(new_annotations)

    def add_key_media_type(cls, f_key, m: BaseModel):
        new_fields: Dict[str, ModelField] = {}
        new_annotations: Dict[str, Optional[type]] = {}
        f_annotation = None
        if f_annotation:
            new_annotations[f_key] = f_annotation
        # cls.__setattr__(name=f_key, value=m)
        new_fields[f_key] = ModelField.infer(name=f_key, value=m, annotation=f_annotation, class_validators=None,
                                             config=cls.__config__)

        cls.__fields__.update(new_fields)


class Input(AIModel):
    pass


class Accept(AIModel):
    pass


class Meta(BaseModel):
    '''
    {
        "serviceId": "s6d69bb68",
        "version": "v1.0",
        "service": [
            "s6d69bb68"
        ],
        "sub": "ase",
        "call": "atmos-low-concurrency",
        "call_type": "0",
        "webgate_type": 0,
        "hosts": "api.xf-yun.com",
        "route": "/v1/private/s6d69bb68",
        "s6d69bb68": {
            "input": {
                "input_text": {
                    "dataType": "text"
                }
            },
            "accept": {
                "output_imgs": {
                    "dataType": "image"
                }
            }
        },

    }'''

    serviceId: str = Field()
    version: str = Field()
    sub: str = Field()
    call: str = Field()
    call_type: str = Field()
    webgate_type: int = Field()
    hosts: str = Field()
    route: str = Field()


class Header(BaseModel):
    appid: str
    uid: Optional[str]
    device_id: Optional[str]
    imei: Optional[str]
    imsi: Optional[str]
    mac: Optional[str]
    net_type: Optional[str]
    net_isp: Optional[str]
    status: int
    res_id: Optional[str]


class SvcParameter(BaseModel):
    key1: str
    key2: str


class Parameter(AIModel):
    pass



class Payload(AIModel):
    pass


class SchemaInput(BaseModel):
    header: Header = Field(None, alias="header")
    parameter: Parameter = Field(None, alias="parameter")
    payload: Payload = Field(None, alias="payload")

    @classmethod
    def addPayloadData(cls, key_name: str, m: BaseModel):
        new_fields: Dict[str, ModelField] = {}
        new_annotations: Dict[str, Optional[type]] = {}
        f_annotation = None
        if f_annotation:
            new_annotations[key_name] = f_annotation
        f_value = {"dataType": 11}
        new_fields[key_name] = ModelField.infer(name=key_name, value=f_value, annotation=f_annotation,
                                                class_validators=None,
                                                config=cls.__config__)

        cls.__fields__.update(new_fields)


class SchemaOutput(BaseModel):
    def __int__(self):
        pass


class AIschema():
    def __init__(self, meta, schemainput, schemaoutput, is_aipaas=False, keep_default=True):
        self.meta = meta
        self.schemaoutput = schemaoutput
        self.schemainput = schemainput
        # 是否是aipaas协议， 兼容内部协议，控制兼容内部aipaas协议
        self.is_aipaas = is_aipaas
        # keep default 保留default
        self.keep_default = keep_default

    def json(self):
        meta = self.meta.dict()
        si = self.process_schema(self.schemainput.schema_json(), self.is_aipaas, self.keep_default)
        so = self.process_schema(self.schemaoutput.schema_json(), self.is_aipaas, self.keep_default)
        return dict(meta=meta, schemainput=si, schemaoutput=so)

    def aipaas(self):
        '''用于替换aipaas实现的 schema， 如default相关字段， 兼容协议'''
        pass

    def process_schema(self, schemajson, is_aipaas, keep_default):
        schema = jsonref.loads(schemajson)
        b = resolve_schema(schema, is_aipaas, keep_default)
        if "definitions" in b:
            del b['definitions']
        # if 'payload' in b['properties']:
        #     if 'allOf' in b['properties']['payload']:
        #         allof = copy.copy(b['properties']['payload']['allOf'][0])
        #         del b['properties']['payload']['allOf']
        #         b['properties']['payload']['properties'] = allof
        #
        #
        #     if 'default' in b['properties']['payload']:
        #         del b['properties']['payload']['default']

        return b


if __name__ == '__main__':
    MAX_TRIES = 100
    # schema = SchemaInput.schema()
    # for i in range(MAX_TRIES):
    #     if '$ref' not in json.dumps(schema):
    #         break
    #     schema = replace_value_in_dict(schema.copy(), schema.copy())
    #
    # del schema['definitions']
    s = SchemaInput.schema_json()
    dd = SchemaInput(header=Header(status=1, appid="c'c"))
    ss = json.loads(s)
    schema = jsonref.loads(s)

    # print(json.dumps(schema, indent=4))
    d = {"sid": "ccc"}
    MetaModel = create_model(
        'MetaModel',
        __base__=Meta,
        **d,
    )
    new_fields: Dict[str, ModelField] = {}

    fname = "scccid"

    Input.add_key_datatype("input_text", "text")
    Input.add_key_datatype("input_text2", "image")
    parameter = Input()

    Accept.add_key_datatype("result", "image")
    accept = Accept()
    v = {"accept": accept, "input": parameter}

    new_fields[fname] = ModelField.infer(name=fname, value=v, annotation=None, class_validators=None,
                                         config=MetaModel.__config__)
    MetaModel.__fields__.update(new_fields)

    a = MetaModel(serviceId="cc", sub="ccd", call="0", call_type="aipaas", webgate_type="c", hosts="ccdd", route="v1",
                  version="v4")
    # parameter.add_key_data_type("k1", "text")
    # pprint.pprint(a.json(), indent=4)
    p = Payload()
    pd = {"p111": TextField(encoding="utf8", format="plain", compress="raw", status=3, text="123"),
          "p22": TextField(encoding="utf8", format="plain", compress="raw", status=3, text="123")}

    PayloadModel = create_model(
        'PayloadModel',
        __base__=Payload,
        **pd
    )
    pdd = {"payload": PayloadModel(), "header": Header(appid="11", status="3"), "parameter": Parameter()}
    SchemaInputModel = create_model(
        'SchemaInputModel',
        **pdd,
        __base__=BaseModel
    )
    sin = SchemaInputModel()

    sc = AIschema(meta=a, schemainput=SchemaInputModel, schemaoutput=SchemaOutput())
    #print(json.dumps(sc.json(), indent=4))

    t = TextField(text=b" ").schema_json()
    #print(t)
