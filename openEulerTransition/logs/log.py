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
                 log_file_path=None, Flevel=log_level, only_file=False):
        fmt = logging.Formatter("%(asctime)s - [%(levelname)s] : %(message)s")

        ch = logging.StreamHandler()
        ch.setLevel(clevel)
        ch.setFormatter(fmt)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(DEBUG)
        self.logger.addHandler(ch)

        if log_file_path:
            self.logger = logging.getLogger(name)
            if only_file:
                fh = logging.FileHandler(filename=log_file_path, encoding="utf-8")
            else:
                fh = handlers.TimedRotatingFileHandler(filename=log_file_path, when="D")
            fh.setLevel(Flevel)
            fh.setFormatter(fmt)
            self.logger.addHandler(fh)
            self.logger.removeHandler(ch)

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


class LoggerSample:
    def __init__(self, name, clevel=log_level,
                 log_file_path=None, Flevel=log_level):
        self.logger_sample = Logger(name, log_file_path=log_file_path, clevel=clevel, Flevel=Flevel, only_file=True)
        self.logger_sample0 = Logger(name, log_file_path=None, clevel=ERROR, Flevel=ERROR)

    def debug(self, message):
        self.logger_sample.debug(message)

    def info(self, message):
        self.logger_sample.info(message)

    def warn(self, message):
        self.logger_sample.warn(message)

    def error(self, message):
        self.logger_sample0.error(message)


logger = LoggerSample("build", log_file_path="openEulerTransition_{0}.log".format(
    str(time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime()))))
# Unified log format，change WARNING to WARN
logging.addLevelName(WARN, 'WARN')
