#!/usr/bin/env python
# coding:utf-8
"""
@author: nivic ybyang7
@license: Apache Licence
@file: package.py
@time: 2022/09/08
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
import tarfile
import os
from aiges.utils.log import log


def reset(tarinfo):
    tarinfo.uid = tarinfo.gid = 0
    tarinfo.uname = tarinfo.gname = "root"
    return tarinfo


def pack(args):
    location = args.location
    files = checkget_project(location)

    output_dir = args.output
    make_tarfile("{}.tar.gz".format("pywrapper"), files)


def checkget_project(path):
    if not os.path.exists(path):
        raise FileNotFoundError

    basicfiles = ["wrapper.py", "requirements.txt", "Readme.md"]
    must_exists = False
    # list to store files name
    files = []
    filepaths = []
    for (dir_path, dir_names, file_names) in os.walk(path):
        for fi in file_names:
            filepaths.append(os.path.join(dir_path, fi))
        files.extend(file_names)
    for fi in basicfiles:
        if fi == "wrapper.py":
            must_exists = True
        else:
            must_exists = False

        if fi not in files and must_exists:
            raise FileNotFoundError("Please execute pack in the wrapper.py dir.:  %s" % fi)
        elif not must_exists:
            log.warn("We suggest you should provide file: %s" % fi)
    return filepaths


def make_tarfile(output_filename, files):
    with tarfile.open(output_filename, "w:gz") as tar:
        for fi in files:
            tar.add(fi, arcname=os.path.basename(fi))
            log.info("Archiving... {}".format(fi))
        log.info("Archived...{}".format(output_filename))


if __name__ == '__main__':
    make_tarfile("aiges.tar.gz", "demo")
