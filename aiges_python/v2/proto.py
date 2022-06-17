# coding: utf-8

## const default value

from jinja2 import Template
import json

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
        "hosts":{{ hosts}},
        "service": {{service}},
        "routeKey":[
		],
		"$svcNickName1":{
            "input":{
                "$input1":"$dataType",
                "$input2":"$dataType"
            },
            "accept":{
                "$accept1":{
                    "dataType":"$dataType"
                },
                "$accept2":{
                    "dataType":"$dataType",
                    "controlPara":"$key1",
                    "controlType":"key"
                }
            }
        },
        "$svcNickName2":{
            "input":{
                "$input1":"$dataType",
                "$input2":"$dataType"
            },
            "accept":{
                "$accept1":{
                    "dataType":"$dataType"
                },
                "$accept2":{
                    "dataType":"$dataType",
                    "controlPara":"$key1",
                    "controlType":"value",
                    "controlValue":[
                        "$value1"
                    ]
                }
            }
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
                    "$svcNickName":{
                        "type":"object",
                        "properties":{
                            "$key1":{
                                "type":"string",
                                "maxLength":50
                            },
                            "$key2":{
                                "type":"number",
                                "minimum":0,
                                "maximum":100
                            },
                            "$key3":{
                                "type":"integer",
                                "minimum":0,
                                "maximum":100
                            },
                            "$key4":{
                                "type":"boolean"
                            },
                            "$accept1":{
                                "type":"object",
                                "properties":{
                                    "encoding":{
                                        "type":"string",
                                        "enum":[
                                            "utf8",
                                            "gb2312"
                                        ]
                                    },
                                    "compress":{
                                        "type":"string",
                                        "enum":[
                                            "gzip"
                                        ]
                                    }
                                }
                            }
                        },
                        "required":[
                            "$key1",
                            "$key4"
                        ]
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
                "properties": {{outputs_payload}}
            }
        }
    }
}
'''


class Field(object):
    def __init__(self, key, data_type):
        self.key = key
        self.data_type = data_type

    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.key)


class StringField(Field):
    def __init__(self, data_type, key, ):
        super(StringField, self).__init__(key, data_type)


# metaclass是类的模板，所以必须从`type`类型派生：
class Metaclass(type):
    def __new__(cls, name, bases, attrs):
        if name == 'AseProto':
            return type.__new__(cls, name, bases, attrs)

        print('Found proto: %s' % name)
        mappings = dict()
        mappings['inputs'] = []
        mappings['accepts'] = []
        for k, v in attrs.items():
            if k == "requestCls":
                for kk, vv in v.__class__.__dict__.items():
                    if kk.startswith("input"):
                        mappings['inputs'].append(vv)

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


class AseProto(metaclass=Metaclass):
    def schema(self):
        s = Template(tpl)
        kwargs = self._parse_mapping()

        msg = s.render(**kwargs)
        print(msg)
        inputs_schema = self._parse_inputs()
        #schema1 = json.loads(msg)
        return

    def _parse_inputs(self):
        inputs = self.__mappings__.get('inputs', [])
        if not inputs:
            raise Exception("your must specify at least one input field!")
        inputs_payloads = {}
        for inp in inputs:
            if inp.data_type == "image":
                 inputs_payloads.update(self._get_image_payload(inp.key))
            elif inp.data_type == "audio":
                 inputs_payloads.update(self._get_audio_payload(inp.key))

        return inputs_payloads

    def _parse_outputs(self):
        accepts = self.__mappings__.get('accepts', [])
        if not accepts:
            raise Exception("your must specify at least one accepts field!")
        accepts_payloads = {}
        for acc in accepts:
            pass



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

    def _parse_payload(self):
        pass

    def _get_image_payload(self, key):
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

    def _get_audio_payload(self, key):
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

    def _get_text_accepts_payload(self,key):
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