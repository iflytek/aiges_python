# coding: utf-8

## const default value
import sys

import time
import base64

#
try:
    from aiges_embed import ResponseData, Response, DataListNode, DataListCls, SessionCreateResponse, callback
except:
    from aiges.dto import Response, ResponseData, DataListNode, DataListCls, DataAudio, SessionCreateResponse, callback, \
        init_rq

from jinja2 import Template
import json
import os
from aiges.utils.log import log
from aiges.core.types import *
import threading
from pprint import pprint
from aiges.stream import *
import queue
from threading import Lock
from multiprocessing import Process
from aiges.schema.aischema import *

from pydantic import Field as PField
from pydantic.fields import FieldInfo
from pydantic import ConstrainedStr, ConstrainedInt, StrictStr, StrictInt, conint, constr

SUB = "ase"
CALL = "atmos"
CALL_TYPE = 0
HOSTS = [
    "api.xf-yun.com"
]
ROUTEKEY = []

type_map = {
    "text": STRING,
    "audio": AUDIO,
    "image": IMAGE,
    "video": VIDEO
}

tpl = '''
{
    "meta":{
        "serviceId":"{{serviceId}}",
        "version":"{{version}}",
        "route":"{{route}}",
        "sub":"{{sub}}",
        "call":"{{call}}",
        "call_type":{{call_type}},
        "hosts":"{{ hosts}}",
        "service": {{service}},
        "routeKey":[
		],
		"{{serviceId}}":{
            "input":{{inputs_fields}},
            "accept":{{accepts_fields}}
        }
    },
    "schemainput":{
        "type":"object",
        "properties":{
            "header":{
                "type":"object",
                "properties":{
                    "appid":{
                        "type":"string",
                        "maxLength":50
                    },
                    "uid":{
                        "type":"string",
                        "maxLength":50
                    },
                    "device_id":{
                        "type":"string",
                        "maxLength":50
                    },
                    "device.imei":{
                        "type":"string",
                        "maxLength":50
                    },
                    "device.imsi":{
                        "type":"string",
                        "maxLength":50
                    },
                    "device.mac":{
                        "type":"string",
                        "maxLength":50
                    },
                    "device.other":{
                        "type":"string",
                        "maxLength":50
                    },
                    "net.type":{
                        "type":"string",
                        "maxLength":50
                    },
                    "net.isp":{
                        "type":"string",
                        "maxLength":50
                    },
                    "app.ver":{
                        "type":"string",
                        "maxLength":50
                    }
                },
                "required":[
                    "appid"
                ]
            },
            "parameter":{
                "type":"object",
                "properties":{
                    "{{serviceId}}":{
                        "type":"object",
                        "properties":{{parameters}},
                        "required": {{required_paramters}}
                    }
                }
            },
            "payload":{
                "type":"object",
                "properties": {{inputs_payload}}
            }
        }
    },
    "schemaoutput":{
        "type":"object",
        "properties":{
            "payload":{
                "type":"object",
                "properties": {{accepts_payloads}}
            }
        }
    }
}
'''


class Field(object):
    def __init__(self, key, data_type):
        self.key = key
        self.data_type = data_type
        self.description = ""
        self.title = ''

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.key)

    def _check_path(self, path):
        if not os.path.exists(path):
            e = FileNotFoundError
            log.warn(e)
        return path

    def _encode(self, dataTye, encoding, binary):
        print("Not implement here , just give back")
        return binary

    @property
    def test_value(self):
        return NotImplementedError


class ParamField(Field):
    pass


class PayloadField(Field):
    pass


class JsonBodyField(PayloadField):
    def __init__(self, key, value="", need_base64=False):
        super(JsonBodyField, self).__init__(key, STRING)
        self.value = value
        self.data_type = STRING
        self.need_base64 = need_base64
        self.key = key

    @property
    def test_value(self):
        if not self.need_base64:
            return self.value
        else:
            return base64.b64encode(self.value)


class StringBodyField(PayloadField):
    def __init__(self, key, value=b" ", need_base64=False, encoding="utf8", format="plain", compress="raw", status=3):
        super(StringBodyField, self).__init__(key, STRING)
        if not isinstance(value, bytes):
            log.error("type String Body value: %s" % type(value))
            if isinstance(value, str):
                log.error("values is :%s" % value)
            raise Exception("StringBodyField value must be bytes String...")
        self.value = value
        self.data_type = STRING
        self.need_base64 = need_base64
        self.key = key
        self.encoding = encoding
        self.format = format
        self.compress = compress
        self.status = status
        self.text = b"value"

    @property
    def test_value(self):
        if not self.need_base64:
            return self.value
        else:
            return base64.b64encode(self.value)


