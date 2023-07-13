import re
from openEulerTransition.configure.spec_config import *
from openEulerTransition.configure.yaml_config import *
from openEulerTransition.configure.macros_config import *
from openEulerTransition.logs.log import logger


class LuaFile(object):
    CREATED_LUA = {"Phase": False, "runtimePhase": False}


def lower_first_word(words: str):
    if words == "Patches":
        return "patchset"
    if words == "Sources":
        return "source"
    if words == "Macros":
        return "rpmMacros"
    if words.upper() == "URL":
        return "homepage"
    if len(words) <= 1:
        return words.lower()
    else:
        return words[0].lower() + words[1:]


def clear_sub_extra_judge(sub_name, default_dict, target_items=None):
    """
    清理子包多余的判断语句
    :param sub_name:
    :param default_dict
    :param target_items:
    :return:
    """
    if target_items is None:
        target_items = default_dict
    if "%if" in sub_name:
        judge_words = sub_name.replace(sub_name.split("%if")[0], "")
        judge_words_values = judge_words.split("%if")
        judge_words_list = map(lambda x: ("%if" + x).strip(), judge_words_values)
        judge_words_values.remove("")
        judge_count = len(judge_words_values)
        for sub_item_key, sub_item_value in target_items["SubPackages"][sub_name].items():
            if type(sub_item_value) is str:
                if judge_words in sub_item_value:
                    target_items["SubPackages"][sub_name][sub_item_key] = sub_item_value.replace(judge_words, "")
            elif type(sub_item_value) is list and sub_item_value:
                if sub_item_key == "FilesJudgement" and judge_count:
                    if judge_count == 1 and judge_words in sub_item_value:
                        sub_item_value.remove(judge_words)
                    else:
                        for single_judge_words in judge_words_list:
                            if single_judge_words in sub_item_value:
                                sub_item_value.remove(single_judge_words)
                for index1, member_item_value in enumerate(sub_item_value):
                    if judge_words in member_item_value:
                        target_items["SubPackages"][sub_name][sub_item_key][index1] = member_item_value.replace(judge_words, "")
    return target_items


def add_quotation_from_member(keywords, default_items, sub_name=None, target_items=None):
    """
    list类型的子项统一增加引号
    :param keywords:
    :param default_items
    :param sub_name:
    :param target_items:
    :return:
    """
    if target_items is None:
        target_items = default_items
    if sub_name is not None:
        if keywords in target_items["SubPackages"][sub_name].keys() and type(
                target_items["SubPackages"][sub_name][keywords]) == list:
            for index0, son_item in enumerate(target_items["SubPackages"][sub_name][keywords]):
                if type(son_item) != str:
                    continue
                extra_escape = "\\" if son_item.endswith("\\") else ""
                if "\"" in son_item and "\'" in son_item:
                    continue
                elif "\"" not in son_item:
                    target_items["SubPackages"][sub_name][keywords][index0] = "\"" + son_item + extra_escape + "\""
                elif "\'" not in son_item:
                    target_items["SubPackages"][sub_name][keywords][index0] = "\'" + son_item + extra_escape + "\'"
    else:
        if keywords in target_items.keys() and type(target_items[keywords]) == list:
            for index1, son_item in enumerate(target_items[keywords]):
                if type(son_item) != str:
                    continue
                extra_escape = "\\" if son_item.endswith("\\") else ""
                if "\"" in son_item and "\'" in son_item:
                    continue
                elif "\"" not in son_item:
                    target_items[keywords][index1] = "\"" + son_item + extra_escape + "\""
                elif "\'" not in son_item:
                    target_items[keywords][index1] = "\'" + son_item + extra_escape + "\'"
    return target_items


def remove_marginals_quotes(_line):
    """
    去掉边缘的引号
    :param _line:
    :return:
    """
    if _line.startswith("\"") and _line.endswith("\""):
        _line = _line[1:-1]
    elif _line.startswith("\'") and _line.endswith("\'"):
        _line = _line[1:-1]
    return _line


def resolve_inner_quotes(_line):
    """
    处理字符串内部的引号
    :param _line:
    :return:
    """
    # _line = remove_marginals_quotes(_line)
    if "\"" in _line and "\\\"" not in _line:
        _line = _line.replace("\"", "\\\"")
    return _line


