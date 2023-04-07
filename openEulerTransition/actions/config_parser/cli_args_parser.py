#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) Huawei Technologies Co., Ltd. 2016-2019. All rights reserved.
# Author: robell

""" 输入参数处理 """
import argparse
import optparse
import os

import openEulerTransition.configure.__version__ as version
from openEulerTransition.actions.utils.file_operate import Path
from openEulerTransition.logs.log import logger
from openEulerTransition.logs.error_info import EXCEPTION_CODE, EXCEPTION_RESPONSE

_SCRIPT_CWD = Path.cwd()


class ArgsParser:
    """ 输入参数的解析器, 提供了一些标准的参数, 也可以由外部定制"""

    def __init__(self, desc, _type='openEuler'):
        """
        :param desc: 用于描述命令名称
        :param _type:
        """
        usage = desc
        self._parser = optparse.OptionParser(usage, version=version.VERSION)
        self.type = _type

        cmd_args = {
            'conf': '_conf_file',
            'parse': '_parse_file',
            'shell': '_shell_script',
            'python': '_python_script',
            'target': '_target_type',
            'log': '_log_file',
        }

        if self.type == 'openEuler':
            for arg in cmd_args:
                func = getattr(self, cmd_args.get(arg))
                func()
        else:
            logger.error("%s\n            Reason:%s\n        EXCEPTION_RESPONSE:%s\n" % (
                EXCEPTION_CODE[600], 'Invalid Command Line', EXCEPTION_RESPONSE[1]))
            raise Exception(EXCEPTION_CODE[600], 'Invalid Command Line')

    def _parse_file(self):
        self._parser.add_option(
            '--parse', '-p',
            dest="spec_file",
            type="string", default=None,
            help='Spec file.')

    def _shell_script(self):
        self._parser.add_option(
            '--shell', '-s',
            dest="shell_script",
            type="string", default=None,
            help='Shell file.')

    def _python_script(self):
        self._parser.add_option(
            '--python', '-y',
            dest="python_script",
            type="string", default=None,
            help='Python file.')

    def _target_type(self):
        self._parser.add_option(
            '--target', '-t',
            dest="target_type",
            type="string", default="spec",
            help='File type.')

    def _conf_file(self):
        self._parser.add_option(
            '--conf', '-c',
            dest="conf_file",
            type="string", default=None,
            help='Conf file.'
        )

    def _log_file(self):
        self._parser.add_option(
            '--logpath', '-l',
            dest="log_path",
            type="string", default="",
            help='Log path.'
        )

    def parser(self):
        return self._parser

    def parse(self):
        try:
            args = self._parser.parse_args()
            if vars(args).get('root_path') is not None:
                args.root_path = Path.abs(args.root_path)
            return args
        except Exception as e:
            raise Exception(EXCEPTION_CODE[602], e)


class ArgsAction:
    """ arg_parser 的通用 action """

    @staticmethod
    def error_prefix(script_name, option_string):
        return '{}: error: argument {}:'.format(script_name,
                                                '/'.join(option_string))

    @staticmethod
    def path_existence_checker(root_path, paths, option_string):
        """ 检查路径是否存在 """
        for path in paths:
            if not os.path.exists(Path.join(root_path, path)):
                return Exception(('{} \'{}\' isn\'t existed.'+os.linesep).format(
                    ArgsAction.error_prefix('args', option_string), path))

    @staticmethod
    def root_path_checker():
        """ 只检查目录是否存在 """

        class RootPathChecker(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                path = values
                # if baseline is valid，and the root_path is root path of the git repo.
                # by checking .git son-folder is existed, to judge validity of the root_path.
                if vars(namespace).get('baseline') is not None:
                    path = Path.join(path, '.git')
                ArgsAction.path_existence_checker(_SCRIPT_CWD, [path],
                                                  self.option_strings)
                setattr(namespace, self.dest, values)

        return RootPathChecker

    @staticmethod
    def filepaths_checker():
        """检查参数 filepaths 的有效性
        filepaths 是基于 root_path 的多个相对路径
        """

        class FilePathsChecker(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                if vars(namespace).get('root_path') is not None:
                    ArgsAction.path_existence_checker(namespace.root_path,
                                                      values,
                                                      self.option_strings)
                setattr(namespace, self.dest, values)

        return FilePathsChecker

    @staticmethod
    def path_base_root_path_existence_checker():
        """检查基于 root_path 的单个相对路径的有效性"""

        class PathBaseRootPathExistenceChecker(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                ArgsAction.path_existence_checker(namespace.root_path,
                                                  [values],
                                                  self.option_strings)
                setattr(namespace, self.dest, values)

        return PathBaseRootPathExistenceChecker

    @staticmethod
    def path_base_cwd_existence_checker():
        """检查基于当前工作路径的单个相对路径的有效性"""

        class PathBaseCWDExistenceChecker(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                ArgsAction.path_existence_checker(_SCRIPT_CWD, [values],
                                                  self.option_strings)
                setattr(namespace, self.dest, values)

        return PathBaseCWDExistenceChecker


class BuildArgsParser:

    def __init__(self, system_type, args):
        self._build_arg = ArgsParser('openEuler - setup tool for openEulerTransition project', system_type)
        self._parser = self._build_arg.parser().parse_args(args)
        self._parser = self._build_arg.parser().parse_args(args)

    def parser(self):
        return self._parser
