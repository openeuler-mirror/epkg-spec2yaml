import re
from openEulerTransition.configure.spec_config import *


def lower_first_word(words: str):
    if words == "Patches":
        return "patchset"
    if words == "Sources":
        return "source"
    if words == "Macros":
        return "rpmMacros"
    if words.upper() == "URL":
        return "meta.homepage"
    if words in ["Description", "License", "Summary"]:
        return "meta." + words[0].lower() + words[1:]
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


def revise_macros(macros: list, source_dict: dict):
    """
    从源数据中修改宏
    :param macros: 宏
    :param source_dict: 源数据
    :return:
    """
    for i in range(len(macros)):
        line = macros[i]
        if re.search(r"\\\\[0-9|a-z|A-Z|.|(|)|$]", line) is not None:
            exist_special_words = re.findall(r"\\\\[0-9|a-z|A-Z|.|(|)|$]", line)
            for a_special_words in exist_special_words:
                line = line.replace(a_special_words, "\\\\" + a_special_words)
        if re.search(r"\\[0-9|a-z|A-Z|.|(|)|$]", line) is not None:
            exist_special_words = re.findall(r"\\[0-9|a-z|A-Z|.|(|)|$]", line)
            for a_special_words in exist_special_words:
                start = 0
                while line.find(a_special_words, start, len(line)) != -1:
                    sub_index = line.find(a_special_words, start, len(line))
                    if sub_index > 0 and line[sub_index-1] == "\\":
                        start = sub_index + 1
                        continue
                    line_list = list(line)
                    line_list.insert(sub_index, "\\")
                    line = "".join(line_list)
                    start = line.find(a_special_words, start, len(line)) + 1
        if not line.startswith("%define") and re.search("%\{version\}", line) or re.search("%\{name\}", line):
            if 'Version' in source_dict:
                line = re.sub("%\{version\}", source_dict['Version'][0], line)
            if 'Name' in source_dict:
                line = re.sub("%\{name\}", source_dict['Name'][0], line)
        macros[i] = line


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


def _remove_duplicate(_dict):
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
