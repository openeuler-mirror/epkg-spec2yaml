import os
import re
from .data_operate import esc_value

class CompileParams(object):
    def __init__(self):
        self.cmake_params = {
            "phase.cmake": "",
            "build.cmake.flags": {}
        }
        self.configure_params = {
            "build.configure.flags": {}
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
            if "#" in line:
                line = line.split("#")[0]
            if "--" in line:
                if re.search("( -with-| -without-| -enable-| -disable-)", line):
                    error_keywords_list = re.findall("( -with-| -without-| -enable-| -disable-)\S+", line)
                    for error_keywords in error_keywords_list:
                        line = line.replace(error_keywords, error_keywords.replace("-", "--", 1))
                tmp_compile_flags = line.split("--")[1:]
                compile_flags = list(map(lambda x: "--" + x.rstrip(" \\"), tmp_compile_flags))
                for compile_flag in compile_flags:
                    if compile_flag.strip().endswith("<<EOF"):
                        configure_line += compile_flag
                    elif compile_flag.strip().startswith("--enable-") or compile_flag.strip().startswith("--disable-"):
                        if "=" in compile_flag:
                            param, value = compile_flag.split("=", 1)
                        else:
                            value = str("--enable-" in compile_flag).lower()
                            param = compile_flag.replace("--disable-", "--enable-").lstrip()
                        if "build." + key_name + ".flags" not in params:
                            params["build." + key_name + ".flags"] = {}
                        value = esc_value(value.rstrip("\\ "))
                        if condition:
                            suffix = " " + " ".join(condition)
                            params["build." + key_name + ".flags"][param.strip("\\").strip() + suffix] = value
                        else:
                            params["build." + key_name + ".flags"][param.strip("\\").strip()] = value
                    elif re.match("(--with-)|(--without-).*", compile_flag.strip()):
                        if "=" in compile_flag:
                            param, value = compile_flag.split("=", 1)
                            value = esc_value(value.rstrip("\\ "))
                        else:
                            param = compile_flag.strip("\\")
                            value = "true"
                        if "--without-" in param:
                            param = param.replace("--without-", "--with-")
                            value = reverse_bool_value(value)
                        if "build." + key_name + ".flags" not in params:
                            params["build." + key_name + ".flags"] = {}
                        if condition:
                            params["build." + key_name + ".flags"][param.strip() + " " + " ".join(condition)] = value
                        else:
                            params["build." + key_name + ".flags"][param.strip()] = value
                    elif re.match("(--build=)|(--target=)|(--host=)|(--prefix=)", compile_flag.strip()):
                        param, value = compile_flag.split("=", 1)
                        if "build." + key_name + ".flags" not in params:
                            params["build." + key_name + ".flags"] = {}
                        value = esc_value(value.rstrip("\\ "))
                        if condition:
                            params["build." + key_name + ".flags"][param.strip() + " " + " ".join(condition)] = value
                        else:
                            params["build." + key_name + ".flags"][param.strip()] = value
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
    return params, script


def add_make_flag(script):
    """
    make叠加%{?build_make_flags}
    :param script:
    :return:
    """
    if "cmake" in script:
        return script
    line_list = script.split(os.linesep)
    make_dir = ""
    make_num = 0
    for line_index, line in enumerate(line_list):
        if line.startswith("pushd "):
            make_dir = re.findall("\w+", line)[-1]
            continue
        if line == "popd" and make_dir != "":
            make_dir = ""
            continue
        if line.startswith("make ") or line.startswith("%make_build "):
            if make_dir == "" and make_num == 0:
                make_num += 1
                make_func_name = ""
            elif make_dir == "" and make_num != 0:
                make_func_name = "_" + str(make_num)
            else:
                make_func_name = "_" + make_dir
            if line.endswith("\\"):
                line_list[line_index] = line.rstrip("\\").rtrip() + " %{?build_make" + make_func_name + "_flags} \\"
            else:
                line += " %{?build_make" + make_func_name + "_flags}"
                line_list[line_index] = line
    return os.linesep.join(line_list)


def reverse_bool_value(word):
    """yes=>no, true=>false, ON=>OFF"""
    if isinstance(word, bool):
        return not word
    relation_ship = {
        "yes": "no",
        "no": "yes",
        "false": "true",
        "true": "false",
        "ON": "OFF",
        "OFF": "ON"
    }
    return relation_ship.get(word, word)
