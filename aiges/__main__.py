import os
import sys
from typing import Any

from plumbum import cli, colors
from aiges.utils.log import log
from aiges.cmd.create import *  # 初始化项目目录
from aiges.cmd.package import *


class AigesCliManager(cli.Application):
    # 程序名称
    PROGNAME = "aiges sdk工具包" | colors.green
    VERSION = "1.0" | colors.blue
    DESCRIPTION = "kahn的CLI集合"
    USAGE = "aiges ai套件工具"

    def main(self):
        if not self.nested_command:  # will be ``None`` if no sub-command follows
            log.fatal("No subcommand given!")
            print()
            self.help()
            return 1
        elif len(self.nested_command[1]) < 2 and any(
                "create" in arg for arg in self.nested_command[1]
        ):
            log.error(
                "Subcommand  missing  required arguments! use 'create --help'"
            )
            return 1


@AigesCliManager.subcommand("create")  # type: ignore
class ManagerCreate(cli.Application):
    DESCRIPTION = "Aiges create project..."

    parent: AigesCliManager
    project_name: Any = cli.SwitchAttr(
        ["--name", "-n"],
        str,
        group="Create",
        help="初始化wrapper.py工程项目名称",
        default="wrapperDemo",
    )

    init_path: Any = cli.SwitchAttr(
        ["--path", "-p"],
        str,
        group="Create",
        help="初始化工程位置",
        default="./",
    )

    @cli.autoswitch(str, argname="模块名")
    def test(self, args):
        print("creating..%s" % str(args))

    def targeted(self):
        class Args:
            pass

        arg = Args()
        arg.name = self.project_name
        arg.path = self.init_path
        create_project(arg)

    def main(self):
        self.targeted()
        log.info("Done")


@AigesCliManager.subcommand("pack")  # type: ignore
class ManagerPack(cli.Application):
    DESCRIPTION = "Aiges pack wrapper directory..."

    parent: AigesCliManager
    location: Any = cli.SwitchAttr(
        ["--location", "-l"],
        str,
        group="Pack",
        help="工程目录路径",
        default="./",
    )

    output_path: Any = cli.SwitchAttr(
        ["--output", "-o"],
        str,
        group="Pack",
        help="输出压缩包路径",
        default="./",
    )

    @cli.autoswitch(str, argname="模块名")
    def test(self, args):
        print("creating..%s" % str(args))

    def targeted(self):
        class Args:
            pass

        arg = Args()
        arg.location = self.location
        arg.output = self.output_path
        pack(arg)

    def main(self):
        self.targeted()
        log.info("Done")


@AigesCliManager.subcommand("config")  # type: ignore
class ManagerConfig(cli.Application):
    DESCRIPTION = "Aiges Config Helper..."

    def main(self):
        # self.targeted()
        log.info("Done")


@ManagerConfig.subcommand("set")
class ConfigSet(ManagerConfig):
    parent: ManagerConfig

    def main(self, *args, **kwargs):
        log.info("setting config ...")
        print(args)
        print(kwargs)

@ManagerConfig.subcommand("get")
class ConfigGet(ManagerConfig):
    parent: ManagerConfig

    def main(self, *args, **kwargs):
        log.info("Getting config ...")
        print(args)

if __name__ == '__main__':
    AigesCliManager.run()