def update_keywords(keywords, value=""):
    """
    更新关键字（只有sources和patches）
    :param keywords:
    :param value:
    :return:
    """
    if keywords.lower().startswith("source"):
        keywords = 'Sources'
    elif keywords.lower().startswith("patch"):
        num = keywords[5:]
        if num.startswith("0") and len(num) > 1:
            num = re.sub("^0*", "", num)
            keywords = keywords[0:5] + num
        keywords = 'Patches'
    return keywords


def find_quotes_from_words(words):
    """
    从字段中找出引号，做特殊处理，是yaml不会识别引号为特殊字符串
    :param words:
    :return:
    """
    value = words
    if "'" in words.strip("'") and '"' not in words.strip("'"):
        value = '"' + words + '"'
    elif '"' in words.strip('"') and "'" not in words.strip('"'):
        value = "'" + words + "'"
    return value


def parse_case_spell(word, source_items):
    """
    解析关键字的拼写问题，目的是兼容spec大小写不敏感的特性
    :param word:关键字
    :param source_items:
    :return:
    """
    if not word:
        return False, word
    temp_keys_list = []
    for _key in source_items.keys():
        temp_keys_list.append(_key)
    for _key1 in SINGLES:
        temp_keys_list.append(_key1)
    for _key2 in REQUIRES:
        temp_keys_list.append(_key2)
    for _key3 in ORDER_ENTRIES:
        temp_keys_list.append(_key3)
    for _key4 in SEVERAL:
        temp_keys_list.append(_key4)
    for temp_key in temp_keys_list:
        if word.lower() == temp_key.lower():
            word = temp_key
            return True, word
    return False, word


def add_special_keywords(_items, line, keyword):
    if keyword.lower() in line:
        line = line.replace("%" + keyword.lower(), "").strip()
        if keyword in _items:
            _items[keyword].append(line)
        else:
            _items[keyword] = [line]


def translate_keys(_dict):
    """
    将AutoReq/AutoProv的值转换成布尔类型
    :param _dict: 传入的字典
    :return:
    """
    # translate AutoReq/AutoProv to spectacle boolean keys
    autoreq = autoprov = None
    if 'AutoReq' in _dict:
        autoreq = _dict['AutoReq']
        del _dict['AutoReq']
    if 'AutoProv' in _dict:
        autoprov = _dict['AutoProv']
        del _dict['AutoProv']
    if 'AutoReqProv' in _dict:
        if _dict['AutoReqProv'] == '0':
            autoreq = autoprov = '0'
        del _dict['AutoReqProv']

    if autoreq == '0' and autoprov == '0':
        _dict['NoAutoReqProv'] = 'yes'
    elif autoreq == '0':
        _dict['NoAutoReq'] = 'yes'
    elif autoprov == '0':
        _dict['NoAutoProv'] = 'yes'


def remove_duplicate(_dict):
    """
    配置去重
    :param _dict:字典类型输入
    :return:
    """
    dup = '--disable-static'
    if 'ConfigOptions' in _dict and dup in _dict['ConfigOptions']:
        _dict['ConfigOptions'].remove(dup)
        if not _dict['ConfigOptions']:
            del _dict['ConfigOptions']
    if 'FilesJudgement' in _dict and len(_dict['FilesJudgement']) == 0:
        del _dict['FilesJudgement']
    if "Description" in _dict.keys() and _dict["Description"].startswith("`"):
        _dict["Description"] = "_" + _dict["Description"]

    # check duplicate requires for base package
    if "SubPackages" in _dict:
        if 'Epoch' in _dict:
            autodep = "%{name} = %{epoch}:%{version}-%{release}"
        else:
            autodep = "%{name} = %{version}-%{release}"

        for sp in _dict["SubPackages"]:
            if 'Requires' in sp and autodep in sp['Requires']:
                sp['Requires'].remove(autodep)
                if not sp['Requires']:
                    del sp['Requires']
            if 'FilesJudgement' in sp and len(sp['FilesJudgement']) == 0:
                del sp['FilesJudgement']
            if "Description" in sp.keys() and sp["Description"].startswith("`"):
                sp["Description"] = "_" + sp["Description"]

    # check duplicate '%defattr' for files list
    if 'extra' in _dict and 'Files' in _dict['extra']:
        try:
            _dict['extra']['Files'].remove('%defattr(-,root,root,-)')
        except ValueError:
            pass


