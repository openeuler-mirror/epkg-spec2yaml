#!/bin/env python
# -*- encoding: utf-8 -*-

"""
功能：文件基础函数、涉及各种文件格式的读、写 、拷贝、移动、delete等例如 yaml file ,json,xml等
版权信息：Copyright Huawei Technologies Co., Ltd. 2010-2022. All rights reserved.
"""
import os
import shutil
import glob
import yaml
import re
import json
import codecs
import platform
import jinja2
from datetime import date, datetime

from openEulerTransition.logs.log import logger
from os.path import join, basename
from collections import OrderedDict
from openEulerTransition.logs.error_info import EXCEPTION_CODE
import threading
import configparser


class Path:
    @staticmethod
    def join(path, *paths):
        """拼接路径"""
        return os.path.abspath(os.path.join(path, *paths))

    @staticmethod
    def abs(path, *paths):
        """获取拼接后的绝对路径"""
        return os.path.abspath(os.path.join(path, *paths))

    @staticmethod
    def cwd():
        """ 获取当前工作路径 """
        return Path.abs(os.getcwd())

    @staticmethod
    def parent(path):
        """ path 的上一级目录 """
        return Path.join(path, '..')

    @staticmethod
    def relpath(path, start=None):
        """获取相对路径"""
        return os.path.relpath(path, start)

    @staticmethod
    def unnormpath(path):
        """ 反规范化路径, 会将 \\ 替换为 / """
        if not platform.system() == 'Windows':
            return path
        # If it is a drive letter under Windows, special treatment will be given to fix the drive letter in uppercase
        if path[1] == ':':
            win_path = path[0].upper() + path[1:]
            return win_path.replace('\\', '/')
        return path.replace('\\', '/')

    @staticmethod
    def all_subdirs(path):
        """ 获取所有子目录 """
        if not os.path.isdir(path):
            return []
        return list(filter(lambda o: os.path.isdir(Path.join(path, o)), os.listdir(path)))

    @staticmethod
    def makedirs(path):
        """创建多层目录"""
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def removedirs(path):
        """递归删除目录及其子目录"""
        if not os.path.exists(path):
            return
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)


class Chdir:
    def __init__(self, to):
        self.to = to
        self.back = os.getcwd()

    def __enter__(self):
        os.chdir(self.to)

    def __exit__(self, exc_type, exc_value, exc_tb):
        os.chdir(self.back)

def check_conf_file(path):
    if os.path.isfile(path):
        if path.endswith(".conf"):
            return True
        else:
            return False

def check_yaml_file(path):
    if os.path.isfile(path):
        if path.endswith(".yaml") or path.endswith(".yml"):
            return True
        else:
            return False


def check_spec_file(path):
    if os.path.isfile(path):
        if path.endswith(".spec"):
            return True
        else:
            return False


def make_sure_dir(*args, **kwargs):
    clean_existing = kwargs["clean_existing"] if "clean_existing" in kwargs else False
    for d in args:
        if os.path.exists(d):
            if clean_existing:
                shutil.rmtree(d)
                logger.info("[make_sure_dir]rmtree %s" % d)
                os.makedirs(d)
                logger.info("[make_sure_dir]makedirs %s" % d)
        else:
            os.makedirs(d)
            logger.info("[make_sure_dir]makedirs %s" % d)


def get_list_by_wildcard(wildcard):
    dirs = []
    files = []
    for e in glob.glob(wildcard):
        if not os.path.exists(e):
            logger.warn("[get_list_by_wildcard] %s is not existed" % e)
        if os.path.isdir(e):
            dirs.append(e)
        else:
            files.append(e)
    # print(" dirs: {}\n, files: {}".format(dirs, files))
    return dirs, files


def remove(path):
    tp = type(path)
    if tp == str:
        dirs, files = get_list_by_wildcard(path)
        for d in dirs:
            shutil.rmtree(d)
            logger.info("[remove]rmtree %s" % d)
        for f in files:
            os.remove(f)
            logger.info("[remove]remove %s" % f)
    elif tp == list or tp == tuple:
        for e in path:
            remove(e)
            logger.info("[remove]remove %s" % e)


