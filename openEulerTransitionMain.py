#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import sys
from openEulerTransition.logs.log import logger
from openEulerTransition.actions.config_parser.cli_args_parser import BuildArgsParser
from openEulerTransition.actions.generation.spec_file import CreateSPEC
from openEulerTransition.actions.generation.yaml_file import CreateYAML


def main():
    (options, _) = BuildArgsParser('openEuler', sys.argv[1:]).parser()
    if options.yaml_file:
        log_path = options.log_path
        if not os.path.exists(log_path):
            log_path = ""
        if log_path != "":
            log_file_name = "openEulerTransition_{0}.log".format(
                str(time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())))
            logger.log_file_path = os.path.join(log_path, log_file_name)
            logger.change_path()
        if options.target_type == "spec":
            CreateSPEC(options.yaml_file, conf_path=options.conf_file, shell_path=options.shell_script,
                       python_path=options.python_script).transition()
        else:
            logger.error("There is no other target type to solve than spec")
    elif options.spec_file:
        CreateYAML(options.spec_file).transition()


if __name__ == '__main__':
    main()