def esc_value(val):
    """
    加载%标识符
    :param val: 字段
    :return:
    """
    # ESC for leading '%', for yaml syntax
    if val.startswith('%') or \
            val.startswith('*') or \
            ": " in val or \
            val.endswith(':'):
        quote_char = ""
        extra_escape = "\\" if val.endswith("\\") else ""
        if not ((val.startswith("\"") and val.endswith("\"")) or (val.startswith("\'") and val.endswith("\'"))):
            if '\"' in val and "\'" not in val:
                quote_char = '\''
            elif '\"' not in val:
                quote_char = '\"'
        return quote_char + val + extra_escape + quote_char
    elif "\t" in val:
        return val.replace("\t", "  ")
    else:
        return val


def add_tab_in_lines(lines, tab=" "*4, tab_left=False):
    """

    :param lines:
    :param tab:
    :param tab_left:
    :return:
    """
    result = ""
    line_list = lines.split(os.linesep)
    if tab_left:
        for line in line_list:
            result += line.replace(tab_left, "", 1) + os.linesep
    else:
        for line in line_list:
            result += tab + line + os.linesep
    return result


def add_string_to_dict(dict1, this_key, line, turn_line=True):
    """
    向字典中加字符串
    :param dict1:
    :param this_key:
    :param line:
    :param turn_line:
    :return:
    """
    if this_key in ["include", "description", "package", "Recommends", "ExclusiveArch"]:
        return dict1
    if this_key in SINGLES + SEVERAL:
        return dict1
    if True:
        suffix = os.linesep if turn_line else ""
        if this_key in dict1:
            dict1[this_key] += line + suffix
        else:
            dict1[this_key] = line + suffix
    return dict1


def divide_rpm_global(macros_text, rpm_global_text):
    line_list = macros_text.split(os.linesep)
    if_flag = 0
    else_flag = 0
    target_list = line_list.copy()
    remove_list = []
    for i, line in enumerate(line_list):
        if line.endswith("%{expand:"):
            continue
        if re.match("%global\s+\S+ [\s\S]+", line) is not None:
            if line.endswith("\\"):
                continue
            if if_flag == else_flag == 0:
                line_list = line.split()
                if len(line_list) == 3:
                    global_key = line_list[1]
                    global_value = line_list[2]
                elif len(line_list) > 3:
                    global_key = line_list[1]
                    global_value = " ".join(line_list[2:])
                else:
                    continue
                global_value = resolve_inner_quotes(global_value)
                rpm_global_text[global_key] = "\"" + global_value + "\""
                remove_list.append(i)
        if line.startswith("%if"):
            if_flag += 1
        elif line.startswith("%else"):
            else_flag += 1
        elif line.strip() == "%endif":
            if_flag -= 1
            else_flag -= 1 if else_flag else 0
    remove_list.reverse()
    for remove_index in remove_list:
        target_list.pop(remove_index)
    macros_text = os.linesep.join(target_list)
    return macros_text, rpm_global_text


def get_reverse_judgement(judgement):
    if "%ifarch" in judgement:
        return judgement.replace("%ifarch", "%ifnarch")
    elif "%ifnarch" in judgement:
        return judgement.replace("%ifnarch", "%ifarch")
    elif "%ifos" in judgement:
        return judgement.replace("%ifos", "%ifnos")
    elif "%ifnos" in judgement:
        return judgement.replace("%ifnos", "%ifos")
    elif "%if %{with " in judgement:
        return judgement.replace("%if %{with ", "%if %{without ")
    elif "%if %{without " in judgement:
        return judgement.replace("%if %{without ", "%if %{with ")
    elif "%if !" in judgement:
        return judgement.replace("%if !", "%if ")
    else:
        return judgement.replace("%if ", "%if ! ")


