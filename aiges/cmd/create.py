#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: create.py
@time: 2022/07/26
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

from typing import Any
from jinja2 import Environment
import os
from aiges.utils.log import log

template_env: Any = Environment(
    extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols"],
    trim_blocks=True,
    lstrip_blocks=True,
)

def _load_template(tpl):
    if not os.path.exists(tpl):
        raise FileNotFoundError("not found %s" % tpl)
    log.info("load success j2 file.")
    return template_env.from_string(open(tpl, "r").read())


def load_readme():
    tpl = "./tpls/Readme.md.j2"
    return _load_template(tpl)

def create_project(args):
    project_name = args.name
    project_path = args.path
    print("creating project")
    # todo
    # 1. 创建 project目录
    # 2. 渲染readme.md
    # 3. 渲染 wrapper.py
    # 4. 渲染 dockerfile
    # 5. 渲染 requirments.txt

    # 假设先实现1个readme,以下是demo， 请自己优化
    t = load_readme()
    vars = {
        "project_name":project_name,
        "project_path":project_path,
        "test":'for test',

    }
    print(t.render(vars = vars))
          

def initialize_project_dir(project_name, project_path):
    """

    :param project_name:  待初始化项目名称
    :param project_path:  待初始化项目地址
    :return:
    """
    # todo
    # 1. 创建 project_name的目录
    # 2. di
    pass


