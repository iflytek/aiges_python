#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: flask_restx_test
@time: 2022/11/22
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
def test_Flas():
    # app = Flask(__name__)
    # api = Api(app, version='1.0', title='Sample API',
    #           description='A sample API',
    #           )

    api = Namespace("AISchema")
    todo = api.model('Todo', {
        'id': fields.Integer(readonly=True, description='The task unique identifier'),
        'task': fields.String(required=True, description='The task details')
    })

    schemaInput1 = api.model('schemaInput', {
        'required': ['header', "parameters", "payload"],
        'properties': {
            'header': {
                'type': 'object'
            },
            'parameter': {
                'type': 'object'
            },
            'payload': {
                'type': 'object'
            }
        },
        'type': 'object'
    })
    schemaInput1 = api.model("schemaInput", {
        "header": fields.Nested(todo),
        "parameter": fields.Nested(todo),
        "payload": fields.Nested(todo)
    })
    print(dir(schemaInput1))
    print(schemaInput1._schema)
    print(todo._schema)


def replace_value_in_dict(item, original_schema):
    if isinstance(item, list):
        return [replace_value_in_dict(i, original_schema) for i in item]
    elif isinstance(item, dict):
        if list(item.keys()) == ['$ref']:
            definitions = item['$ref'][2:].split('/')
            res = original_schema.copy()
            for definition in definitions:
                res = res[definition]
            return res
        else:
            return {key: replace_value_in_dict(i, original_schema) for key, i in item.items()}
    else:
        return item