def check(value):
    if value == "default":
        return value
    pattern = re.compile(r'^(0*)([1-7][0-7]{2})$')
    try:
        new_value = pattern.match(value).group()
    except AttributeError:
        logger.error("对于文件和目录的权限只能是八进制的数据，请核实属性")
        raise Exception("权限%s不是八进制" % value)
    else:
        return new_value


def write_yaml(content, to_file, default_flow_style=False, default_style=" ", keep_order=False):
    with open(to_file, "w") as new_file:
        if not keep_order:
            yaml.dump(content, new_file, default_flow_style=default_flow_style,
                      default_style=default_style, allow_unicode=True)
        else:
            _ordered_yaml_dump(content, new_file, default_flow_style=default_flow_style)


def read_yaml(source, from_file=True, jina_template=True, keep_order=True, include=False):
    if include:
        source = include_yaml(source)

    if source is None:
        raise NameError('Yaml file path cannot be None!')
    if not os.path.exists(source):
        raise FileNotFoundError("Sorry! We don't find " + source + ".")

    if from_file:
        with open(source, encoding='UTF-8') as f:
            content = f.read()

    if jina_template:
        yaml_content = content
        for i in range(4):
            yaml_content = _ordered_jina_yaml_template(source, str(yaml_content), keep_order)
    else:
        yaml_content = _ordered_yaml_load(content) if keep_order else yaml.safe_load(content)

    return yaml_content


def _ordered_jina_yaml_template(yaml_file, content, keep_order):
    yaml_file_name = os.path.basename(yaml_file)
    yaml_dir_name = os.path.dirname(yaml_file)
    data_dict = _ordered_yaml_load(content) if keep_order else yaml.safe_load(content)
    if 'systemEnv' in data_dict:
        if type(data_dict['systemEnv']) != list:
            logger.error("=====systemEnv的格式不对，请检查你的yaml file: {}配置=====".format(yaml_file))
            raise Exception(EXCEPTION_CODE[601], data_dict['systemEnv'])
        sys_env_dict = {}
        for k in data_dict['systemEnv']:
            val = os.getenv(k)
            if not val:
                # 变量不存在即跳过转换
                # logger.warn("=====systemEnv 不存在系统变量：{}，请检查你的yaml file: {}配置=====".format(k, yaml_file))
                continue
            if platform.system() == 'Windows':
                # 由于windows下jinja模块对有路径 c:\\情况会报错,使用encode规避，并且去掉b'开头，'结尾的字符串
                sys_env_dict[k] = re.sub("^b'|'$", '', str(os.getenv(k).encode('utf-8')))  # .replace('\\', '/')
            else:
                sys_env_dict[k] = os.getenv(k)
        # 替换 systemEnv type from list to dict
        del data_dict['systemEnv']
        data_dict['systemEnv'] = sys_env_dict
    try:
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath=yaml_dir_name))
        template = env.get_template(yaml_file_name)
    except jinja2.TemplateNotFound as e:
        logger.error("=====jinja2 TemplateNotFound ，请检查你的yaml file: {}配置=====".format(yaml_file))
        raise Exception(EXCEPTION_CODE[601], e)
    res_data = template.render(**data_dict)
    return _ordered_yaml_load(res_data) if keep_order else yaml.safe_load(res_data)


