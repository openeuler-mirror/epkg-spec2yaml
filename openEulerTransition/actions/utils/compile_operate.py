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
            if "--" in line:
                tmp_compile_flags = line.split("--")[1:]
                compile_flags = list(map(lambda x: "--" + x.rstrip(" \\", tmp_compile_flags)))
                for compile_flag in compile_flags:
                    if compile_flag.strip().startswith("--enable-") or compile_flag.strip().startswith("--disable-"):
                        if "=" in compile_flag:
                            param, value = compile_flag.split("=", 1)
                        else:
                            value = str("--enable-" in compile_flag).lower()
                            param = compile_flag.replace("--disable-", "--enable-").lstrip()
                        if "build." + key_name + ".Flags" not in params:
                            params["build." + key_name + ".Flags"] = {}
                        value = esc_value(value.rstrip("\\ "))
                        if condition:
                            suffix = " " + " ".join(condition)
                            params["build." + key_name + ".Flags"][param.strip("\\").strip() + suffix] = value
                        else:
                            params["build." + key_name + ".Flags"][param.strip("\\").strip()] = value
                    elif re.match("(--with-)|(--without-).*", compile_flag.strip()):
                        if "=" in compile_flag:
                            param, value = compile_flag.split("=", 1)
                            value = esc_value(value.strip("\\ "))
                        else:
                            param = compile_flag.strip("\\")
                            value = "yes"
                        if "build." + key_name + ".Flags" not in params:
                            params["build." + key_name + ".Flags"] = {}
                        if condition:
                            params["build." + key_name + ".Flags"][param.strip() + " " + " ".join(condition)] = value
                        else:
                            params["build." + key_name + ".Flags"][param.strip()] = value
                    elif re.match("(--build=)|(--target=)|(--host=)|(--prefix=)", compile_flag.strip()):
                        param, value = compile_flag.split("=", 1)
                        if "build." + key_name + ".Flags" not in params:
                            params["build." + key_name + ".Flags"] = {}
                        value = esc_value(value.strip("\\ "))
                        if condition:
                            params["build." + key_name + ".Flags"][param.strip() + " " + " ".join(condition)] = value
                        else:
                            params["build." + key_name + ".Flags"][param.strip()] = value
                    else:
                        configure_line += f"  {compile_flag} \\{os.linesep}"
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
    raise Exception("Error compile text, lack of configure command!")


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
