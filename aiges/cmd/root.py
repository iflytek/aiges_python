import argparse
from .create import *  # 初始化项目目录
from .config import *


def rootCmd():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest='create')

    # create project command
    create_parser = subparsers.add_parser('create')
    project_name = ""
    create_parser.add_argument('-n', '--name', help="初始化wrapper.py工程项目名称")
    create_parser.add_argument('-p', '--path', default="./", help="初始化工程位置")

    args = parser.parse_args()
    kwargs = vars(args)
    if kwargs.pop('create') == "create":
        create_project(args)
    else:
        print("not supported for this command")


def registerSubcommand(parser, name):
    subparsers = parser.add_subparsers(dest=name)
    named_parser = subparsers.add_parser(name)
    return subparsers