def resolve_else_judgement(line: str):
    if "%else %if ! " in line:
        line = line.replace("%else %if ! ", "%if ")
    elif "%else %if !" in line:
        line = line.replace("%else %if !", "%if")
    if "%else %ifn" in line:
        line = line.replace("%else %ifn", "%if")
    if "%else %if " in line:
        line = line.replace("%else %if ", "%if ! ")
    elif "%else %ifarch" in line:
        line = line.replace("%else %ifarch", "%ifnarch")
    elif "%else %ifos" in line:
        line = line.replace("%else %ifos", "%ifnos")
    if "%else %if" in line:
        line = line.replace("%else %if", "%ifn")
    return line


def divide_out_configure(content: str):
    """
    分出configure字段
    :param content:
    :return:
    """
    configure_items = {}
    configure = ""
    build = ""
    configure_cmd = False
    line_list = content.split(os.linesep)
    configure_num = 0
    configure_cmd_multiline = True
    configure_cmd_flags = ""
    compile_type = ""
    for num, line in enumerate(line_list):
        if line.startswith("#") or line.startswith("%global") or line.startswith("%define"):
            if configure_cmd:
                configure += line + os.linesep
            else:
                build += line + os.linesep
            continue
        if line.startswith("pushd"):
            str_list = re.findall("\w+", line)
            configure_cmd_flags = str_list[-1]
        elif line == "popd":
            configure_cmd_flags = ""
        if configure_cmd:
            if line.strip().startswith("%if") or line.strip().startswith("%else") or line.strip().startswith("%endif"):
                configure += line + os.linesep
            elif line.endswith("\\"):
                if not configure_cmd_multiline:
                    configure_cmd_multiline = True
                configure += line + os.linesep
            else:
                if configure_cmd_multiline:
                    configure += line + os.linesep
                else:
                    build += line + os.linesep
                if configure_cmd and configure.strip() != "":
                    if configure_cmd_flags:
                        key_name = f"{compile_type}_{configure_cmd_flags}"
                    elif configure_num > 1:
                        key_name = f"{compile_type}_{str(configure_num - 1)}"
                    else:
                        key_name = compile_type
                    configure_items[key_name] = configure.strip()
                    configure = ""
                configure_cmd = False
                continue
        if line.lstrip(".").startswith("/configure") or line.startswith("%configure"):
            if line.lstrip(".").startswith("/configure"):
                configure += "%{?add_configure_flags} \\" + os.linesep
            compile_type = "configure"
            if not configure_cmd:
                if configure_cmd_flags:
                    build += "configure_" + configure_cmd_flags + os.linesep
                else:
                    if configure_num == 0:
                        build += "configure" + os.linesep
                    else:
                        build += "configure_" + str(configure_num) + os.linesep
                configure_num += 1
            configure_cmd = True
            configure += line + os.linesep
        elif line.startswith("%cmake"):
            compile_type = "cmake"
            if not configure_cmd:
                if configure_cmd_flags:
                    build += "cmake_" + configure_cmd_flags + os.linesep
                else:
                    if configure_num == 0:
                        build += "cmake" + os.linesep
                    else:
                        build += "cmake_" + str(configure_num) + os.linesep
                configure_num += 1
            configure_cmd = True
            configure += line + os.linesep
        if not configure_cmd:
            build += line + os.linesep
        if compile_type and compile_type in line and not line.endswith("\\"):
            configure_cmd_multiline = False
    if configure != "" and configure_items == {}:
        configure_items[compile_type] = configure.strip()
    return configure_items, build.strip()


def get_if_with_parts(line):
    with_parts = re.findall("%if %\{with \w+}", line)
    without_parts = re.findall("%if %\{without \w+}", line)
    with_parts = list(map(lambda x: x.replace("%if %{with", "").replace("}", "").strip(), with_parts))
    without_parts = list(map(lambda x: x.replace("%if %{without", "").replace("}", "").strip(), without_parts))
    return with_parts, without_parts


def calculate_brackets(line):
    brackets_left_list = re.findall("(\{)|(\()", line)
    brackets_right_list = re.findall("(})|(\))", line)
    left_character = re.findall("\\\\\\(", line)
    left_count = len(brackets_left_list) - len(left_character)
    right_character = re.findall("\\\\\\)", line)
    right_count = len(brackets_right_list) - len(right_character)
    return left_count, right_count


