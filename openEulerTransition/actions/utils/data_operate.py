import re
import os
from openEulerTransition.configure.spec_config import *


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


def resolve_inner_quotes(_line):
    """
    处理字符串内部的引号
    :param _line:
    :return:
    """
    can_trans = not ((_line.startswith("\"") and _line.endswith("\"")) or (
            _line.startswith("\'") and _line.endswith("\'")))
    if can_trans and ("\"" in _line and "\\\"" not in _line):
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
    for _key4 in SKIPS:
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


def resolve_special_macros_config(line, source_items: dict):
    """
    处理特殊的宏配置
    :param line:
    :param source_items:
    :return:
    """
    if line == "%package_help":
        if "SubPackages" in source_items:
            source_items["SubPackages"]["help"] = {"Summary": ["Documents for %{name}"],
                                                   "BuildArch": ["noarch"],
                                                   "Requires": ["man info"],
                                                   "Description":
                                                       "Man pages and other related documents for %{name}."}
        else:
            source_items["SubPackages"] = {"help": {"Summary": ["Documents for %{name}"],
                                                    "BuildArch": ["noarch"],
                                                    "Requires": ["man info"],
                                                    "Description":
                                                        "Man pages and other related documents for %{name}."}}


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
            ":\t" in val or \
            val.endswith(':'):
        quote_char = ""
        extra_escape = "\\" if val.endswith("\\") else ""
        if not ((val.startswith("\"") and val.endswith("\"")) or (val.startswith("\'") and val.endswith("\'"))):
            if '\"' in val and "\'" not in val:
                quote_char = '\''
            elif '\"' not in val and "\'" in val:
                quote_char = '\"'
        return quote_char + val + extra_escape + quote_char
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
    if this_key in ["include", "description"]:
        return dict1
    if this_key in SINGLES:
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
    elif "%if ! " in judgement:
        return judgement.replace("%if ! ", "%if ")
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
    configure = ""
    build = ""
    configure_cmd = False
    line_list = content.split(os.linesep)
    for num, line in enumerate(line_list):
        if line.startswith("#"):
            if configure_cmd:
                configure += line + os.linesep
            else:
                build += line + os.linesep
            continue
        if configure_cmd:
            if line.startswith("%if") or line.startswith("%else") or line.startswith("%endif"):
                configure += line + os.linesep
            elif line.endswith("\\"):
                configure += line + os.linesep
            else:
                configure += line + os.linesep
                configure_cmd = False
        if "configure" in line.lower():
            if "configure" in line:
                line = line.replace("configure", "configure %%{env.configureFlags}")
            if not configure_cmd:
                build += "configure" + os.linesep
            configure_cmd = True
            configure += line + os.linesep
        if not configure_cmd:
            build += line + os.linesep
    return configure.strip(), build.strip()


def get_if_with_parts(line):
    with_parts = re.findall("%if %[{]with \w+}", line)
    without_parts = re.findall("%if %[{]without \w+}", line)
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
    target_first = "--rpm_macro_param: " + first_line if "<lua>" in first_line else "#rpm_macro_param: " + first_line
    temp_list = first_line.split()
    if len(temp_list) > 1 and (temp_list[0].startswith("-") or temp_list[1].startswith("-")):
        text = text.replace(first_line, target_first, 1)
    if "<lua>" in first_line:
        name = obj.name
        file_name = os.path.splitext(name)[0]
        mode = "a+" if file_obj.CREATED_LUA[file_name] else "w+"
        file_obj.CREATED_LUA[file_name] = True
        with open(name.replace(".sh", ".lua"), mode) as f:
            if mode == "w+":
                f.write("#!/usr/bin/env lua" + os.linesep*2)
            text = add_tab_in_lines(text)
            f.write("function " + name + "()" + os.linesep + text + os.linesep)
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
        if "-f" in files_input:
            files_input_value = "#rpm_macro_param:"
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
            target_items = add_input_to_files(files_input_value + get_line_suffix(if_lines, else_lines, else_status), target_items)
    elif len(opt) == 1 and opt[0] == "%files":
        if origin_items != target_items:
            target_items = origin_items
        if "files" not in target_items:
            target_items["files"] = ""
    return target_items


def strip_files_startswith(text):
    if re.match("%files \S+ -f", text) is not None:
        match_words = re.findall("%files \S+ -f", text)[0]
        match_words = remove_package_name(match_words)
        strip_words = match_words.rstrip("-f").strip()
        text = text.replace(strip_words, "#rpm_macro_param:", 1)
    if text.startswith("%files"):
        # text = text.lstrip("%files")
        first_line = text.split(os.linesep)[0]
        target_first = remove_package_name(first_line)
        text = text.replace(first_line, target_first, 1)
        if target_first != "%files":
            text = text.replace("%files", "#rpm_macro_param:", 1)
        else:
            text = text.replace("%files", "", 1)
    return text


