import os
import re
from .data_operate import esc_value

class CompileParams(object):
    def __init__(self):
        self.cmake_params = {
            "phase.cmake": "",
            "build.cmakeFlags": {}
        }
        self.configure_params = {
            "build.configureFlags": {}
        }


def configure_params_split(script: str, configure_cmd_flag: str=""):
    """
    configure参数分解
    :param configure_cmd_flag:
    :param script:
    :return:
    """
    compile_params = CompileParams()
    params = compile_params.configure_params
    configure_line = ""
    configure_num = 0
    key_name = "configure"
    if "%configure" in script or "./configure" in script:
        line_list = script.split(os.linesep)
        start = False
        condition = []
        for line in line_list:
            if line.startswith("%configure") or line.lstrip(".").startswith("/configure"):
                start = True
                configure_line = line + os.linesep
                if configure_cmd_flag:
                    key_name = configure_cmd_flag
                elif configure_num > 1:
                    key_name = "configure_" + str(configure_num)
                configure_num += 1
                continue
            elif not start:
                continue
            if start and (line.strip().startswith("--enable-") or line.strip().startswith("--disable-")):
                if "=" in line:
                    param, value = line.split("=", 1)
                else:
                    value = str("--enable-" in line).lower()
                    param = line.replace("--disable-", "--enable-").lstrip()
                if "build." + key_name + ".Flags" not in params:
                    params["build." + key_name + ".Flags"] = {}
                value = esc_value(value.rstrip("\\ "))
                if condition:
                    suffix = " " + " ".join(condition)
                    params["build." + key_name + ".Flags"][param.strip("\\").strip() + suffix] = value
                else:
                    params["build." + key_name + ".Flags"][param.strip("\\").strip()] = value
            elif start and re.match("(--with-)|(--without-).*", line.strip()):
                if "=" in line:
                    param, value = line.split("=", 1)
                    value = esc_value(value.strip("\\ "))
                else:
                    param = line.strip("\\")
                    value = "yes"
                if "build." + key_name + ".Flags" not in params:
                    params["build." + key_name + ".Flags"] = {}
                if condition:
                    params["build." + key_name + ".Flags"][param.strip() + " " + " ".join(condition)] = value
                else:
                    params["build." + key_name + ".Flags"][param.strip()] = value
            elif start and re.match("(--build=)|(--target=)|(--host=)|(--prefix=)", line.strip()):
                param, value = line.split("=", 1)
                if "build." + key_name + ".Flags" not in params:
                    params["build." + key_name + ".Flags"] = {}
                value = esc_value(value.strip("\\ "))
                if condition:
                    params["build." + key_name + ".Flags"][param.strip() + " " + " ".join(condition)] = value
                else:
                    params["build." + key_name + ".Flags"][param.strip()] = value
            elif line.lstrip().startswith("%if"):
                configure_line += line + os.linesep
                condition.insert(0, line.strip())
            elif line == "%else" and condition:
                configure_line += line + os.linesep
                condition[0] = line + condition[0]
            elif line == "%endif" and condition:
                last_configure_line = configure_line.strip().split(os.linesep)[-1]
                if last_configure_line.strip().startswith("%if"):
                    configure_line = os.linesep.join(configure_line.strip().split(os.linesep)[:-1]) + os.linesep
                else:
                    configure_line += line + os.linesep
                condition.pop(0)
            elif line.endswith("\\"):
                configure_line += line + os.linesep
                continue
            else:
                configure_line += line + os.linesep
                start = False
        return params, configure_line


def cmake_params_split(script, cmake_cmd_flag):
    """
    cmake参数分解
    :param script:
    :param cmake_cmd_flag:
    :return:
    """
    compile_params = CompileParams()
    params = compile_params.cmake_params
    if "cmake" not in script:
        return params
    line_list = script.split(os.linesep)
    start = False
    condition = []
    cmake_cmd = ""
    for line in line_list:
        if line.startswith("%cmake"):
            start = True
        if not start:
            continue
        if line.lstrip().startswith("-D") and "=" in line:
            line = line.lstrip().replace("-D", "", 1).rstrip("\\")
            param, value = line.split("=", 1)
            if f"build.{cmake_cmd_flag}.Flags" not in params:
                params["build." + cmake_cmd_flag + ".Flags"] = {}
            value = esc_value(value.rstrip("\\ "))
            if condition:
                suffix = " " + " ".join(condition)
                params["build." + cmake_cmd_flag + ".Flags"][param + suffix] = value
            else:
                params["build." + cmake_cmd_flag + ".Flags"][param] = value
        elif line.lstrip().startswith("%if"):
            condition.insert(0, line.strip())
        elif line == "%else" and condition:
            condition[0] = line + condition[0]
        elif line == "%endif" and condition:
            condition.pop(0)
        else:
            cmake_cmd += line + os.linesep
            if not line.strip().endswith("\\"):
                start = False
    return params, cmake_cmd