def add_context(name, text, obj, file_obj: LuaFile):
    first_line = text.split(os.linesep)[0]
    target_first = "--" + RPM_MACRO_PARAM_COMMENT + " " + first_line if "<lua>" in first_line else "#" + RPM_MACRO_PARAM_COMMENT + " " + first_line
    temp_list = first_line.split()
    if len(temp_list) > 1:
        if name not in MAIN_SHELL_KEYWORDS and not re.match("configure|cmake.*", name) and (temp_list[0].startswith(
                "-") or temp_list[1].startswith("-")):
            text = text.replace(first_line, target_first, 1)
    if "<lua>" in first_line:
        file_name = os.path.splitext(obj.name)[0]
        mode = "a+" if file_obj.CREATED_LUA[file_name] else "w+"
        file_obj.CREATED_LUA[file_name] = True
        with open(obj.name.replace(".sh", ".lua"), mode) as f:
            if mode == "w+":
                f.write("#!/usr/bin/env lua" + os.linesep*2)
            text = add_tab_in_lines(text)
            f.write("function " + name + "()" + os.linesep + text + "end" + os.linesep*2)
            f.close()
        return file_obj
    text = add_tab_in_lines(text)
    obj.write(name + "() {" + os.linesep + text + "}" + os.linesep*2)
    return file_obj


def inline_to_mainline(inline: list, mainline: list):
    if len(inline) != 0 and len(mainline) == 0:
        return mainline, inline
    return inline, mainline


def add_input_to_files(input_value, items):
    if "files" in items and isinstance(items["files"], str):
        items["files"] += input_value + os.linesep
    else:
        items["files"] = input_value + os.linesep
    return items


def get_line_suffix(if_cond_part, else_cond_part, else_status):
    if len(if_cond_part) > 0 and len(else_cond_part) == 0 and not else_status:
        _line_suffix = " " + " ".join(if_cond_part)
    elif len(if_cond_part) > 0 and len(else_cond_part) > 0 and else_status:
        temp_if_cond_part = if_cond_part.copy()
        temp_else_cond_part = else_cond_part.copy()
        _line_suffix = ""
        while len(temp_else_cond_part) > 0 or len(temp_if_cond_part) > 0:
            if len(temp_if_cond_part) > len(temp_else_cond_part):
                if len(temp_if_cond_part) > 0:
                    _line_suffix += " " + temp_if_cond_part[-1]
                    temp_if_cond_part.pop()
                if len(temp_else_cond_part) > 0:
                    _line_suffix += " " + temp_else_cond_part[-1]
                    temp_else_cond_part.pop()
            else:
                if len(temp_else_cond_part) > 0:
                    _line_suffix += " " + temp_else_cond_part[-1]
                    temp_else_cond_part.pop()
                if len(temp_if_cond_part) > 0:
                    _line_suffix += " " + temp_if_cond_part[-1]
                    temp_if_cond_part.pop()
    else:
        _line_suffix = ""
    return _line_suffix


def parse_files_input(origin_items, target_items, **kwargs):
    line = kwargs.get("line")
    if_lines = kwargs.get("if_lines") if "if_lines" in kwargs else []
    else_lines = kwargs.get("else_lines") if "else_lines" in kwargs else []
    else_status = kwargs.get("else_status") if "else_status" in kwargs else False
    opt = line.split()
    if len(opt) > 1:
        files_input = opt[1:]
        files_input_value = ""
        while '-f' in files_input:
            this_files_input = files_input[files_input.index('-f') + 1].strip()
            files_input_value += " -f " + this_files_input
            files_input.remove("-f")
            opt.remove("-f")
            if this_files_input != "":
                files_input.remove(this_files_input)
                opt.remove(this_files_input)
        if len(opt) == 1 and opt[0] == "%files":
            if origin_items != target_items and "files" not in origin_items:
                items = origin_items
                items["files"] = line + os.linesep
        if files_input_value != "":
            target_items = add_input_to_files("%files " + files_input_value + get_line_suffix(if_lines, else_lines, else_status),
                                              target_items)
    elif len(opt) == 1 and opt[0] == "%files":
        if origin_items != target_items:
            target_items = origin_items
        if "files" not in target_items:
            target_items["files"] = ""
    return target_items


