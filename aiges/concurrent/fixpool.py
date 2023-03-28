#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: fixpool
@time: 2023/03/02
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
from aiges.concurrent.pool import Pool
from aiges.worker import Worker

class FixedPool(Pool):
    """
    a pool fixed size, for limit the objs
    """
    capacity = 1
    allocated = 0
    pool = {}

    def set_capacity(self, c):
        self.capacity = c

    def get(self, key) -> Worker:
        return self.pool.get(key)

    def add(self, obj):
        if self.allocated >= self.capacity:
            return False, ""
        key = f"worker-{self.allocated}"
        self.pool[key] = obj
        self.allocated += 1
        return True, key

    def remove(self, key):
        if key in self.pool:
            self.pool.pop(key)
            self.allocated -= 1
        return True

    def clear_all(self):
        self.pool = {}
        self.allocated = 0


if __name__ == '__main__':
    p = FixedPool()
    p.set_capacity(1)
    p.add("cc", "cc")
    p.add("ccc", "cc")

    print(p.allocated)
