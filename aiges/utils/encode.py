from functools import wraps
import inspect
import numpy as np
import cv2
try:
    from aiges_embed import ResponseData, Response, DataListNode, DataListCls  # c++
except:
    from aiges.dto import Response, ResponseData, DataListNode, DataListCls


class encoder(object):
    def __init__(self,key,encoder_type="image",image_type="color"):
        self.encoder = encoder_type
        self.key = key
        self.image_type = image_type

    def __call__(self, func):

        @wraps(func)
        def wrapper(*args,**kwargs):
            all_args = inspect.getcallargs(func, *args, **kwargs)
            reqData = all_args.get('reqData')
            cls = all_args.get('cls')
            params = all_args.get('params')
            if self.encoder == "text":
                reqData.list[0].data = reqData.list[0].data.decode("utf-8")
                res = func(cls,params, reqData)
            elif self.encoder == "image":
                if self.image_type == "color":
                    reqData.list[0].data = cv2.imdecode(np.frombuffer(reqData.list[0].data, np.uint8), cv2.IMREAD_COLOR)
                elif self.image_type == "gray":
                    reqData.list[0].data = cv2.imdecode(np.frombuffer(reqData.list[0].data, np.uint8), cv2.IMREAD_GRAYSCALE)
                print(reqData.list[0].data.shape)
                res = func(cls,params, reqData)
            else:
                res = func(*args, **kwargs)
            return res
        return wrapper