def strip_files_startswith(text):
    param_text = ""
    file_lines = text.strip().split(os.linesep)
    content_line_index = 0
    for line_num, file_line in enumerate(file_lines):
        if re.match("%files \S+ -f", file_line) is not None:
            content_line_index += 1
        elif file_line.startswith("%files"):
            target_line = remove_package_name(file_line)
            if "-f" in target_line:
                content_line_index += 1
        else:
            break
    if content_line_index < len(file_lines):
        if file_lines[content_line_index].startswith("%files"):
            text = os.linesep.join(file_lines[content_line_index + 1:])
        else:
            text = os.linesep.join(file_lines[content_line_index:])
    else:
        text = ""
    if content_line_index > 0:
        for line in file_lines[0:content_line_index]:
            if re.match("%files \S+ -f", line) is not None:
                line = " ".join(line.split()[2:])
                param_text += line + os.linesep
            if line.startswith("%files"):
                target_line = remove_package_name(line)
                if target_line != "%files":
                    target_line = target_line.replace("%files", "", 1)
                    param_text += target_line + os.linesep
    return text, param_text


def divide_several_requires(origin_list):
    target_list = []
    for line in origin_list:
        if "%if" in line:
            target_list.append(line)
            continue
        if re.search("\(.* .*\)", line):
            target_list.append(line)
        elif re.search("\S+\s+[>=<]+\s+\S+", line) is not None:
            search_list = re.findall("\S+\s+[>=<]+\s+\S+", line)
            search_list = list(map(lambda x: x.strip(","), search_list))
            target_list += search_list
        elif "," in line:
            temp_list = line.split(",")
            if "" in temp_list:
                temp_list.remove("")
            temp_list = list(map(lambda x: x.strip(), temp_list))
            target_list += temp_list
        else:
            target_list += line.split()
    return target_list


def change_requires_struct(origin, target, items: dict, global_dict=None, macros_text=""):
    """改变依赖的结构"""
    if global_dict is None:
        global_dict = {}
    add_define_flags = []
    target_list = items[origin].copy()
    for build_rq in items[origin]:
        if "%else %if" in build_rq:
            target_list.remove(build_rq)
            build_rq = resolve_else_judgement(remove_marginals_quotes(build_rq))
            value = build_rq.split("%if")[0].strip()
            if value.startswith("%"):
                value = "\"" + value.replace("\"", "\\\"") + "\""
            add_judgement, add_define_flags = change_judgement_grammar(build_rq.replace(value, ""), global_dict,
                                     macros_text=macros_text)
            new_key = target + add_judgement
            if new_key in items:
                items[new_key].append(value)
            else:
                items[new_key] = [value]

        elif "%if" in build_rq:
            target_list.remove(build_rq)
            build_rq = remove_marginals_quotes(build_rq)
            add_judgement, add_define_flags = change_judgement_grammar(build_rq, global_dict, macros_text=macros_text)
            new_key = target + add_judgement
            value = build_rq.split("%if")[0].strip()
            value = divide_several_requires([value])
            value = list(map(lambda x: change_macros_usage(x, global_dict, macros_text), value))
            for v_index, v_item in enumerate(value):
                if v_item.startswith("%"):
                    value[v_index] = "\"" + v_item.replace("\"", "\\\"") + "\""
            if new_key in items:
                items[new_key] += value
            else:
                items[new_key] = value
        else:
            pass
    target_list = divide_several_requires(target_list)
    target_list = list(map(lambda x: change_macros_usage(x, global_dict, macros_text), target_list))
    items[origin] = target_list
    return items, add_define_flags


