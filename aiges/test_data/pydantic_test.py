# !/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: pydantic_test
@time: 2023/01/14
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
from typing import Optional

from pydantic import BaseModel, create_model, ConstrainedStr
from pydantic.fields import FieldInfo

# DynamicFoobarModel = create_model('DynamicFoobarModel', foo=(str, FieldInfo(title='Foo',max_length=10,min_length=0)), bar=(int, FieldInfo(title='Foo',gt=0,lt=100)))
DynamicFoobarModel = create_model('DynamicFoobarModel',
                                  **{"foo": (str, FieldInfo(title='Foo', max_length=10, min_length=0),
                                             ),
                                     "bar": (Optional[int], FieldInfo(title='Foo', gt=0, le=100,))},
                                  )

print(DynamicFoobarModel.schema())
