import os
import re
from openEulerTransition.configure.spec_config import *


def find_file_exist(path, file_keywords="spec"):
    """
    查找spec文件是否存在
    :param path:
    :param file_keywords:
    :return:
    """
    folder_list = os.listdir(path)
    for folder in folder_list:
        folder_path = os.path.join(path, folder)
        if file_keywords in folder and os.path.isfile(folder_path):
            return folder_path
        if os.path.isdir(folder_path):
            status = find_file_exist(folder_path, file_keywords)
            if status:
                return status
    return ""


def get_project_path():
    """
    获得工程路径
    :return:
    """
    return os.getcwd()


def trans_shell2dict(shell_content):
    """
    把shell脚本的内容转换为字典
    :param shell_content:
    :return:
    """
    result = {}
    for _key in SHELL_KEYWORDS:
        lower_keywords = _key.lower()
        if re.search(lower_keywords + r".*\(\)\s*\{", shell_content) is not None:
            for n in range(len(re.findall(lower_keywords + r".*\(\)\s*\{", shell_content))):
                cutter1 = re.findall(lower_keywords + r".*\(\)\s*\{", shell_content)[n]
                sub_name = cutter1.split("()")[0].lstrip(lower_keywords + "_")
                temp_text = split_shell_content(cutter1, shell_content, lower_keywords)
                function_body = temp_text.strip(os.linesep).strip("}").strip(os.linesep)
                old_key = _key
                if sub_name != "":
                    _key += "_" + sub_name
                result[_key] = function_body
                _key = old_key
    return result


def split_shell_content(cutter0, text, keywords):
    """
    切割脚本内容
    :param cutter0:
    :param text:
    :param keywords：
    :return:
    """
    temp_text = cutter0.join(text.split(cutter0)[1:])
    temp_shell_keywords = SHELL_KEYWORDS.copy()
    temp_shell_keywords.remove(keywords)
    for key2 in temp_shell_keywords:
        if re.search(key2 + r".*\(\)\s*\{", temp_text) is not None:
            cutter2 = re.findall(key2 + r".*\(\)\s*\{", temp_text)[0]
            temp_text = temp_text.split(cutter2)[0]
    return temp_text


def update_shell_include(shell_content, inherited_shell_content):
    """
    更新shell继承的函数
    :param shell_content: shell内容
    :param inherited_shell_content: 被继承的shell内容
    :return:
    """
    if inherited_shell_content == "":
        return shell_content
    else:
        shell_content_dict = trans_shell2dict(shell_content)
        inherited_shell_content_dict = trans_shell2dict(inherited_shell_content)
        temp_dict = inherited_shell_content_dict.copy()
        for inherit_shell_key, inherit_shell_function in inherited_shell_content_dict.items():
            if inherit_shell_key in shell_content_dict.keys():
                temp_dict[inherit_shell_key] = shell_content_dict[inherit_shell_key]
                shell_content_dict.pop(inherit_shell_key)
        for inherited_shell_key, inherited_shell_function in shell_content_dict.items():
            temp_dict[inherited_shell_key] = inherited_shell_function
        result = "#!/bin/bash\n\n"
        for temp_key, temp_value in temp_dict.items():
            result += temp_key + "() {" + os.linesep
            result += temp_value + "\n}\n\n"
        return result


def change_yaml2sh_file(file):
    return file.replace(".yaml", ".sh").replace(".yml", ".sh")