class ComplexEncoder(json.JSONEncoder):
    """"
    Problem description: When the JSON provided by Python is used to convert data into JSON data,
                        An error is reported for data in datetime format:
                        TypeError: Object of type'datetime' is not JSON serializable.
    Solution:   Rewrite the JSON class and use the built-in for the rest.
                When using json.dumps, you need to invoke the class defined above
                and specify the cls parameter to ComplexEncoder. The code is as follows:
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


def write_json(content, to_file, sort_keys=False):
    with open(to_file, "w") as f:
        json.dump(content, f, sort_keys=sort_keys, indent=2, separators=(',', ': '), cls=ComplexEncoder)


def read_json(path):
    with codecs.open(path, 'r', 'utf-8', 'replace') as fin:
        return json.load(fin)


def _ordered_yaml_load(content, loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(loader):
        pass

    def construct_mapping(ldr, node):
        ldr.flatten_mapping(node)
        return object_pairs_hook(ldr.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.safe_load(content)


def _ordered_yaml_dump(data, stream=None, dumper=yaml.SafeDumper, default_flow_style=False):
    class OrderedDumper(dumper):
        pass

    def _dict_representer(dpr, data):
        return dpr.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, default_flow_style=default_flow_style, width=1000, allow_unicode=True)


def copy_rename(f, to, rename=""):
    # 设置中间临时文件夹进行处理
    tmp = "renamedir"
    make_sure_dir(tmp)
    shutil.copy2(f, tmp)
    os.rename(join(tmp, basename(f)), join(tmp, rename))
    logger.debug("[copy_rename]rename from %s ======>> %s" %
                 (join(tmp, basename(f)), join(tmp, rename)))
    shutil.copy2(join(tmp, rename), to)
    logger.debug("[copy_rename]move from %s ======>> %s" %
                 (join(tmp, rename), to))


def config_parser(file_path):
    """
    分析ini 文件
    :param file_path: 文件路径
    """
    cf = configparser.ConfigParser()
    cf.read(file_path, encoding="utf-8")
    d = dict(cf._sections)
    for k in d:
        d[k] = dict(d[k])
    return d


def calc_filesize(filename):
    return os.stat(filename).st_size


def get_files_fist(path):
    result = list()
    if os.path.isfile(path):
        result.append(path)
    elif os.path.isdir(path):
        for dirpath, dirnames, filenames in os.walk(path, followlinks=True):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                result.append(file_path)
        result.sort()
    else:
        print("it's a special file(socket,FIFO,device file)")
    return result


def write_to_file(contents, dest_file):
    fp = open(dest_file, "w")

    for content in contents:
        str0 = str(content)
        str1 = str0.replace("\\\\", "/")
        fp.write(str1)
        fp.write(os.linesep)
    fp.close()


def find_path_with_reg(cur_path, reg_exp: str):
    """
    :param cur_path:
    :param reg_exp: "tmp*/ww*/a*.yaml"
    :return:
    """
    res_paths = []
    path_lst = re.split(r'[/ \\]', cur_path) + re.split(r'[/ \\]', reg_exp)
    patt_lst = [i for i in path_lst if i]
    size = len(patt_lst)
    for this_path in get_alldirs_of_path(cur_path):
        this_lst = re.split(r'[/ \\]', this_path)
        if len(this_lst) != size or not math_path(patt_lst, this_lst):
            continue
        res_paths.append(this_path)
    return res_paths


def get_alldirs_of_path(cur_path):
    """
    root 表示当前正在访问的文件夹路径
    dirs 表示该文件夹下的子目录名list
    files 表示该文件夹下的文件list
    :param cur_path:
    :return: 路径列表
    """
    tmp = list()
    for root, dirs, files in os.walk(cur_path, followlinks=True):
        tmp.extend([os.path.join(root, f) for f in files])
        tmp.extend([os.path.join(root, d) for d in dirs])
    return tmp


def math_path(patt_lst, this_lst):
    """
    支持正则表达式的路径匹配
    :param patt_lst: 模式分割列表
    :param this_lst: 路径分割列表
    :return:
    """
    for i in range(len(this_lst)):
        if not re.findall(patt_lst[i], this_lst[i]):
            return None
    return True


def merge_file(paths_lst, new_file):
    print(paths_lst, new_file)
    with open(new_file, mode='a', encoding="utf-8") as file:
        file.seek(0)
        file.truncate()
        for path in paths_lst:
            with open(path, encoding="utf-8") as child:
                child_data = child.read()
                file.write(child_data)
            file.write(os.linesep)
    return new_file


def include_yaml(path):
    new_file_path = os.path.dirname(os.path.abspath(path))
    new_file = Path.join(new_file_path, '..', 'tmp_include_result.yaml')
    data = read_yaml(path, jina_template=False, include=False)

    if data.get('include') and isinstance(data.get('include'), list):
        include_lst = data.get('include')
        include_lst.append(path)
        return merge_file(include_lst, new_file)
    return path


def merge_yaml(paths_lst):
    new_file_path = os.path.dirname(os.path.abspath(paths_lst[-1]))
    # file_name = str(time.time()).replace('.', '')
    new_file = 'tmp_include_result' + str(threading.currentThread().ident) + '.yaml'
    return merge_file(paths_lst, new_file)
