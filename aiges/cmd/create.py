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
import datetime

import os
import shutil
from typing import Any
from jinja2 import Environment
import aiges
from aiges.utils.log import log

WRAPPER_DIR = "wrapper"
TPL_DIR = os.path.join(os.path.dirname(aiges.__file__), "tpls")

template_env: Any = Environment(
    extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols"],
    trim_blocks=True,
    lstrip_blocks=True,
)


def _load_template(tpl):
    if not os.path.exists(tpl):
        raise FileNotFoundError("not found %s" % tpl)
    log.info("load success %s" % tpl)
    return template_env.from_string(open(tpl, "r").read())


def load_readme():
    tpl = os.path.join(TPL_DIR, "Readme.md.j2")
    return _load_template(tpl)


def load_requirements():
    tpl = os.path.join(TPL_DIR, "requirements.txt.j2")
    return _load_template(tpl)


def load_dockerfile():
    tpl = os.path.join(TPL_DIR, "Dockerfile.j2")
    return _load_template(tpl)


def load_wrapper():
    tpl = os.path.join(TPL_DIR, "wrapper.py.j2")
    return _load_template(tpl)


def create_project(args):
    project_name = args.name
    project_path = args.path
    log.info("creating project: %s" % project_name)
    # todo
    # 1. 创建 project目录
    # 2. 渲染readme.md
    # 3. 渲染 wrapper.py
    # 4. 渲染 dockerfile
    # 5. 渲染 requirments.txt
    # 假设先实现1个readme,以下是demo， 请自己优化
    initialize_project_dir(project_name, project_path)


def initialize_project_dir(project_name, project_path):
    """

    :param project_name:  待初始化项目名称
    :param project_path:  待初始化项目地址
    :return:
    """
    # todo
    # 1. 创建 project_name的目录
    # 2. di
    abs = os.path.join(project_path, project_name)
    abs_wrapper_dir = os.path.join(abs, WRAPPER_DIR)
    os.makedirs(abs, exist_ok=True)
    os.makedirs(abs_wrapper_dir, exist_ok=True)

    # 创建示例 wrapper.py
    log.info("Templates file dir: %s" % TPL_DIR)
    tpls = os.listdir(TPL_DIR)
    log.info("Templates: %s" % str(tpls))
    wrapper_t = load_wrapper()
    wrapper_vars = {
        "datetime": datetime.datetime.now(),
        "project_name": project_name,
        "project_path": project_path
    }
    wfile = os.path.join(abs_wrapper_dir, "wrapper.py")
    log.info("Generating: %s" % wfile)
    with open((wfile), "wb") as wf:
        wf.write(wrapper_t.render(vars=wrapper_vars).encode('utf-8'))
        wf.close()
    log.info("Generated: %s >>> Done" % wfile)

    # 创建 Readme.md
    readme_t = load_readme()
    readme_vars = {
        "project_name": project_name,
        "project_path": project_path,
        "test": 'for test',

    }
    readme_file = os.path.join(abs, "README.md")
    log.info("Generating: %s" % readme_file)
    with open(readme_file, 'wb') as rf:
        rf.write(readme_t.render(vars=readme_vars).encode('utf-8'))
        rf.close()
    log.info("Generated: %s >>> Done" % readme_file)

    # 创建 requirements.txt
    require_t = load_requirements()
    require_vars = {}
    require_file = os.path.join(abs, "requirements.txt")
    log.info("Generating: %s" % require_file)
    with open(require_file, 'wb') as rf:
        rf.write(require_t.render(vars=require_vars).encode('utf-8'))
        rf.close()
    log.info("Generated: %s >>> Done" % require_file)

    # 创建 Dockerfile
    dockerfile_t = load_dockerfile()
    dockerfile_vars = {}
    dockerfile_file = os.path.join(abs, "Dockerfile")
    log.info("Generating: %s" % dockerfile_file)
    with open(dockerfile_file, 'wb') as rf:
        rf.write(dockerfile_t.render(vars=dockerfile_vars).encode('utf-8'))
        rf.close()
    log.info("Generated: %s >>> Done" % dockerfile_file)

    # 创建测试数据目录
    test_data = os.path.join(abs_wrapper_dir, "test_data")
    os.makedirs(test_data,exist_ok=True)
    test_png = os.path.join(abs_wrapper_dir, "test_data","test.png")
    shutil.copy(os.path.join(os.path.dirname(aiges.__file__),"test_data","test.png"), test_png)