class AudioBodyField(PayloadField):
    def __init__(self, key, path="", encoding="raw", format="plain", compress="raw", status=3):
        super(AudioBodyField, self).__init__(key, AUDIO)
        self.data_type = AUDIO
        self.path = self._check_path(path)
        self.key = key
        self.audio = b" "
        self.encoding = encoding
        self.status = status
        self.compress = compress
        self.format = format

    @property
    def test_value(self):
        if not os.path.exists(self.path):
            log.warn("%s not exist.. check " % self.path)
            return b""

        with open(self.path, "rb") as f:
            return f.read()


class ImageBodyField(PayloadField):
    def __init__(self, key, path="", need_base64=False, encoding="jpg", status=3):
        super(ImageBodyField, self).__init__(key, IMAGE)
        self.need_base64 = need_base64
        self.data_type = IMAGE
        self.path = self._check_path(path)
        self.key = key
        self.encoding = encoding
        self.status = status
        self.image = self.test_value

    @property
    def test_value(self):
        if not os.path.exists(self.path):
            log.warn("%s not exist.. check " % self.path)
            return b"<your image base64 here>"

        with open(self.path, "rb") as f:
            content = f.read()
            if not self.need_base64:
                return content
            else:
                return base64.b64encode(content)


class StringParamField(ParamField):
    def __init__(self, key, minLength=0, maxLength=1024, enums=[], required=False, value="", description="", title=""):
        self.key = key
        self.data_type = "string"
        self.max_length = maxLength
        self.min_length = minLength
        self.value = value
        self.enums = enums
        self.required = required
        self.description = description
        self.title = title

    def _schema(self):
        # todo enhance
        sc = {self.key: {"type": self.data_type}}
        if self.enums:
            sc[self.key]['enum'] = self.enums
        else:
            sc[self.key]['maxLength'] = self.max_length
        return sc

    def _to_dict(self):
        if not self.enums:
            return {self.key: {
                "type": self.data_type,
                "minLength": self.min_length,
                "maxLength": self.max_length
            }}
        return {self.key: {
            "type": self.data_type,
            "enum": self.enums
        }}

    @property
    def test_value(self):
        return self.value


class NumberParamField(ParamField):
    def __init__(self, key, minimum=0, maximum=100, enums=[], required=False, value=0):
        super(NumberParamField, self).__init__(key, "number")
        self.key = key
        self.enums = enums
        self.data_type = "number"
        self.minimum = minimum
        self.maximum = maximum
        self.value = value
        self.required = required

    def _schema(self):
        # todo enhance
        sc = {self.key: {"type": self.data_type}}
        if self.enums:
            sc[self.key]['enum'] = self.enums
        else:
            sc[self.key]['maximum'] = self.maximum
        return sc

    def _to_dict(self):
        if not self.enums:
            return {self.key: {
                "type": self.data_type,
                "minimum": self.minimum,
                "maximum": self.maximum
            }}
        return {self.key: {
            "type": self.data_type,
            "enum": self.enums
        }}

    @property
    def test_value(self):
        return self.value


class IntegerParamField(ParamField):
    def __init__(self, key, minimum=0, maximum=100, enums=[], required=False, value=0):
        self.enums = enums
        self.key = key
        self.data_type = "integer"
        self.minimum = minimum
        self.maximum = maximum
        self.required = required
        self.value = value

    def _schema(self):
        # todo enhance
        sc = {self.key: {"type": self.data_type}}
        if self.enums:
            sc[self.key]['enum'] = self.enums
        else:
            sc[self.key]['maximum'] = self.maximum
        return sc

    def _to_dict(self):
        if not self.enums:
            return {self.key: {
                "type": self.data_type,
                "minimum": self.minimum,
                "maximum": self.maximum
            }}
        return {self.key: {
            "type": self.data_type,
            "enum": self.enums
        }}

    @property
    def test_value(self):
        return self.value


