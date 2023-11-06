#!/bin/env python
# -*- coding: utf-8 -*-
"""
功能：日志模块等
版权信息：Copyright Huawei Technologies Co., Ltd. 2010-2022. All rights reserved.
"""
import logging
import os
import time
from logging import handlers

print_color = {"black": 30, "red": 31, "green": 32, "yellow": 33,
               "blue": 34, "purple": 35, "darkGreen": 36, "white": 37}

DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

log_level = DEBUG
if os.getenv('CI_BUILD_DEBUG') != 'True':
    log_level = ERROR

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
    def __init__(self, name, clevel=log_level, log_file_path=None):
        self.log_file_path = log_file_path
        self.name = name
        self.fmt = logging.Formatter("%(asctime)s - [%(levelname)s] : %(message)s")

        self.ch = logging.StreamHandler()
        self.ch.setLevel(clevel)
        self.ch.setFormatter(self.fmt)
        self.fh = None

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(DEBUG)
        self.logger.addHandler(self.ch)

    def set_log_conf(self, Flevel=log_level, only_file=False):
        if self.log_file_path:
            self.logger = logging.getLogger(self.name)
            if only_file:
                self.fh = logging.FileHandler(filename=self.log_file_path, encoding="utf-8")
            else:
                self.fh = handlers.TimedRotatingFileHandler(filename=self.log_file_path, when="D")
            self.fh.setLevel(Flevel)
            self.fh.setFormatter(self.fmt)
            self.logger.addHandler(self.fh)
            self.logger.removeHandler(self.ch)

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


logger = Logger("build", log_file_path="openEulerTransition_{0}.log".format(
    str(time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime()))))
# Unified log format，change WARNING to WARN
logging.addLevelName(WARN, 'WARN')
