#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: aiges_methods.py
@time: 2022/08/06
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
import logging
import os
from typing import Any, Dict, List, Tuple, Union
from aiges.utils.flask_utils import *
import yaml

logger = logging.getLogger(__name__)



def init_metadata(user_model: Any) -> Dict:
    """
    Call the user model to get the model init_metadata

    Parameters
    ----------
    user_model
        User defined class instance

    Returns
    -------
        Validated model metadata
    """
    # meta_user: load metadata defined in the user_model instance
    if hasattr(user_model, "init_metadata"):
        try:
            meta_user = user_model.init_metadata()
        except AigesMicroserviceException:
            meta_user = {}
            pass
    else:
        meta_user = {}

    if not isinstance(meta_user, dict):
        logger.error("init_metadata must return dict")
        meta_user = {}

    # meta_env: load metadata from environmental variable
    try:
        meta_env = yaml.safe_load(os.environ.get("MODEL_METADATA", "{}"))
    except yaml.YAMLError as e:
        logger.error(f"Reading metadata from MODEL_METADATA env variable failed: {e}")
        meta_env = {}

    meta = {**meta_user, **meta_env}

    try:
        return validate_model_metadata(meta)
    except SeldonInvalidMetadataError as e:
        logger.error(f"Metadata validation error\n{e}")
        logger.error(f"Failed to validate metadata {meta}")
        return None