def divide_several_requires(origin_list):
    target_list = []
    for line in origin_list:
        if "%if" in line:
            target_list.append(line)
            continue
        if re.search("\S+ [>=<]+ \S+", line) is not None:
            search_list = re.findall("\S+ [>=<]+ \S+", line)
            search_list = list(map(lambda x: x.strip(","), search_list))
            target_list += search_list
        elif "," in line:
            temp_list = line.split(",")
            temp_list = list(map(lambda x: x.strip(), temp_list))
            target_list += temp_list
        else:
            target_list += line.split()
    return target_list


def change_requires_struct(origin, target, items: dict):
    """改变依赖的结构"""
    target_list = items[origin].copy()
    for build_rq in items[origin]:
        if "%else %if" in build_rq:
            target_list.remove(build_rq)
            build_rq = resolve_else_judgement(build_rq)
            value = build_rq.split("%if")[0].strip()
            new_key = target + " " + change_judgement_grammar(build_rq.replace(value, "")).strip()
            if new_key in items:
                items[new_key].append(value)
            else:
                items[new_key] = [value]

        elif "%if" in build_rq:
            new_key = target + " " + change_judgement_grammar(build_rq, cut_judge=True)
            value = build_rq.split("%if")[0].strip()
            value = divide_several_requires([value])
            value = list(map(lambda x: change_macros_usage(x), value))
            if new_key in items:
                items[new_key] += value
            else:
                items[new_key] = value
            target_list.remove(build_rq)
        else:
            pass
    target_list = divide_several_requires(target_list)
    target_list = list(map(lambda x: change_macros_usage(x), target_list))
    items[origin] = target_list
    return items


def change_judgement_grammar(line, cut_judge=False):
    if cut_judge:
        keywords = line.split("%if")[0]
        line = line.replace(keywords, "", 1)
    judgement = ""
    # TODO(%if %{with ***}=>when )
    if "%if %{with" in line:
        with_parts, without_parts = get_if_with_parts(line)
        judgement = "when"
        if len(with_parts):
            judgement += " +" + " +".join(with_parts)
        if len(without_parts):
            judgement += " -" + " -".join(without_parts)
    # TODO(	%if 0%{?openEuler}=>when %%%{rpmGlobal.openEuler})
    if re.search("%if\s+[0x]%\{\?[\w|_]}", line) is not None:
        results = re.findall("%if\s+[0x]%\{\?[\w|_]}", line)
        conditions = list(map(lambda x: x.split("?")[0].rstrip("}"), results))
        for condition in conditions:
            if condition in RPM_GLOBAL_MACROS:
                judgement += " when %%%{rpmGlobal." + condition + "}"
            else:
                judgement += " when %{" + condition + "}"
    # TODO(	%if %{openEuler}=>when %%{rpmGlobal.openEuler})
    if re.search("%if\s+%\{[\w|_]}", line) is not None:
        results = re.findall("%if\s+%\{[\w|_]}", line)
        conditions = list(map(lambda x: x.split("?")[0].rstrip("}"), results))
        results = list(map(lambda x: "%%{rpmGlobal." + x + "}", conditions))
        judgement += " when " + " ".join(results)
    # TODO(%ifarch|%ifos|%ifnarch|%ifnos=>when arch in)
    if re.search("%ifarch|%ifos|%ifnarch|%ifnos", line) is not None:
        results = re.findall("%if.+", line)
        tmp_results = results.copy()
        for i in tmp_results:
            if re.search("%ifarch|%ifos|%ifnarch|%ifnos", i) is None:
                results.remove(i)
        conditions = list(map(lambda x: x.replace("%ifarch", " when arch in").replace(
            "%ifnarch", " when arch not in").replace("%ifos", " when os in").replace(
            "%ifnos", " when os not in"), results))
        judgement += " ".join(conditions)
    if "%if" in line and judgement == "":
        judgement = line.replace("%if !", "when not").replace("%if", "when")
    judgement = change_macros_usage(judgement)
    return judgement


def change_macros_usage(line):
    # TODO(%{version}-%{release}=>%%{version}-%%{release})
    if re.search("%\{version}|%\{name}|%\{release}|%\{epoch}", line):
        line = line.replace("%{version}", "%%{version}").replace("%{name}", "%%{name}").replace("%{release}", "%%{release}").replace("%{epoch}", "%%{epoch}")
    # TODO(%{atk_version}=>%%{rpmGlobal.atk_version})
    if re.search(" %\{\w+}", line) is not None:
        results = re.findall(" %\{\w+}", line)
        for macro in results:
            line = line.replace(macro, macro.replace("%{", "%%{rpmGlobal."))
    return line


def check_sub_files(line):
    line_list = line.split()
    if line_list and line_list[0] == "files":
        line_list.remove("files")
    while "-f" in line_list:
        index_input = line_list.index("-f") + 1
        line_list.pop(index_input)
        line_list.remove("-f")
    if len(line_list) == 0:
        return False
    else:
        return True


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