class BooleanParamField(ParamField):
    def __init__(self, key, title="", default=False, required=False):
        self.key = key
        self.data_type = "boolean"
        self.required = required
        self.default = default
        self.title = title

    def _schema(self):
        # todo enhance
        return {self.key: {"type": self.data_type, "default": self.default}}

    def _to_dict(self):
        return {self.key: {
            "type": self.data_type,
        }}

    @property
    def test_value(self):
        return self.default


# metaclass是类的模板，所以必须从`type`类型派生：
class Metaclass(type):
    def __new__(cls, name, bases, attrs):
        if name == 'AseProto':
            return type.__new__(cls, name, bases, attrs)

        print('Found proto: %s' % name)
        mappings = dict()
        mappings['inputs'] = []
        mappings['accepts'] = []
        mappings['params'] = []
        for k, v in attrs.items():
            if k == "requestCls":
                for kk, vv in v.__class__.__dict__.items():
                    if isinstance(vv, PayloadField):
                        mappings['inputs'].append(vv)
                    if isinstance(vv, ParamField):
                        mappings['params'].append(vv)

            if k == "responseCls":
                for kk, vv in v.__class__.__dict__.items():
                    if kk.startswith("accept") or isinstance(vv, PayloadField):
                        mappings['accepts'].append(vv)
            if k == "call":
                mappings['call'] = v
            if k == "sub":
                mappings['sub'] = v
            if k == "route":
                mappings['route'] = v
            if k == "call_type":
                mappings['call_type'] = v

        attrs['__mappings__'] = mappings  # 保存属性和列的映射关系
        return type.__new__(cls, name, bases, attrs)