def change_judgement_grammar(line, global_dict, macros_text=""):
    tmp_conditions = line.split("%if")[1:]
    conditions = list(map(lambda x: "%if" + x.rstrip(), tmp_conditions))
    judgement = ""
    add_define_flags = []
    for condition in conditions:
        if judgement != "":
            judgement += " "
        # TODO(%if %{with ***}=>when )
        if re.match("%if %\{with ", condition) or re.match("%if %\{without ", condition):
            with_parts, without_parts = get_if_with_parts(condition)
            judgement = "when"
            if len(with_parts):
                judgement += " +" + " and +".join(with_parts)
            if len(without_parts):
                if with_parts:
                    judgement += " and"
                judgement += " -" + " and -".join(without_parts)
        elif re.match("%if\s+%\{\?_with_\w+:\s*1", condition):
            base_param = condition.split("_with_")[1].split(":")[0].rstrip("}")
            judgement = "when"
            add_define_flags.append(base_param)
            judgement += " " + base_param
        # TODO(	%if 0%{?openEuler}=>when ${{rpmrc.openEuler})
        elif re.fullmatch("%if\s+[0x]%\{\?[\w|_]+}", condition) is not None:
            base_condition = condition.split("?")[1].rstrip("}")
            if condition in RPM_GLOBAL_MACROS:
                judgement += "when ${{rpmrc." + base_condition + "}}"
            elif condition in global_dict:
                judgement += "when ${{rpmGlobal." + base_condition + "}}"
            else:
                judgement += condition.replace("%if", "rpmWhen")
        # TODO(	%if %{openEuler}=>when ${{rpmGlobal.openEuler}})
        elif re.fullmatch("%if\s+%\{[\w|_]+}", condition) is not None:
            judgement += "when " + add_rpm_global(condition.split("{")[1].rstrip("}"))
        # TODO(%ifarch|%ifos|%ifnarch|%ifnos=>when arch in)
        elif re.match("%ifarch|%ifos|%ifnarch|%ifnos", condition) is not None:
            if " " not in condition:
                logger.error("error condition: {0}".format(condition))
            base_condition = condition.strip().split(" ", 1)[1]
            if base_condition.startswith("%{") and base_condition.endswith("}"):
                base_param = base_condition.replace("%{", "").replace("}", "")
                changed_param = change_macros_type(base_param, global_dict, macros_text)
                condition = condition.replace(base_condition, changed_param)
            condition = condition.replace("%ifarch", "when arch in").replace(
                "%ifnarch", "when arch not in").replace("%ifos", "when os in").replace(
                "%ifnos", "when os not in")
            if re.search(" (%\{([\w_]+)})", condition):
                params = re.findall(" (%\{([\w_]+)})", condition)
                for param in params:
                    changed_param = change_macros_type(param[1], global_dict, macros_text)
                    condition = condition.replace(param[0], changed_param)
            judgement += condition
        else:
            judgement += change_to_when_or_rpmwhen(condition, global_dict, macros_text)
    judgement = change_macros_usage(judgement, global_dict, macros_text)
    judgement = merge_multi_judgement(judgement)
    if "%if " in judgement:
        judgement = judgement.replace("%if ", "rpmWhen ")
    if not judgement.startswith(" ") and judgement != "":
        judgement = " " + judgement.strip()
    return judgement.rstrip(), add_define_flags


def change_to_when_or_rpmwhen(condition, spec_global, spec_macros):
    condition = condition.replace("%if", "").strip()
    non = "not " if condition.strip().startswith("!") else ""
    if re.fullmatch("\w%\{?.*}\s+!\s*=\s*\w", condition):
        if condition[0] == condition[-1]:
            base_param = condition.split("%{")[1].split("}")[0]
        else:
            base_param = ""
    else:
        base_param = ""
    if base_param != "":
        if base_param in RPM_GLOBAL_MACROS or base_param in spec_global:
            rpm_flag = "when"
        elif re.search("\n%define\s+" + base_param + " ", spec_macros) is not None or re.search("\n%global\s+" + base_param + " ", spec_macros) is not None:
            rpm_flag = "when"
        else:
            rpm_flag = "rpmWhen"
    else:
        rpm_flag = "rpmWhen"
    if rpm_flag == "rpmWhen":
        target = rpm_flag + " " + condition.strip()
    else:
        modified_condition = modify_by_when(base_param, spec_global, spec_macros)
        if non:
            target = rpm_flag + modified_condition.replace("!", non, 1).strip()
        else:
            target = rpm_flag + modified_condition.strip()
    return target


def merge_multi_judgement(words):
    when_count = words.count("when")
    if when_count > 1:
        words = words.replace("when", "<when>")
        words = words.replace("<when>", "when", 1)
        words = words.replace("<when>", "and")
    return words


