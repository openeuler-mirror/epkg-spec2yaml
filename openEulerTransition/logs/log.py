#!/bin/env python
# -*- coding: utf-8 -*-
"""
功能：日志模块等
版权信息：Copyright Huawei Technologies Co., Ltd. 2010-2022. All rights reserved.
"""
import logging
import os

print_color = {"black": 30, "red": 31, "green": 32, "yellow": 33,
               "blue": 34, "purple": 35, "darkGreen": 36, "white": 37}

DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

log_level = DEBUG

if os.getenv('CI_BUILD_DEBUG') != 'True':
    log_level = INFO


class LogInfo:
    def __init__(self, ):
        pass

    @staticmethod
    def header(component=None, action=None, stage=None, func=None, file_line=None):
        log_info = "====>[component: {}]--[action: {}]--[stage: {}]<====->func: {}--file_line: {}".format(
            component, action, stage, func, file_line
        )
        return log_info


class Logger(object):
    def __init__(self, name, clevel=log_level,
                 log_file_path=None, Flevel=log_level):
        fmt = logging.Formatter("%(asctime)s - [%(levelname)s] : %(message)s")

        ch = logging.StreamHandler()
        ch.setLevel(clevel)
        ch.setFormatter(fmt)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(DEBUG)
        self.logger.addHandler(ch)

        if log_file_path:
            fh = logging.FileHandler(log_file_path)
            fh.setLevel(Flevel)
            fh.setFormatter(fmt)
            self.logger.addHandler(fh)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warn(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


logger = Logger("build")
# Unified log format，change WARNING to WARN
logging.addLevelName(WARN, 'WARN')