class WrapperBase(metaclass=Metaclass):
    config = {}

    def __init__(self, legacy=True, is_aipaas=True, keep_schema_default_value=True):
        # 仅测试调试用
        self.inputs_test_values = {}
        self.params_test_values = {}
        self.respData = []
        self.session = SessionManager()
        self.legacy = legacy
        self.is_aipaas = is_aipaas
        self.keep_schema_default_value = keep_schema_default_value
        self._schema = None

    def gradio(self):
        from aiges.gradio_util.component import GradioComponent
        import gradio as gr
        if self._schema:
            g = GradioComponent(self._schema)
            g.run()
        pass

    def schema(self):
        '''传统模式默认: 基于模板生成schema'''
        if self.legacy:
            return self.schema_legacy()
        else:
            return self.schema_v2()

    def schema_v2(self):
        '''
        基于pydantic 生成 schema
        '''
        args = self._parse_mapping()

        svcId = args.get("serviceId")
        inputs_fields, inputs_payloads = self._parse_inputs_v2()
        accepts_fields, accepts_payloads = self._parse_outputs_v2()
        ParamModel = self._parse_params_v2(svcId, accepts_payloads)

        # check meta input output
        for k, v in inputs_fields.items():
            Input.add_key_datatype(k, v.get('dataType'))

        _in = Input()
        for k, v in accepts_fields.items():
            Accept.add_key_datatype(k, v.get('dataType'))
        _accept = Accept()
        svcdict = {svcId: {"input": _in, "accept": _accept}}

        args.update(svcdict)
        MetaModel = create_model(
            'MetaModel',
            __base__=Meta,
            **args,
        )

        # prepare schemainput
        ## 1. payload
        tmp = dict()
        for k, v in inputs_payloads.items():
            tmp[k] = v

        PayloadModel = create_model(
            'PayloadModel',
            __base__=Payload,
            **tmp
        )
        # todo:  appid status parameterize
        sin = {"payload": PayloadModel(), "header": Header(appid="11", status="3"), "parameter": ParamModel()}
        SchemaInputModel = create_model(
            'SchemaInputModel',
            **sin,
            __base__=BaseModel
        )
        _sin = SchemaInputModel()

        # 2. preprare output palyoad
        OutputPayloadModel = create_model(
            'OutputPayloadModel',
            __base__=BaseModel,
            **accepts_payloads
        )
        _output_payload = {"payload": OutputPayloadModel()}
        OutputModel = create_model("OutputModel",
                                   __base__=BaseModel, **_output_payload)

        # return  _sin.schema_json()
        sc = AIschema(meta=MetaModel(), schemainput=SchemaInputModel(), schemaoutput=OutputModel(),
                      is_aipaas=self.is_aipaas, keep_default=self.keep_schema_default_value)
        log.info("Generating V2 Schema....")
        self._schema = sc
        return json.dumps(sc.json())

    def schema_legacy(self):
        s = Template(tpl)
        kwargs = self._parse_mapping()
        inputs_fields, inputs_body = self._parse_inputs()
        accepts_fields, accepts_payloads = self._parse_outputs()
        params_fields, required_params = self._parse_params()
        kwargs.update({"parameters": json.dumps(params_fields)})
        kwargs.update({"inputs_fields": json.dumps(inputs_fields)})
        kwargs.update({"accepts_fields": json.dumps(accepts_fields)})
        kwargs.update({"required_paramters": json.dumps(required_params)})
        kwargs.update({"inputs_payload": json.dumps(inputs_body)})
        kwargs.update({"accepts_payloads": json.dumps(accepts_payloads)})

        msg = {}
        try:
            msg = json.loads(s.render(**kwargs))
        except Exception as e:
            raise AttributeError("cant' format to schema %s" % str(e))
        log.info("Generating Legacy Schema...")
        data = json.dumps(msg, indent=4, ensure_ascii=False)
        return data

    def _parse_inputs(self):
        inputs = self.__mappings__.get('inputs', [])
        if not inputs:
            raise Exception("your must specify at least one input field!")
        inputs_payloads = {}
        inputs_fields = {}
        for inp in inputs:
            if inp.data_type == IMAGE:
                inputs_fields.update({inp.key: {"dataType": "image"}})
                self.inputs_test_values.update({inp.key: inp.test_value})
                inputs_payloads.update(self._get_image_inputs_payload(inp.key))
            elif inp.data_type == AUDIO:
                inputs_fields.update({inp.key: {"dataType": "audio"}})
                self.inputs_test_values.update({inp.key: inp.test_value})
                inputs_payloads.update(self._get_audio_inputs_payload(inp.key))
            elif inp.data_type == STRING:
                inputs_fields.update({inp.key: {"dataType": "text"}})
                self.inputs_test_values.update({inp.key: inp.test_value})

                inputs_payloads.update(self._get_text_accepts_payload(inp.key))
        return inputs_fields, inputs_payloads

    def _parse_inputs_v2(self):
        inputs = self.__mappings__.get('inputs', [])
        if not inputs:
            raise Exception("your must specify at least one input field!")
        inputs_payloads = {}
        inputs_fields = {}
        for inp in inputs:
            if inp.data_type == IMAGE:
                inputs_fields.update({inp.key: {"dataType": "image"}})
                self.inputs_test_values.update({inp.key: inp.test_value})
                i = ImageField(encoding=inp.encoding, status=inp.status, image=b"test")
                inputs_payloads.update({inp.key: i})
            elif inp.data_type == AUDIO:
                inputs_fields.update({inp.key: {"dataType": "audio"}})
                self.inputs_test_values.update({inp.key: inp.test_value})
                i = AudioField(encoding=inp.encoding, status=inp.status, audio=b"test")
                inputs_payloads.update({inp.key: i})
            elif inp.data_type == STRING:
                inputs_fields.update({inp.key: {"dataType": "text"}})
                self.inputs_test_values.update({inp.key: inp.test_value})
                i = TextField(encoding=inp.encoding, status=inp.status, text=inp.text, compress=inp.compress,
                              format=inp.format)
                inputs_payloads.update({inp.key: i})
        return inputs_fields, inputs_payloads

    def _parse_outputs_v2(self):
        accepts = self.__mappings__.get('accepts', [])
        if not accepts:
            raise Exception("your must specify at least one accepts field!")
        accepts_payloads = {}
        accepts_fields = {}
        for acc in accepts:
            if acc.data_type == IMAGE:
                accepts_fields.update({acc.key: {"dataType": "image"}})
                i = ImageField(encoding=acc.encoding, status=acc.status, image=acc.image)
                accepts_payloads.update({acc.key: i})
            elif acc.data_type == AUDIO:
                accepts_fields.update({acc.key: {"dataType": "audio"}})
                i = AudioField(encoding=acc.encoding, status=acc.status, image=acc.audio)
                accepts_payloads.update({acc.key: i})
            elif acc.data_type == STRING:
                accepts_fields.update({acc.key: {"dataType": "text"}})
                i = TextField(encoding=acc.encoding, status=acc.status, text=acc.text, compress=acc.compress,
                              format=acc.format)
                accepts_payloads.update({acc.key: i})
            ## binary support todo
        return accepts_fields, accepts_payloads

    def _parse_outputs(self):
        accepts = self.__mappings__.get('accepts', [])
        if not accepts:
            raise Exception("your must specify at least one accepts field!")
        accepts_payloads = {}
        accepts_fields = {}
        for acc in accepts:
            if acc.data_type == IMAGE:
                accepts_fields.update({acc.key: {"dataType": "image"}})
                accepts_payloads.update(self._get_image_inputs_payload(acc.key))
            elif acc.data_type == AUDIO:
                accepts_fields.update({acc.key: {"dataType": "audio"}})
                accepts_payloads.update(self._get_audio_inputs_payload(acc.key))
            elif acc.data_type == STRING:
                accepts_fields.update({acc.key: {"dataType": "text"}})
                accepts_payloads.update(self._get_text_accepts_payload(acc.key))
            ## binary support todo
        return accepts_fields, accepts_payloads

    def _parse_mapping(self):
        call = self.__mappings__.get("call", "atmos")
        call_type = self.__mappings__.get("call_type", 0)
        route = self.__mappings__.get("route", "/{}/private/{}".format(self.version, self.serviceId))
        sub = self.__mappings__.get("sub", "ase")
        hosts = self.__mappings__.get("hosts", "api.xf-yun.com")
        webgate_type = self.__mappings__.get("webgate_type", 0)
        args = dict()
        args['serviceId'] = self.serviceId
        if self.legacy:
            args['service'] = json.dumps([self.serviceId])
        else:
            args['service'] = [self.serviceId]
        args['version'] = self.version
        args['call'] = call
        args['call_type'] = call_type
        args['route'] = route
        args['sub'] = sub
        args['hosts'] = hosts
        args['webgate_type'] = webgate_type
        return args

    def _parse_params(self):
        params = self.__mappings__.get('params', [])
        params_fields = {}
        required_params = []
        for param in params:
            if param.required:
                required_params.append(param.key)
            params_fields.update(param._schema())
            self.params_test_values.update()
            self.params_test_values[param.key] = param.test_value
        return params_fields, required_params

    def _parse_params_v2(self, serviceId, accepets_payloads):
        params = self.__mappings__.get('params', [])
        a_dict = {}
        _dict = {}
        for param in params:
            if isinstance(param, StringParamField):
                if param.required:
                    _dict[param.key] = (str, PField(default="cc", title='Foo', max_length=10, min_length=0))
                else:
                    _dict[param.key] = (Optional[str], PField(title='Foo', max_length=10, min_length=0))
            elif isinstance(param, NumberParamField):
                if param.required:
                    _dict[param.key] = (int, PField(title=param.title, gt=param.minimum, le=param.maximum))
                else:
                    _dict[param.key] = (Optional[int], PField(title=param.title, gt=param.minimum, le=param.maximum))
            elif isinstance(param, BooleanParamField):
                if param.required:
                    _dict[param.key] = (bool, PField(title=param.title, default=param.default))
                else:
                    _dict[param.key] = (Optional[bool], PField(title=param.title, default=param.default))

            # if param.required:
            #     # todo param required should do here
            #     _dict[param.key] = param.test_value
            # else:
            #     _dict[param.key] = param.test_value

        # 这里是处理 accept parameters expect
        for k, v in accepets_payloads.items():
            _dict[k] = v

        TmpModel = create_model("TempModel", __base__=BaseModel, **_dict)
        a_dict[serviceId] = TmpModel()

        Paramodel = create_model(
            'Paramodel',
            __base__=BaseModel,
            **a_dict,
        )
        return Paramodel

    def _parse_params_v2_old(self, serviceId, accepets_payloads):
        params = self.__mappings__.get('params', [])

        _dict = {}
        for param in params:
            if isinstance(param, StringParamField):
                if param.required:
                    _dict[param.key] = (str, PField(default="cc", title='Foo', max_length=10, min_length=0))
                else:
                    _dict[param.key] = (Optional[str], PField(title='Foo', max_length=10, min_length=0))
            elif isinstance(param, NumberParamField):
                if param.required:
                    _dict[param.key] = (int, PField(title=param.title, gt=param.minimum, le=param.maximum))
                else:
                    _dict[param.key] = (Optional[int], PField(title=param.title, gt=param.minimum, le=param.maximum))
            elif isinstance(param, BooleanParamField):
                if param.required:
                    _dict[param.key] = (bool, PField(title=param.title, default=param.default))
                else:
                    _dict[param.key] = (Optional[bool], PField(title=param.title, default=param.default))

            # if param.required:
            #     # todo param required should do here
            #     _dict[param.key] = param.test_value
            # else:
            #     _dict[param.key] = param.test_value

        a_dict = {}

        # 这里是处理 accept parameters expect
        for k, v in accepets_payloads.items():
            a_dict[k] = v

        TmpModel = create_model("TempModel", __base__=BaseModel, **a_dict)
        _dict[serviceId] = TmpModel()

        Paramodel = create_model(
            'Paramodel',
            __base__=BaseModel,
            **_dict,
        )
        return Paramodel

    def _parse_payload(self):
        pass

    def _get_image_inputs_payload(self, key):
        return {
            key: {
                "type": "object",
                "properties": {
                    "encoding": {
                        "type": "string",
                        "enum": ["jpg", "png", "bmp", "jpeg"]
                    },
                    "image": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 10485760
                    },
                    "status": {
                        "type": "integer",
                        "enum": [3]
                    }
                }
            }
        }

    def _get_audio_inputs_payload(self, key):
        return {
            key: {
                "type": "object",
                "properties": {
                    "encoding": {
                        "type": "string",
                        "enum": [
                            "opus",
                            "speex"
                        ]
                    },
                    "sample_rate": {
                        "type": "integer",
                        "enum": [
                            8000,
                            16000
                        ]
                    },
                    "bit_depth": {
                        "type": "integer",
                        "enum": [
                            8,
                            16
                        ]
                    },
                    "channels": {
                        "type": "integer",
                        "enum": [
                            1,
                            2
                        ]
                    },
                    "status": {
                        "type": "integer",
                        "enum": [
                            0,
                            1,
                            2,
                            3
                        ]
                    },
                    "seq": {
                        "type": "integer"
                    },
                    "audio": {
                        "type": "string"
                    }
                }
            }
        }

    def _get_text_inputs_payload(self, key):
        return {
            key: {
                "type": "object",
                "properties": {
                    "encoding": {
                        "type": "string",
                        "enum": [
                            "utf8",
                            "gb2312"
                        ]
                    },
                    "status": {
                        "type": "integer",
                        "enum": [
                            0,
                            1,
                            2,
                            3
                        ]
                    },
                    "seq": {
                        "type": "integer"
                    },
                    "text": {
                        "type": "string"
                    }
                }
            }
        }

    def _get_text_accepts_payload(self, key):
        return {
            key: {
                "type": "object",
                "properties": {
                    "encoding": {
                        "type": "string",
                        "enum": [
                            "utf8",
                            "gb2312"
                        ]
                    },
                    "compress": {
                        "type": "string",
                        "enum": [
                            "gzip"
                        ]
                    },
                    "status": {
                        "type": "integer",
                        "enum": [
                            0,
                            1,
                            2,
                            3
                        ]
                    },
                    "seq": {
                        "type": "integer"
                    },
                    "text": {
                        "type": "string"
                    }
                }
            }
        }

    '''
    服务初始化
    @param config:
        插件初始化需要的一些配置，字典类型
        key: 配置名
        value: 配置的值
    @return
        ret: 错误码。无错误时返回0
    '''

    def wrapperInit(cls, config: {}) -> int:
        raise NotImplementedError("Please Inplement Wrapper Class Method: wrapperInit(cls, config: {}) ")

    '''
    服务逆初始化

    @return
        ret:错误码。无错误码时返回0
    '''

    def wrapperFini(cls) -> int:
        raise NotImplementedError("Please Inplement Wrapper Class Method: wrapperFini(cls) ")

    '''
    非会话模式计算接口,对应oneShot请求,可能存在并发调用

    @param usrTag 句柄
    #param params 功能参数
    @param  reqData     写入数据实体
    @param  respData    返回结果实体,内存由底层服务层申请维护,通过execFree()接口释放
    @param psrIds 需要使用的个性化资源标识列表
    @param psrCnt 需要使用的个性化资源个数

    @return 接口错误码
        reqDat
        ret:错误码。无错误码时返回0
    '''

    def wrapperOnceExec(cls, params: {}, reqData: DataListCls, usrTag: str = "") -> Response:
        raise NotImplementedError(
            "Please Inplement Wrapper Class Method: wrapperOnceExec(cls, usrTag: str, params: {}, reqData: [], respData: [], psrIds: [], psrCnt: int) ")

    def wrapperOnceExecAsync(cls, params: {}, reqData: DataListCls, sid: str) -> Response:
        raise NotImplementedError(
            "Please Inplement Wrapper Class Method: wrapperOnceExec(cls, usrTag: str, params: {}, reqData: [], respData: [], psrIds: [], psrCnt: int) ")

    def wrapperError(cls, ret: int) -> str:
        if ret == 100:
            return "This is a  error return"
        return ""

    '''
        保留接口
    '''

    def wrapperCreate(cls, params: {}, sid: str, userTag: str = "") -> SessionCreateResponse:
        print(params)

        print(sid)
        return

    '''
        保留接口
    '''

    def wrapperWrite(cls, handle: str, datas: [], sid: str) -> int:
        return 0

    '''
        保留接口
    '''

    def wrapperRead(cls, handle: str, sid: str) -> []:
        return []

    def wrapperDestroy(cls, handle: str) -> int:
        return 0

    def check_resp(self, resp) -> bool:

        if not isinstance(resp, Response):
            log.error("Please return Response instance in function wrapperOnceExec")
            return False

        # check 响应list长度
        if len(resp.list) == 0:
            log.error("Please return content in response.list")
            return False

        if resp.error_code != 0:
            return True

        for d in resp.list:
            # check Response data 类型
            if not isinstance(d.data, memoryview) and not isinstance(d.data, bytes):
                log.error("ResponseData 's data field must be  bytes or memoryview")
                return False
            if d.len != len(d.data):
                log.error(
                    "ResponseData: key: %s 's len is mismatch,Please Check! expect %d, actual: %d" % (
                        d.key, d.len, len(d.data)))
                return False

        # check 响应key是否重复
        keys = [r.key for r in resp.list]
        set_keys = set(keys)
        log.info("response keys: %s", str(keys))
        if not len(keys) == len(set_keys):
            log.error("response list keys must be u nique...")
            log.error("invalid keys %s" % str(keys))
            return False

        return True

    def run(self, stream=False):
        if not stream:
            self.run_once()
        else:
            self.run_stream()

    def run_once(self):
        # 1. 模拟调用初始化引擎
        #  传入配置当前模拟为空
        self.wrapperInit(self.config)

        try:
            # 2. 准备wrapperOnceExec需要的数据
            inputs_fields, inputs_body = self._parse_inputs()

            params_fields, required_params = self._parse_params()
            params = self.params_test_values
            reqData = []
            reqData.append(self.inputs_test_values)
            req = DataListCls()
            tmp = []
            for key, value in self.inputs_test_values.items():
                node = DataListNode()
                node.key = key
                node.data = value
                node.len = len(value)
                typeStr = inputs_fields[key]["dataType"]
                node.type = type_map.get(typeStr)
                tmp.append(node)

            req.list = tmp
            # 3. 模拟调用 exec，并返回数据
            response = self.wrapperOnceExec(params, req)
            if self.check_resp(response):
                log.info("wrapper.py has been verified... Congratulations ...!")
            else:
                log.error("Sorry, Please Check The Log Output Above ...")
        except Exception as e:
            # 4. 模拟检查 wrapperOnceExec返回
            log.error(e)
            self.wrapperError(-1)

    def run_stream(self):
        q = init_rq()
        # 1. 模拟调用初始化引擎
        #  传入配置当前模拟为空
        self.wrapperInit(self.config)
        # 2. 准备wrapperOnceExec需要的数据
        inputs_fields, inputs_body = self._parse_inputs()

        params_fields, required_params = self._parse_params()
        params = self.params_test_values
        # 2. 模拟流式创建会话
        req = DataListCls()
        tmp = []
        for key, value in self.inputs_test_values.items():
            node = DataListNode()
            node.key = key
            node.data = value
            node.len = len(value)
            typeStr = inputs_fields[key]["dataType"]
            node.type = type_map.get(typeStr)
            tmp.append(node)

        req.list = tmp

        sid = "test-111111"
        sb = self.wrapperCreate(params, sid)
        print("get sb 's handle ,%s", sb.handle)
        self.wrapperWrite(sb.handle, req, sid)
        is_stopping = False
        while not is_stopping:
            r = q.get()
            for i in r.list:
                if i.status == DataEnd:
                    print("end!!!!")
                    is_stopping = True
