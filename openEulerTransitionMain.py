#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import os
import sys
import time
from openEulerTransition.actions.config_parser.cli_args_parser import BuildArgsParser
from openEulerTransition.logs.log import logger
from openEulerTransition.actions.writer.yaml_writer import YamlWriter
from openEulerTransition.actions.utils.file_operate import check_spec_file


def main():
    (options, _) = BuildArgsParser('openEuler', sys.argv[1:]).parser()
    log_path = options.log_path
    if not os.path.exists(log_path):
        log_path = ""
    if log_path != "":
        log_file_name = "openEulerTransition_{0}.log".format(
            str(time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())))
        logger.log_file_path = os.path.join(log_path, log_file_name)
        logger.change_path()
    if not check_spec_file(options.spec_file):
        logger.error("Cannot find valid spec file, file path is " + options.spec_file)
        return
    yaml_writer = YamlWriter(options.spec_file)
    yaml_writer.parse()


if __name__ == '__main__':
    main()
