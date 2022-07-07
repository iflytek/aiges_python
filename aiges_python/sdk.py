# coding: utf-8

## const default value
import base64

from jinja2 import Template
import json
import os
from pprint import pprint

SUB = "ase"
CALL = "atmos"
CALL_TYPE = 0
HOSTS = [
    "api.xf-yun.com"
]
ROUTEKEY = []

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

STRING = 0
AUDIO = 1
IMAGE = 2
VIDEO = 3


class Field(object):
    def __init__(self, key, data_type):
        self.key = key
        self.data_type = data_type

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.key)

    def _check_path(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError
        return path

    def _encode(self, dataTye, encoding, binary):
        print("Not implement here , just give back")
        return binary

    @property
    def test_value(self):
        return NotImplementedError


class StringBodyField(Field):
    def __init__(self, key, value="", need_base64=False):
        super(StringBodyField, self).__init__(key, STRING)
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


class AudioBodyField(Field):
    def __init__(self, key, path=""):
        super(AudioBodyField, self).__init__(key, AUDIO)
        self.data_type = AUDIO
        self.path = self._check_path(path)
        self.key = key

    @property
    def test_value(self):
        with open(self.path, "rb") as f:
            return f.read()


class ImageBodyField(Field):
    def __init__(self, key, path="", need_base64=False):
        super(ImageBodyField, self).__init__(key, IMAGE)
        self.need_base64 = need_base64
        self.data_type = IMAGE
        self.path = self._check_path(path)
        self.key = key

    @property
    def test_value(self):
        with open(self.path, "rb") as f:
            content = f.read()
            if not self.need_base64:
                return content
            else:
                return base64.b64encode(content)


class StringParamField(Field):
    def __init__(self, key, minLength=0, maxLength=50, enums=[], required=False):
        self.key = key
        self.data_type = "string"
        self.max_length = maxLength
        self.min_length = minLength
        self.enums = enums
        self.required = required

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


class NumberParamField(Field):
    def __init__(self, key, minimum=0, maximum=100, enums=[], required=False):
        self.key = key
        self.enums = enums
        self.data_type = "number"
        self.minimum = minimum
        self.maximum = maximum
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


class IntegerParamField(Field):
    def __init__(self, key, minimum=0, maximum=100, enums=[], required=False):
        self.enums = enums
        self.key = key
        self.data_type = "integer"
        self.minimum = minimum
        self.maximum = maximum
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


class BooleanParamField(Field):
    def __init__(self, key, default=False, required=False):
        self.key = key
        self.data_type = "boolean"
        self.default = default
        self.required = required

    def _schema(self):
        # todo enhance
        return {self.key: {"type": self.data_type, "default": self.default}}

    def _to_dict(self):
        return {self.key: {
            "type": self.data_type,
        }}


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
                    if kk.startswith("input"):
                        mappings['inputs'].append(vv)
                    if kk.startswith("params"):
                        mappings['params'].append(vv)

            if k == "responseCls":
                for kk, vv in v.__class__.__dict__.items():
                    if kk.startswith("accept"):
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


class AIserviceManager(metaclass=Metaclass):
    def schema(self):
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
            raise AttributeError("cant' format to schma %s" % str(e))

        print(json.dumps(msg, indent=4, ensure_ascii=False))

        # pprint(inputs_body)
        # pprint(inputs_fields)
        # pprint(accepts_fields)

        # schema1 = json.loads(msg)
        return

    def _parse_inputs(self):
        inputs = self.__mappings__.get('inputs', [])
        if not inputs:
            raise Exception("your must specify at least one input field!")
        inputs_payloads = {}
        inputs_fields = {}
        for inp in inputs:
            if inp.data_type == IMAGE:
                inputs_fields.update({inp.key: {"dataType": "image"}})
                inputs_payloads.update(self._get_image_inputs_payload(inp.key))
            elif inp.data_type == AUDIO:
                inputs_fields.update({inp.key: {"dataType": "audio"}})
                inputs_payloads.update(self._get_audio_inputs_payload(inp.key))
            elif inp.data_type == STRING:
                inputs_fields.update({inp.key: {"dataType": "text"}})
                inputs_payloads.update(self._get_text_accepts_payload(inp.key))
        return inputs_fields, inputs_payloads

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
        call_type = self.__mappings__.get("call_type", "0")
        route = self.__mappings__.get("route", "/v1/private/{}".format(self.serviceId))
        sub = self.__mappings__.get("sub", "ase")
        hosts = self.__mappings__.get("hosts", "api.xf-yun.com")
        args = dict()
        args['serviceId'] = self.serviceId
        args['service'] = json.dumps([self.serviceId])
        args['version'] = self.version
        args['call'] = call
        args['call_type'] = call_type
        args['route'] = route
        args['sub'] = sub
        args['hosts'] = hosts
        return args

    def _parse_params(self):
        params = self.__mappings__.get('params', [])
        params_fields = {}
        required_params = []
        for param in params:
            if param.required:
                required_params.append(param.key)
            params_fields.update(param._schema())
        return params_fields, required_params

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

