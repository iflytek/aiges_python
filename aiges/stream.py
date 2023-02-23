#!/usr/bin/env python
# coding:utf-8
""" 
@author: nivic ybyang7
@license: Apache Licence 
@file: stream
@time: 2022/09/20
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
import threading
from threading import Lock
from multiprocessing import Manager, Process
import aiges.core.types as ai_types
import time
import os
import queue

lock = Lock()


class SessionManager:
    """
    session管理器
    """

    def __init__(self, config={}, mode=ai_types.THREAD_MODE, nums=0):
        self.initialized = False
        self.code = 0

        self.handle_pool: Pool  # handle池子，对应handle绑定的计算资源可以自行控制
        self.lock = threading.Lock()

    def init_wrapper_config(self, config={}):
        self.wrapperConfig = config

    def init_handle_pool(self, mode, nums, ReqThreadCls):
        if mode == ai_types.THREAD_MODE:
            # 默认线程模式
            self.handle_pool = self.init_threads(ReqThreadCls, nums)
        elif mode == ai_types.PROCESS_MODE:
            # 进程+线程模式当前不可用
            self.handle_pool = self.init_processes(ReqThreadCls, 2, 5)
        else:
            self.handle_pool = self.init_threads(ReqThreadCls, nums)
        self.initialized = True

    def init_threads(self, ReqThreadCls, nums=10):
        # 线程模式
        return ThreadPool(ReqThreadCls, 0, nums)

    def init_processes(self, ReqThreadCls, procs=2, threads_per_cpu=5):
        # 进程\线程模式
        return ProcessThreadPool(ReqThreadCls, procs, threads_per_cpu)

    def get_session(self, handle):
        # 通过handle名获取 session ,实际上取的是thread
        s = None
        if self.handle_pool.workers:
            s = self.handle_pool.get_thread(handle)
        if not s:
            pass
        return s

    def set_idle_session(self, handle):
        self.handle_pool.set_idle(handle)

    def get_idle_handle(self):
        # 获取一个空闲的session
        _session = None
        with lock:
            handle, _session = self.handle_pool.get_idle_thread_handle()
            if not _session:
                return
            return handle

    def reset_session(self, handle):
        _session = self.handle_pool.reset_thread(handle)

    def push_back(self, handle):
        # 标记这个handle对应线程为空闲
        self.set_idle_session(handle)
        self.reset_session(handle)
        pass


class Pool:
    """
    基类Pool
    """

    def __init__(self):
        # 维护 workers
        self.workers = {}

    def get_thread(self, handle):
        raise NotImplementedError

    def get_idle_thread_handle(self):
        "获取一个空闲的 线程handle"
        for h, s in self.workers.items():
            if s.idle:
                _session = s
                s.is_idle = False
                return h, s

    def reset_thread(self, handle):
        "重置一个线程状态，根据handle名"
        t = self.workers.get(handle)
        if not t:
            return
        t.reset()

    def set_idle(self, handle):
        t = self.workers.get(handle)
        if not t:
            return
        t.is_idle = True


class ThreadPool(Pool):
    """
    简易线程pool， 用于记录handle 和thread 绑定关系
    """

    def __init__(self, reqDataThreadCls, processs_no=0, nums=10, ):
        self.workers = {}
        for i in range(0, nums):
            handle = "Process-{}-Thread-{}".format(str(processs_no), str(i))
            self.workers[handle] = WorkerThread(handle)
            self.workers[handle].setStreamHandleThreadClass(reqDataThreadCls)
            self.workers[handle].start()

    def get_thread(self, handle):
        return self.workers.get(handle)


class StreamHandleThread(threading.Thread):
    """
    流式处理worker线程基类:

    """

    def __init__(self, session_thread, in_q, out_q):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.is_stopping = False
        self.session_thread = session_thread  # 为worker线程的父线程
        self.in_q = in_q
        self.out_q = out_q

    def init_model(self, *args, **kwarg):
        raise NotImplementedError("implementhis")

    def stop(self):
        self.is_stopping = True

    def run(self):
        # 此方法需要子类重写
        self.init_model(self.session_thread.handle)
        while not self.is_stopping:
            time.sleep(100)
            # req = self.in_q.get()
            # if req.list[0].status == 2:
            #    self.session_thread.reset()


class WorkerProcess(Process):
    """
    TODO: Depreciated 进程线程模式当前不可用
    """

    def __init__(self, workers, reqDataThreadCls, process_no=0, threads_per_cpu=2):
        Process.__init__(self)
        self.workers = workers
        self.process_no = process_no
        self.threads_per_cpu = threads_per_cpu
        self.reqDataThreadCls = reqDataThreadCls
        self.process_id = None

    # 重写run方法
    def run(self):
        self.process_id = os.getpid()
        for i in range(0, self.threads_per_cpu):
            handle = "Process-{}-Thread-{}".format(str(os.getpid()), str(i))
            print(handle + "start")
            self.workers[handle] = WorkerThread(handle)
            self.workers[handle].setStreamHandleThreadClass(self.reqDataThreadCls)
            self.workers[handle].start()


class ProcessThreadPool(Pool):
    """
    TODO: Depreciated 进程线程模式当前不可用
    """

    def __init__(self, reqWorkerHandleCls, procs=2, threads_per_cpu=5):
        self.workers = {}
        self.process = {}
        for i in range(0, procs):
            # 初始化进程
            p = WorkerProcess(self.workers, reqWorkerHandleCls, str(i), threads_per_cpu)
            p.start()
            self.process[p.process_id] = p

    def get_thread(self, handle):
        return self.workers.get(handle)


class WorkerThread(threading.Thread):
    """
    Worker线程, 负责记录每次会话的上下文数据
    """

    # 继承父类threading.Thread
    def __init__(self, handle):
        threading.Thread.__init__(self)
        self.handle = handle  # handle标识，此处指的的是线程handle标识
        self.setDaemon(True)
        self.sid = ""  # 会话ID,由外部请求输入
        self.is_stopping = False
        self.in_q = queue.Queue()  # 定义输入工作线程队列
        self.out_q = queue.Queue()  # 异步callback获取结果时，此队列无用，仅同步取结果时有用
        self.is_idle = True  # 标明当前线程是否空闲，空闲则可以被获取
        self.params = {}  # 记录某次会话的用户功能参数

        self.StreamHandleThreadClass = StreamHandleThread  # 默认的流式处理线程类，实际使用时，请继承此类并自定义run方法

        self.callback_fn = None  # 该回调为，运行时，c++传入的会话callback，函数形式为 callback(response:Response , sid:string),
        # 用于回调数据返回

    def init_model(self, *args, **kwargs):
        raise NotImplementedError("Please implement this method...")

    @property
    def idle(self):
        return self.is_idle

    def setup_sid(self, sid):
        # 设置会话ID
        self.sid = sid

    def setup_params(self, params):
        # 设置会话参数
        self.params = params
        self.is_idle = False

    def setup_callback_fn(self, callback):
        # 设置会话callback，用于返回响应数据，函数形式为 callback(response:Response , sid:string),
        self.callback_fn = callback

    def reset(self):
        self.sid = ""
        self.params = {}
        with self.in_q.mutex:
            self.in_q.queue.clear()
        with self.out_q.mutex:
            self.out_q.queue.clear()
        self.is_idle = True

    def setStreamHandleThreadClass(self, cls):
        if issubclass(self.StreamHandleThreadClass, StreamHandleThread):
            print("handle thread set up ok...")
        self.StreamHandleThreadClass = cls

    def stop(self):
        self.is_stopping = True

    def run(self):
        pr = self.StreamHandleThreadClass(self, self.in_q, self.out_q)
        pr.start()
        pr.join()
