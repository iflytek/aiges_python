import argparse
from .create import *  # 初始化项目目录
from .config import *
from .package import *

import pkg_resources


def rootCmd():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='action')

    # create project command
    create_parser = subparsers.add_parser('create')
    project_name = ""
    create_parser.add_argument('-n', '--name', help="初始化wrapper.py工程项目名称")
    create_parser.add_argument('-p', '--path', default="./", help="初始化工程位置")

    # version
    version = subparsers.add_parser('version')

    # package wrapper
    pack_parser = subparsers.add_parser('pack')
    pack_parser.add_argument('-l', '--location', help="工程目录路径", default="./")
    pack_parser.add_argument('-o', '--output', help="输出压缩路径", default="./")

    args = parser.parse_args()
    kwargs = vars(args)
    action = kwargs.pop('action')
    if action == "create":
        create_project(args)
    elif action == "version":
        print_version()
    elif action == "pack":
        pack(args)

    else:
        print("not supported for this command")


def registerSubcommand(parser, name):
    subparsers = parser.add_subparsers(dest=name)
    named_parser = subparsers.add_parser(name)
    return subparsers


def print_version():
    print(repr(pkg_resources.get_distribution('aiges')))
