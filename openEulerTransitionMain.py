#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import sys
from openEulerTransition.actions.config_parser.cli_args_parser import BuildArgsParser
from openEulerTransition.logs.log import logger
from openEulerTransition.actions.writer.yaml_writer import YamlWriter
from openEulerTransition.actions.utils.file_operate import check_spec_file


def main():
    (options, _) = BuildArgsParser('openEuler', sys.argv[1:]).parser()
    if not check_spec_file(options.yaml_file):
        logger.error("Cannot find valid spec file, file path is " + options.yaml_file)
        return
    yaml_writer = YamlWriter(options.yaml_file)
    yaml_writer.parse()


if __name__ == '__main__':
    main()