def modify_by_when(word, spec_global, spec_macros=""):
    if re.search("\w?%\{\??\w+}", word) is not None:
        search_words = re.findall("\w?%\{\??\w+}", word)
        for search_word in search_words:
            core_word = search_word.split("%{")[1].rstrip("}").lstrip("?")
            if core_word in RPM_GLOBAL_MACROS:
                word = "${{rpmGlobal." + core_word + "}}"
            elif core_word in spec_global or core_word in spec_macros:
                word = "${{rpmGlobal." + core_word + "}}"
            else:
                word = word.replace(search_word, "${{" + core_word + "}}")
    return word


def add_rpm_global(before):
    if before in RPM_GLOBAL_MACROS:
        after = "${{rpmrc." + before + "}}"
    else:
        after = "${{rpmGlobal." + before + "}}"
    return after


def change_macros_usage(line, rpm_global=None, rpm_macros=""):
    if rpm_global is None:
        rpm_global = {}
    if line.startswith("rpmWhen"):
        return line
    # TODO(%{version}-%{release}=>${{pkg.version}}-${{release}})
    if re.search("%\{version}|%\{name}|%\{release}|%\{epoch}", line):
        line = line.replace("%{version}", "${{pkg.version}}").replace("%{name}", "${{pkg.name}}").replace("%{release}", "${{pkg.release}}").replace("%{epoch}", "${{pkg.epoch}}")
    # TODO(%{atk_version}=>${{rpmGlobal.atk_version}})
    if re.search(" %\{\w+}", line) is not None:
        results = re.findall(" %\{\w+}", line)
        for macro in results:
            param = macro.strip().split("%{")[1].strip("}")
            if param in RPM_GLOBAL_MACROS:
                prefix = "${{rpmrc."
                suffix = "}}"
            elif param in rpm_global or param in rpm_macros:
                prefix = "${{rpmGlobal."
                suffix = "}}"
            else:
                prefix = "%{"
                suffix = "}"
            line = line.replace(macro, macro.replace("%{", prefix).replace("}", suffix))
    return line


def check_sub_files(line):
    line_list = line.split()
    if line_list and line_list[0] == "%files":
        line_list.remove("%files")
    line_list = remove_files_param(line_list)
    if len(line_list) == 0:
        return False
    else:
        return True


def get_sub_name_from_line(line, keywords):
    line_list = line.split()
    if line_list and line_list[0] == keywords:
        line_list.remove(keywords)
    line_list = remove_files_param(line_list)
    if "-n" in line_list:
        if len(line_list) >= line_list.index("-n") + 2:
            return line_list[line_list.index("-n") + 1]
        else:
            logger.error("error format in this line: " + line)
            return line_list[-1]
    else:
        return line_list[-1]


def remove_files_param(opt):
    while "-f" in opt:
        index_input = opt.index("-f") + 1
        opt.pop(index_input)
        opt.remove("-f")
    return opt


def right_strip_extra_judge(text):
    line_list = text.split(os.linesep)
    last_line = line_list[0]
    if last_line.startswith("%if"):
        return os.linesep.join(line_list[:-1])
    return text


def remove_package_name(line, remove_keywords=False):
    opts = line.split()
    target = "" if remove_keywords else opts[0]
    if len(opts) < 2:
        return line
    param_value = False
    for opt in opts[1:]:
        if opt.startswith("-"):
            if opt != "-n":
                target += " " + opt
                param_value = True
        elif param_value:
            target += " " + opt
            param_value = False
    return target


def check_rpm_condition(judgements, rpm_globals):
    rpm_condition = True
    for judgement in judgements:
        if "%{with " in judgement or "%{without " in judgement or "%ifarch" in judgement:
            rpm_condition = True
            continue
        if re.search("%\{\??[\w_]+}", judgement) is not None:
            conditions = re.findall("%\{\??[\w_]+}", judgement)
            for condition in conditions:
                condition = condition.lstrip("%{?").rstrip("}")
                if condition not in RPM_GLOBAL_MACROS or condition not in rpm_globals:
                    rpm_condition = False
                    break
    return rpm_condition


def change_macros_type(base_condition: str, rpm_globals, macros_str=""):
    if base_condition in rpm_globals or base_condition in macros_str:
        result = "${{rpmGlobal.%s}}" % base_condition
    elif base_condition in RPM_SYSTEM_MACROS:
        result = "${{rpmrc.%s}}" % base_condition
    else:
        result = base_condition
    return result
