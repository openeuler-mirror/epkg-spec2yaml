import os
import re
import sys
import copy
from openEulerTransition.logs.log import logger
from openEulerTransition.actions.utils.file_operate import Chdir
from openEulerTransition.configure.spec_config import *
from openEulerTransition.configure.yaml_config import *

HEADERS = ('package',
           'description',
           'prep',
           'build',
           'install',
           'clean',
           'check',
           'preun',
           'pretrans',
           'pre',
           'postun',
           'posttrans',
           'post',
           'files',
           'changelog',
           'include')
SINGLES = ('Summary',
           'Name',
           'Version',
           'Epoch',
           'URL',
           'Group',
           'BuildArch',
           'Source',
           'Patch',
           'AutoReq',
           'AutoProv',
           'AutoReqProv',
           'Autoreq',
           'Autoprov',
           'Autoreqprov',
           'Prefix',
           'License')
REQUIRES = ('BuildRequires',
            'Requires',
            'Requires(post)',
            'Requires(postun)',
            'Requires(posttrans)',
            'Requires(pre)',
            'PreRequires', 'PreReq', 'Prereq',  # alias in old spec
            'Requires(preun)',
            'Requires(pretrans)',
            'Provides',
            'Obsoletes',
            'Conflicts',
            'BuildConflicts',
            'FilesJudgement',
            )
SKIPS = ('BuildRoot',)

ORDER_ENTRIES = ['Macros',
                 'Name',
                 'Summary',
                 'Version',
                 'Release',
                 'Epoch',
                 'Group',
                 'License',
                 'URL',
                 'SCM',
                 'Sources',
                 'ExtraSources',
                 'Patches',
                 'Description',
                 'Define',
                 'Undefine',
                 'Global',
                 'Requires',
                 'RequiresPre',
                 'RequiresPreUn',
                 'RequiresPreTrans',
                 'RequiresPost',
                 'RequiresPostUn',
                 'RequiresPostTrans',
                 'BuildRequires',
                 'Provides',
                 'Obsoletes',
                 'Conflicts',
                 'ConfigOptions',
                 'Builder',
                 'BuildArch',
                 'ExclusiveArch',
                 'LocaleName',
                 'LocaleOptions',
                 'Files',
                 'FilesInput',
                 'SupportOtherDistros',
                 'UseAsNeeded',
                 'NoAutoReq',
                 'NoAutoProv',
                 'NoAutoReqProv',
                 'ExclusiveArch',
                 'ExcludeArch',
                 'Recommends',
                 'Supplements',
                 'Prefix',
                 'OrderWithRequires',
                 'Suggests',
                 'IncludeSource',
                 'FilesJudgement'
                 ]
# must have keys for 'main' package
MUSTHAVE = {'Release': '1',
            }

# state definition of parser
(
    ST_MAIN,
    ST_INLINE,
    ST_SUBPKG,
) = list(range(3))

TAB = '    '  # 4space, instead of Tab


class SpecError(Exception):
    """基础报错类型"""
    def __ini__(self, cur_state, cur_pkg, cur_line):
        self.cur_state = cur_state
        self.cur_pkg = cur_pkg
        self.cur_line = cur_line

    def __repr__(self):
        return self.cur_state + self.cur_pkg + self.cur_line


class SpecFormatError(SpecError):
    pass


class SpecUnknowLineError(SpecError):
    pass


class SpecUnknowHeaderError(SpecError):
    pass


class SpectacleDumper(object):
    """ Dumper medium data to output format.
        Supported output format:
            yaml, json

        The format of medium data of spectacle, as input for dumping:
        data = [
                 (key1, val1),                  # atom value
                 ('', ''),                      # for blank line
                 (key2, [val21, val22, val23]), # list of values
                 (key3, [                       # special for 'SubPackages'
                          [                         # items for subpkg
                            (key31, val31),
                            (key32, val32),
                            ...
                          ],
                          [
                            ...
                          ],
                        ]),
                 (key4, {                       # special for 'extra'
                          'key41': 'value41'
                          ...
                        })
               ]

    """

    spec_extra_keys = {
        # key -> ( nkey, nsubkey)
        #                ^^ None means to use <pkg_name>
        'Files': ('files', None),
        'macros': ('macros', None),
        'setup': ('setup', None),
        'define': ('define', None),
        'undefine': ('undefine', None),
        'global': ('global', None),
        'PostMakeInstallExtras': ('install', 'post'),
        'PreMakeInstallExtras': ('install', 'pre'),
        'PostMakeExtras': ('build', 'post'),
        'PreMakeExtras': ('build', 'pre'),
    }

    def __init__(self, format='yaml', opath=None, shell_functions=None, files=None):
        self.format = format
        self.opath = opath
        self.shell_functions = shell_functions
        self.files = files
        self.spec_extra = {}

    def _esc_value(self, val):
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

    def _dump_yaml(self, data, fp, indent='', cur_pkg='main', f_phase=None, f_runtime_phase=None, f_files=None,
                   script_data: dict = None, files_data: dict = None):
        """
        载入内容到yaml文件中
        :param data:源数据
        :param fp:yaml文件写对象
        :param script_data:shell脚本数据
        :param f_phase:shell脚本写对象
        :param f_runtime_phase:shell脚本写对象
        :param f_files:file.yaml写对象
        :param indent:行内容的开头，用于对内容做处理
        :param cur_pkg:用于区分主包和子包
        :param files_data:file.yaml的数据
        :return:
        """
        if indent:
            cur_indent = indent + '- '
        else:
            cur_indent = indent

        first_line = True
        if (f_phase or f_runtime_phase) and script_data:
            if f_phase:
                f_phase.write("#!/usr/bash\n\n")
                for function_name, function_text in script_data.items():
                    if function_name in ["install", "prep", "build", "clean", "check"]:
                        f_phase.write(function_name + "() {" + os.linesep + function_text + "}\n\n")
            if f_runtime_phase:
                f_runtime_phase.write("#!/usr/bash\n\n")
                for function_name, function_text in script_data.items():
                    if function_name not in ["install", "prep", "build", "clean", "check"]:
                        f_runtime_phase.write(function_name + "() {" + os.linesep + function_text + "}\n\n")
        if f_files and files_data:
            for file_member_key, file_member_value in files_data.items():
                f_files.write(file_member_key + ": |" + os.linesep)
                temp_text_list = file_member_value.split(os.linesep)
                for line in temp_text_list[1:]:
                    f_files.write(TAB + line + os.linesep)
        for key, value in data:
            if not first_line and indent:
                cur_indent = indent + '  '

            if not key:
                # empty key means blank line for break
                fp.write(os.linesep)
                continue

            if key == 'extra':
                for extra_key, extra_val in value.items():
                    if not extra_val:
                        continue

                    try:
                        nkey = self.spec_extra_keys[extra_key][0]
                        nsubkey = self.spec_extra_keys[extra_key][1]
                        if not nsubkey:
                            nsubkey = cur_pkg
                    except KeyError:
                        nkey = extra_key
                        nsubkey = cur_pkg

                    if not isinstance(extra_val, list):
                        extra_val = [extra_val]

                    if nkey not in self.spec_extra:
                        self.spec_extra[nkey] = {}
                    self.spec_extra[nkey][nsubkey] = extra_val

                    # handle macros
                    if extra_key == "macros":
                        fp.write(cur_indent + "rpmMacros:" + os.linesep)
                        for item in extra_val:
                            # fp.write(cur_indent + TAB + "%s\n" % item)
                            fp.write(cur_indent + TAB + "- \"%s\"\n" % item.replace('\"', '\\"'))
                        fp.write(os.linesep)
                continue

            if isinstance(value, list):
                fp.write(cur_indent + ("%s:" + os.linesep) % (key))

                for item in value:
                    if isinstance(item, list):
                        # only 'SubPackges' will reach here
                        # cur_pkg will be the 1st pair  ('Name', subpkg)
                        self._dump_yaml(item, fp, cur_indent + TAB, cur_pkg=item[0][1])
                        fp.write(os.linesep)
                    else:
                        fp.write(cur_indent + TAB + ("- %s" + os.linesep) % (self._esc_value(item)))
            elif isinstance(value, bool):
                if value:
                    fp.write(cur_indent + ("%s: yes" + os.linesep) % (key))
                else:
                    fp.write(cur_indent + ("%s: no" + os.linesep) % (key))
            elif isinstance(value, dict):
                if value:
                    fp.write(cur_indent + ("%s:" + os.linesep) % key)
                    for dict_key, dict_value in value.items():
                        if isinstance(dict_value, list):
                            fp.write(cur_indent + TAB + ("%s:" + os.linesep) % dict_key)
                            for sub_item in dict_value:
                                if isinstance(sub_item, list):
                                    self._dump_yaml(sub_item, fp, cur_indent + TAB, cur_pkg=sub_item[0][1])
                                    fp.write(os.linesep)
                                elif isinstance(sub_item, tuple) and len(sub_item) > 1:
                                    if isinstance(sub_item[1], str):
                                        if os.linesep in sub_item[1].strip():
                                            fp.write(cur_indent + TAB * 2 + ("%s: |" + os.linesep) % sub_item[0])
                                            line_list = sub_item[1].split(os.linesep)
                                            for line in line_list:
                                                fp.write(cur_indent + TAB * 3 + line + os.linesep)
                                        else:
                                            fp.write(cur_indent + TAB * 2 + ("%s: %s" + os.linesep) % (
                                                sub_item[0], sub_item[1]))
                                    elif isinstance(sub_item[1], list):
                                        fp.write(cur_indent + TAB * 2 + sub_item[0] + ":" + os.linesep)
                                        for line in sub_item[1]:
                                            fp.write(
                                                cur_indent + TAB * 3 + ("- %s" + os.linesep) % self._esc_value(line))
                                else:
                                    fp.write(cur_indent + TAB * 2 + ("- %s" + os.linesep) % (self._esc_value(sub_item)))
                        elif isinstance(dict_value, str):
                            if dict_key.isdigit():
                                dict_key = "\"" + dict_key + "\""
                            fp.write(cur_indent + TAB + ("%s: %s" + os.linesep) % (dict_key, dict_value))
            else:
                lines_to_write = value.splitlines()

                if len(lines_to_write) == 1:
                    try:
                        fp.write(cur_indent + ("%s: %s" + os.linesep) % (key, self._esc_value(value)))
                    except UnicodeEncodeError:
                        fp.write(cur_indent + ("%s: %s" + os.linesep) % (key, self._esc_value(value).encode('utf8')))

                elif len(lines_to_write) == 0:
                    # not exist until now
                    fp.write(cur_indent + ("%s:" + os.linesep) % (key))
                else:
                    fp.write(cur_indent + ("%s: |" + os.linesep) % key)
                    for line in lines_to_write:
                        fp.write(cur_indent + TAB + ("%s" + os.linesep) % line)

            first_line = False

    def dump(self, data, file_type=None):
        """
        载入文件
        :param data:源数据
        :param file_type:文件名
        :return:
        """
        if not file_type:
            file_type = self.format

        fp = sys.stdout
        fs_phase = sys.stdout
        fs_runtime = sys.stdout
        files_file = sys.stdout
        if self.files is None:
            self.files = {}
        if self.shell_functions:
            try:
                # fs = open(self.opath.replace(".yaml", ".sh"), "w")
                fs_phase = open("phase.sh", "w")
                fs_runtime = open("runtimePhase.sh", "w")
                files_file = open("files.yaml", "w")
            except IOError:
                logger.warn('Cannot open file %s for writing' % self.opath)
                # print out
                pass
        if self.opath:
            try:
                fp = open(self.opath, 'w')
            except IOError:
                logger.warn('Cannot open file %s for writing' % self.opath)
                # print out
                pass

        try:
            if file_type == 'yaml':
                self._dump_yaml(data, fp, script_data=self.shell_functions, f_phase=fs_phase,
                                f_runtime_phase=fs_runtime, f_files=files_file, files_data=self.files)
            else:
                logger.error('Unsupported spectacle data dump format: %s' % file_type)
        finally:
            fp.close()
            fs_phase.close()
            fs_runtime.close()
            files_file.close()

        return self.opath


class Convertor(object):
    """ Class for generic operations:
        *   Translate field names between different format
        *   Transfer non-order dict to ordered list of (key, val) pairs

        Derived sub-classes should update cv_table, the dictionary for
        translation, for specific input format.
    """

    cv_table = {}

    # un-ordered ones will be append the ordered ones in random order
    # 'Files', 'SubPackages' will the last two

    def __init__(self, cv_table=None):
        if cv_table is None:
            cv_table = {}
        self.cv_table.update(cv_table)

    def _translate_keys(self, _dict):
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
        # else: ignore

    def _replace_keys(self, _dict):
        """
        源数据中根据..去掉不需要的键值对
        :param _dict:
        :return:
        """
        for k, v in self.cv_table.items():
            if k == v:
                continue
            if k in _dict:
                _dict[v] = _dict[k]
                del _dict[k]

    def _remove_duplicate(self, _dict):
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

    def convert(self, _dict, need_break=True):
        """
        整理不必要和额外的数据
        :param _dict: 字典类型的输入
        :param need_break: 空关键字会跳过
        :return:
        """
        self._replace_keys(_dict)
        self._translate_keys(_dict)
        self._remove_duplicate(_dict)

        items = []
        package_name = ""
        for entry in ORDER_ENTRIES:
            if entry == "Name" and "SubPackages" in _dict:
                package_name = _dict["Name"]
            if not entry:
                # empty string means a blank line for break
                if need_break:
                    items.append(('', ''))
                continue

            if entry in _dict:
                if entry in MAY_QUOTATION_KEYWORDS:
                    if type(_dict[entry]) == list:
                        need_add_quotation = False
                        for item in _dict[entry]:
                            if type(item) == str and item.startswith("%"):
                                need_add_quotation = True
                                break
                        if need_add_quotation:
                            for index1, item in enumerate(_dict[entry]):
                                if "\"" not in item:
                                    _dict[entry][index1] = "\"" + item + "\""
                                elif "\'" not in item:
                                    _dict[entry][index1] = "\'" + item + "\'"
                    elif type(_dict[entry]) == str and (_dict[entry].lstrip().startswith("%") or ":" in _dict[entry]):
                        if len(_dict[entry].strip(os.linesep).split(os.linesep)) == 1:
                            if not ((_dict[entry].startswith("\"") and _dict[entry].endswith("\"")) or (
                                    _dict[entry].startswith("\'") and _dict[entry].endswith("\'"))):
                                if "\"" not in _dict[entry]:
                                    _dict[entry] = "\"" + _dict[entry].strip() + "\""
                                elif "\'" not in _dict[entry]:
                                    _dict[entry] = "\'" + _dict[entry].strip() + "\'"
                if entry in ["Sources", "Patches"]:
                    target_items = {}
                    the_items = _dict[entry]
                    if isinstance(the_items, list):
                        for index2, member in enumerate(the_items):
                            target_items[str(index2)] = member
                    items.append((lower_first_word(entry), target_items))
                else:
                    items.append((lower_first_word(entry), _dict[entry]))
                del _dict[entry]

        subpkgs = {}
        try:
            subpkgs_list = _dict['SubPackages']
            del _dict['SubPackages']

            for sub_items in subpkgs_list:
                if "AsWholeName" not in sub_items and package_name != "" and "Name" in sub_items:
                    sub_items["Name"] = package_name + "-" + sub_items["Name"]
                elif "AsWholeName" in sub_items:
                    del sub_items["AsWholeName"]
                if "Name" in sub_items:
                    sub_name = sub_items["Name"]
                    del sub_items["Name"]
                    if sub_name.startswith("%"):
                        sub_name = "\"" + sub_name + "\""
                    subpkgs[sub_name] = self.convert(sub_items, False)
        except Exception as e:
            logger.info(str(e))

        if 'extra' in _dict:
            extra = _dict['extra']
            del _dict['extra']
        else:
            extra = {}
        for _key in ["Build", "Install", "Prep", "Check", "Clean"]:
            if _key in _dict:
                del _dict[_key]
        if "BuildRoot" in _dict:
            buildroot = _dict["BuildRoot"]
            del _dict["BuildRoot"]
            _dict["buildRoot"] = buildroot
        for k, v in _dict.items():
            logger.warn('un-ordered entry: %s' % k)
            items.append((k, v))

        if extra:
            try:
                # clean up empty lines in %files
                files = [s.strip() for s in extra['Files'] if s.strip()]
                if files:
                    extra['files'] = files
                    if "Files" in extra:
                        del extra['Files']
                else:
                    del extra['Files']
                    del extra['files']
            except KeyError:
                pass

            if extra:  # check it again
                items.append(('extra', extra))

        if subpkgs:
            items.append(('subpackage', subpkgs))

        return items


class SpecConvertor(Convertor):
    """ Convertor for SpecBuild ini files """

    def __init__(self):
        sb_cv_table = {
            'BuildRequires': 'BuildRequires',
            'description': 'Description',
            'Requires(post)': 'RequiresPost',
            'Requires(postun)': 'RequiresPostUn',
            'Requires(posttrans)': 'RequiresPostTrans',
            'Requires(pre)': 'RequiresPre',
            'PreRequires': 'RequiresPre',
            'PreReq': 'RequiresPre',
            'Prereq': 'RequiresPre',
            'Requires(preun)': 'RequiresPreUn',
            'Requires(pretrans)': 'RequiresPreTrans',
            'Url': 'URL',
            'install': 'Install',
            'build': 'Build',
            'files': 'Files',
            'clean': 'Clean',
            'pre': 'Pre',
            'preun': 'Preun',
            'post': 'Post',
            'postun': 'Postun',
            'pretrans': 'Pretrans',
            'posttrans': 'Posttrans',
            'check': 'Check',
            'prep': 'Prep',
            'include': 'IncludeSource',
            'Autoreq': 'AutoReq',
            'Autoprov': 'AutoProv',
            'Autoreqprov': 'AutoReqProv',
        }
        Convertor.__init__(self, sb_cv_table)


class YamlWriter:
    """
        The following keys will be generated on the fly based on values from
        SPEC, and transfered to yaml
    """

    def __init__(self, spec_fpath):
        self.path = spec_fpath

    def parse(self):
        """
        解析spec文件的入口
        :return:
        """
        directory = os.path.dirname(self.path)
        if self.path.find(os.path.sep) != -1 and directory != os.path.curdir:
            Chdir(directory).__enter__()
        spec_fname = os.path.basename(self.path)
        out_fpath = spec_fname.replace(".spec", ".yaml")
        """Read the input file"""
        spec_parser = SpecParser()
        try:
            spec_parser.read(spec_fname)
        except SpecFormatError as e:
            logger.warn('<spec2yaml> Spec syntax error: %s' % str(e))
        except SpecUnknowHeaderError as e:
            logger.warn('<spec2yaml> Unknown spec header: %s' % str(e))

        convertor = SpecConvertor()

        """Dump them to spectacle file"""
        dumper = SpectacleDumper(format='yaml', opath=out_fpath, shell_functions=spec_parser.shell_functions,
                                 files=spec_parser.files)
        newspec_fpath = dumper.dump(convertor.convert(spec_parser.cooked_items()))

        logger.info('<spec2yaml> Yaml file %s created' % out_fpath)
        if newspec_fpath:
            bak_spec_fpath = os.path.join('spec.backup')
            logger.info('<spec2yaml> New spec file %s was generated by new yaml file,' % newspec_fpath)
            logger.info('<spec2yaml> and orignal spec file was saved as %s' % bak_spec_fpath)


class SpecParser(object):
    """ Parser of SPEC file of rpm package """

    def __init__(self):
        # runtime variables
        self.items = {}
        self.table = {}
        self.cur_pkg = 'main'
        self.macros = []
        self.shell_functions = {}
        self.keywords_if_config = {}
        self.sources_num_dict = {}
        self.patches_num_dict = {}
        self.files = {}
        self.changelog = ""

    def _switch_subpkg(self, subpkg, create=False, cond_part=None):
        """
        识别子包配置
        :param subpkg:子包名
        :param create:是否需要创建
        :param cond_part:是否带判断
        :return:
        """
        # whether '-n subpkg'?
        if cond_part is None:
            cond_part = []
        wholename = False
        filesinput = ''
        ls = subpkg.split()
        while '-f' in ls:
            this_files_input = ls[ls.index('-f') + 1]
            filesinput += this_files_input + os.linesep
            if "-f" in ls:
                filesinput += " "
            ls.remove("-f")
            if this_files_input != "":
                ls.remove(this_files_input)

        if '-p' in ls:
            cmd_run_tool = ls[ls.index('-p') + 1]
            create = True
        else:
            cmd_run_tool = ""
        if '-n' in ls:
            try:
                origin_name = subpkg
                subpkg = ls[ls.index('-n') + 1]
                if "%name" in subpkg:
                    subpkg = subpkg.replace("%name", self.items["Name"][0])
                if subpkg == self.items["Name"][0]:
                    ls.remove("-n")
                    ls.remove(origin_name)
                    if filesinput != '':
                        if 'FilesInput' not in self.items:
                            self.items['FilesInput'] = filesinput
                        else:
                            self.items['FilesInput'] += filesinput
                    return self.items
                wholename = True
            except IndexError:
                raise SpecFormatError(subpkg)
        else:
            subpkg = ls[0]
            if "%{name}" in subpkg:
                subpkg = subpkg.replace("%name", self.items["Name"][0])

        subpkg_name_dict = {}
        subpkg = subpkg.strip()
        if "SubPackages" in self.items:
            for member_pkg in self.items['SubPackages']:
                if "%if" in member_pkg:
                    subpkg_name_dict[member_pkg.split("%if")[0].strip()] = member_pkg
                else:
                    subpkg_name_dict[member_pkg] = member_pkg
        subpkg_new = 'SubPackages' not in self.items or subpkg not in subpkg_name_dict
        if "SubPackages" in self.items:
            for sub_name in self.items["SubPackages"]:
                if "AsWholeName" not in self.items["SubPackages"][sub_name] and "-n" in ls:
                    if subpkg == self.items["Name"][0] + "-" + sub_name or subpkg == "%{name}-" + sub_name:
                        return self.items["SubPackages"][sub_name]
        if "%if" not in subpkg:
            for member_values in subpkg_name_dict.values():
                if member_values.startswith(subpkg + " %if"):
                    subpkg = member_values
        if subpkg_new and 'SubPackages' in self.items:
            if ls[0] in subpkg_name_dict or ("-n" in ls and ls[ls.index('-n') + 1] in subpkg_name_dict):
                subpkg_new = False

        if subpkg_new and not create:
            logger.warn('un-declared subpkg %s found in spec' % subpkg)
            return None

        if subpkg_new:
            if 'SubPackages' not in self.items:
                self.items['SubPackages'] = {}
            if subpkg not in self.items['SubPackages']:
                if len(cond_part) > 0 and "%if" not in subpkg:
                    subpkg += " " + " ".join(cond_part)
                self.items['SubPackages'][subpkg] = {}
            if wholename:
                self.items['SubPackages'][subpkg]['AsWholeName'] = True
        if filesinput != '':
            self.items['SubPackages'][subpkg]['FilesInput'] = filesinput
        if cmd_run_tool != '':
            self.items['SubPackages'][subpkg]
        # switch
        self.cur_pkg = subpkg
        return self.items['SubPackages'][subpkg]

    def _do_package(self, *args, **kwargs):
        # skip, do nothing
        pass

    def _do_include(self, **kwargs):
        items = kwargs.get("items")
        items["include"].remove("%include")

    def _do_prep(self, **kwargs):
        content = kwargs.get("content")
        logger.info('he following is the content of PREP in original spec, please compare them with the '
                    'generated carefully: \n%s' % content)
        items = kwargs.get("items")
        hdr_line = kwargs.get("hdr_line")
        self._do_extra_scripts(items=items, hdr_line=hdr_line, content=content)

    def _do_build(self, **kwargs):
        """ to handle build script:
            trying to find out the most of the generic cases
        """
        items = kwargs.get("items")
        hdr_line = kwargs.get("hdr_line")
        content = kwargs.get("content")
        self._do_extra_scripts(items=items, hdr_line=hdr_line, content=content)

    def _do_install(self, **kwargs):
        """ to handle install script:
            trying to find out the most of the generic cases
        """
        items = kwargs.get("items")
        hdr_line = kwargs.get("hdr_line")
        content = kwargs.get("content")
        lines = content.splitlines()
        if lines and lines[0].startswith('-'):
            lines.pop(0)

        # try to search %find_lang
        filter_lines = []
        for line in lines:
            if line.startswith('%find_lang'):
                fund_lang = re.compile('^%find_lang\s+(.*)\s*').match(line)
                if fund_lang:
                    continue

            filter_lines.append(line)
        items['install'] = [hdr_line]

    def _do_clean(self, **kwargs):
        items = kwargs.get("items")
        hdr_line = kwargs.get("hdr_line")
        content = kwargs.get("content")
        self._do_extra_scripts(items=items, hdr_line=hdr_line, content=content)

    def _do_check(self, **kwargs):
        items = kwargs.get("items")
        hdr_line = kwargs.get("hdr_line")
        content = kwargs.get("content")
        self._do_extra_scripts(items=items, hdr_line=hdr_line, content=content)

    def _parse_prog_in_opt(self, header):
        """
        解析关键字是否带-p
        :param header:spec的关键字
        :return:
        """
        ls = header.split()
        if '-p' in ls:
            try:
                return ls[ls.index('-p') + 1]
            except IndexError:
                raise SpecFormatError(header)
        else:
            return ''

    def _do_extra_scripts(self, **kwargs):
        items = kwargs.get("items")
        hdr_line = kwargs.get("hdr_line")
        content = kwargs.get("content")
        section = hdr_line.split()[0][1:]
        items['extra'][section] = content.strip().splitlines()
        inline_prog = self._parse_prog_in_opt(hdr_line)
        if inline_prog:
            items['extra'][section].insert(0, inline_prog)

    def _do_pre(self, **kwargs):
        items = kwargs.get("items")
        hdr_line = kwargs.get("hdr_line") if "hdr_line" in kwargs else ""
        value = kwargs.get("v") if "v" in kwargs else ""
        self._do_extra_scripts(items=items, hdr_line=hdr_line, content=value)

    def _do_preun(self, **kwargs):
        items = kwargs.get("items")
        hdr_line = kwargs.get("hdr_line")
        content = kwargs.get("content")
        self._do_extra_scripts(items=items, hdr_line=hdr_line, content=content)

    def _do_post(self, **kwargs):
        items = kwargs.get("items")
        hdr_line = kwargs.get("hdr_line")
        content = kwargs.get("content")
        self._do_extra_scripts(items=items, hdr_line=hdr_line, content=content)

    def _do_postun(self, **kwargs):
        items = kwargs.get("items")
        hdr_line = kwargs.get("hdr_line")
        content = kwargs.get("content")
        self._do_extra_scripts(items=items, hdr_line=hdr_line, content=content)

    def _do_pretrans(self, **kwargs):
        items = kwargs.get("items")
        hdr_line = kwargs.get("hdr_line")
        content = kwargs.get("content")
        self._do_extra_scripts(items=items, hdr_line=hdr_line, content=content)

    def _do_posttrans(self, **kwargs):
        items = kwargs.get("items")
        hdr_line = kwargs.get("hdr_line")
        content = kwargs.get("content")
        self._do_extra_scripts(items=items, hdr_line=hdr_line, content=content)

    def _do_changelog(self, **kwargs):
        hdr_line = kwargs.get("hdr_line")
        logger.warn('Please move changelog in %changelog to *.changes file.' + hdr_line)

    def _remove_attrs(self, files):
        # try to remove duplicate '%defattr' in files list
        dup = '%defattr(-,root,root,-)'
        dup2 = '%defattr(-,root,root)'
        if dup in files:
            files.remove(dup)
        if dup2 in files:
            files.remove(dup2)

    def _do_files(self, **kwargs):
        items = kwargs.get("items")
        content = kwargs.get("content")
        files = list(map(str.strip, content.strip().splitlines()))
        if files:
            # skip option line
            if files[0].startswith('-'):
                files.pop(0)
            self._remove_attrs(files)
        items['extra']['Files'] = files

    def _do_description(self, **kwargs):
        items = kwargs.get("items")
        content = kwargs.get("content")
        items['Description'] = content.strip()

    def add_special_keywords(self, _items, line, keyword):
        if keyword.lower() in line:
            line = line.replace("%" + keyword.lower(), "").strip()
            if keyword in _items:
                _items[keyword].append(line)
            else:
                _items[keyword] = [line]

    def parse_case_spell(self, word):
        """
        解析关键字的拼写问题，目的是兼容spec大小写不敏感的特性
        :param word:关键字
        :return:
        """
        if not word:
            return False, word
        temp_keys_list = []
        for _key in self.items.keys():
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

    def find_quotes_from_words(self, words):
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

    def update_keywords(self, keywords, value=""):
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

    def resolve_special_macros_config(self, line):
        """
        处理特殊的宏配置
        :param line:
        :return:
        """
        if line == "%package_help":
            if "SubPackages" in self.items:
                self.items["SubPackages"]["help"] = {"Summary": ["Documents for %{name}"],
                                                     "BuildArch": ["noarch"],
                                                     "Requires": ["man info"],
                                                     "Description":
                                                         "Man pages and other related documents for %{name}."}
            else:
                self.items["SubPackages"] = {"help": {"Summary": ["Documents for %{name}"],
                                                      "BuildArch": ["noarch"],
                                                      "Requires": ["man info"],
                                                      "Description":
                                                          "Man pages and other related documents for %{name}."}}

    def modify_source_number(self, line):
        """
        修改%{SOURCE}序号，与新的Source对齐
        :param line:
        :return:
        """
        if re.search("%\{SOURCE\d*\}", line) is not None:
            source_list = re.findall("%{SOURCE\d*}", line)
            for s in source_list:
                key = s.lstrip("%{").rstrip("}")
                source = key[0:6]
                num = re.sub("^0+", "", key[6:])
                if num == "":
                    num = "0"
                key = source + num
                val = "%{" + self.sources_num_dict[key] + "}"
                line = line.replace(s, val)
        elif re.search("%SOURCE\d*", line) is not None:
            source_list = re.findall("%SOURCE\d*", line)
            for s in source_list:
                key = s.lstrip("%")
                source = key[0:6]
                num = re.sub("^0+", "", key[6:])
                if num == "":
                    num = "0"
                key = source + num
                val = "%" + self.sources_num_dict[key]
                line = line.replace(s, val)
        elif re.search("%\{S:\d*\}", line) is not None:
            source_list = re.findall("%\{S:\d*\}", line)
            for s in source_list:
                key = s.lstrip("%{").rstrip("}")
                key = key.replace("S:", "SOURCE")
                source = key[0:6]
                num = re.sub("^0+", "", key[6:])
                if num == "":
                    num = "0"
                key = source + num
                val = "%{" + self.sources_num_dict[key] + "}"
                line = line.replace(s, val)
        return line

    def modify_patch_serial_number(self, line):
        """
        修改补丁序号，从0开始
        :param line:
        :return:
        """
        if re.search("%patch\d*", line) is not None:
            patch_list = re.findall("^%patch\d*", line)
            key = patch_list[0]
            patch = key[1:6]
            num = re.sub("^0+", "", key[6:])
            if num == "":
                num = "0"
            key = patch + num
            val = "%" + self.patches_num_dict[key]
            line = line.replace(patch_list[0], val)
        elif re.search("%\{PATCH\d*\}", line) is not None:
            patch_list = re.findall("%\{PATCH\d*\}", line)
            for p in patch_list:
                key = p.lstrip("%{").rstrip("}").lower()
                patch = key[0:5]
                num = re.sub("^0+", "", key[5:])
                if num == "":
                    num = "0"
                key = patch + num
                val = "%{" + self.patches_num_dict[key].upper() + "}"
                line = line.replace(p, val)
        return line

    def resolve_inner_quotes(self, _line):
        """"""
        can_trans = not ((_line.startswith("\"") and _line.endswith("\"")) or (
                _line.startswith("\'") and _line.endswith("\'")))
        if can_trans and ("\"" in _line and "\\\"" not in _line):
            _line = _line.replace("\"", "\\\"")
        return _line

    def revise_macros(self):
        macros = self.macros
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
                if 'Version' in self.items:
                    line = re.sub("%\{version\}", self.items['Version'][0], line)
                if 'Name' in self.items:
                    line = re.sub("%\{name\}", self.items['Name'][0], line)
            macros[i] = line

    def read(self, filename):
        """
        读取所有的文件内容和关键字并保存数据
        :param filename:
        :return:
        """
        comment = re.compile('^#.*')
        cond_if = re.compile('^%if.*')
        cond_else = re.compile('^%else.*')
        cond_endif = re.compile('^%endif.*')
        directive = re.compile('^([\w()]+)[ \t]*:[ \t]*(.*)')
        header_re = re.compile('^%(' + '|'.join(HEADERS) + ')\s*(.*)')
        macros_re = re.compile('^%.*')
        single_re = re.compile('^(' + '|'.join(SINGLES) + ')\s*(.*)')
        require_re = re.compile('^(' + '|'.join(REQUIRES) + ')\s*(.*)')

        state = ST_MAIN
        items = self.items
        header = ""
        if_cond_part = []
        else_cond_part = []
        # 用于多行模式向主包模式转换时判断语句的存放
        _if_cond_part = []
        _else_cond_part = []
        else_status = False  # 用于配置信息else状态的记录
        _else_status = False  # 用于逻辑信息else状态的记录
        subpackages_model = False
        while_next = False
        while_next_true = 0
        keywords_type = ""  # 用于多行字段的切换
        last_line = ""  # be used to resolve Line breaks '\'
        source_number = 0
        patch_number = 0
        need_left_strip = True
        cat_eof_model = False
        unclosed_brackets = 0
        in_package_help = False

        def get_line_suffix():
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
        for line in open(filename):
            if unclosed_brackets < 0:
                unclosed_brackets = 0
            if cat_eof_model and header:
                items[header] += line
                if line == "EOF" + os.linesep:
                    cat_eof_model = False
                continue
            real_key = ""
            if last_line != "":
                line = last_line + line
            # preprocessed
            if need_left_strip:
                line = line.strip()
            else:
                if re.match("\s*%if", line):
                    line = line.strip()
                else:
                    line = line.rstrip()
                need_left_strip = True
            if line in MACROS_KEYWORDS:
                self.resolve_special_macros_config(line)
                if line == MACROS_KEYWORDS[0]:
                    in_package_help = True
                    subpackages_model = True
                continue
            if comment.match(line):
                # skip comment line and empty line
                if len(_if_cond_part) == 0:
                    continue
            elif state == ST_MAIN and not line:
                continue
            if header == "description" and line == "%package_description":
                items[header] += "%package_description" + os.linesep
                continue
            if line.endswith("\\"):
                need_left_strip = False
            available_key = header_re.match(line) or single_re.match(line) or require_re.match(line)  # parse key spell
            if available_key:
                if state == ST_INLINE and header in SHELL_KEYWORDS:
                    if re.match("%\w+", line) is not None:
                        temp_available_key = line.strip().lstrip("%").split()[0]
                        available_key = temp_available_key in SHELL_KEYWORDS + ["package"]
                unclosed_brackets = 0
                if in_package_help:
                    if "Summary" in line or "BuildArch" in line or "Requires" in line or "description" in line or line not in SHELL_KEYWORDS:
                        in_package_help = False
                        items = self.items
            if unclosed_brackets != 0:
                brackets_left_list = re.findall("\{\w*|\(\w*", line)
                brackets_right_list = re.findall("\}\w*|\)\w*", line)
                left_character = re.findall("\\\\\\(", line)
                left_count = len(brackets_left_list) - len(left_character)
                right_character = re.findall("\\\\\\)", line)
                right_count = len(brackets_right_list) - len(right_character)
                unclosed_brackets = left_count + unclosed_brackets - right_count
                pre_macro = self.macros.pop()
                pre_macro += line
                if unclosed_brackets == 0:
                    if len(_if_cond_part) > 0:
                        if_cond_part += _if_cond_part
                        state = ST_MAIN
                        _if_cond_part.clear()
                    if len(_else_cond_part) > 0:
                        else_cond_part += _else_cond_part
                        state = ST_MAIN
                        _else_cond_part.clear()
                    while_next_true = 0
                    line_suffix = get_line_suffix()
                    self.macros.append(pre_macro + line_suffix)
                else:
                    self.macros.append(pre_macro + "{os.linesep}")
                continue
            if re.match("(%define)|(%global)|(%bcond_with)|(%\{\!\?)|(%undefine)|(%\{\?)|(%\{expand:\s*%)", line) is not None:
                if header in SHELL_KEYWORDS + ["files"] and state == ST_INLINE:
                    pass
                else:
                    if line.endswith("\\") and not line.endswith("\\\\"):
                        last_line = line + "\\{os.linesep}"
                        continue
                    elif line.endswith("||") or line.endswith("&&"):
                        last_line = line + "{os.linesep}"
                        continue
                    elif line.endswith("\\\\\\"):
                        last_line = line + "\\\\\\{os.linesep}"
                        continue
                    else:
                        last_line = ""
                    if "{" in line or "(" in line:
                        if len(line.split()) == 3 and (line.split()[2] == "(" or line.split()[2] == ")"):
                            pass
                        else:
                            brackets_left_list = re.findall("\{\w*|\(\w*", line)
                            brackets_right_list = re.findall("\}\w*|\)\w*", line)
                            left_character = re.findall("\\\\\\(", line)
                            left_count = len(brackets_left_list) - len(left_character)
                            right_character = re.findall("\\\\\\)", line)
                            right_count = len(brackets_right_list) - len(right_character)
                            if left_count != right_count:
                                unclosed_brackets = left_count - right_count
                    if unclosed_brackets == 0:
                        if len(_if_cond_part) > 0:
                            if_cond_part += _if_cond_part
                            state = ST_MAIN
                            _if_cond_part.clear()
                            if while_next_true:
                                while_next_true = 0
                        if len(_else_cond_part) > 0:
                            else_cond_part += _else_cond_part
                            state = ST_MAIN
                            _else_cond_part.clear()
                            if while_next_true:
                                while_next_true = 0
                        line_suffix = get_line_suffix()
                        self.macros.append(line + line_suffix)
                        state = ST_MAIN
                    else:
                        self.macros.append(line + "{os.linesep}")
                        continue
            if not available_key:
                if ":" in line:
                    first_key = line.split(":")[0].strip()
                    is_available, real_key = self.parse_case_spell(first_key)
                    if not is_available:
                        temp_line = line.replace(line.split(":")[0], line.split(":")[0].capitalize().strip())
                        available_key = header_re.match(temp_line) or single_re.match(
                            temp_line) or require_re.match(temp_line)
                    else:
                        header = real_key
            if available_key:
                if header_re.match(line):
                    if "%package" in line:
                        subpackages_model = True
                    state = ST_INLINE
                    if subpackages_model:
                        state = ST_MAIN
                        if not while_next and header in SHELL_KEYWORDS + ["description", "files"]:
                            if _if_cond_part:
                                if_count = len(re.findall("%if", items[header]))
                                endif_count = len(re.findall("%endif", items[header]))
                                if if_count > endif_count or header == "files":
                                    items[header] += ("%endif" + os.linesep) * len(_if_cond_part)
                                elif if_count == endif_count:
                                    _if_cond_part.pop()
                        if len(_if_cond_part) > 0:
                            if_cond_part += _if_cond_part
                            _if_cond_part.clear()
                            if while_next_true:
                                while_next_true = 0
                        if len(_else_cond_part) > 0:
                            else_cond_part += _else_cond_part
                            _else_cond_part.clear()
                            if while_next_true:
                                while_next_true = 0
                elif single_re.match(line):
                    if single_re.match(line).group(1) not in items:
                        state = ST_MAIN
                        line = self.resolve_inner_quotes(line)
                elif require_re.match(line):
                    if require_re.match(line).group(1) not in items:
                        state = ST_MAIN

            if state == ST_INLINE:
                if header_re.match(line):
                    state = ST_INLINE
                    keywords_type = "lines"
                    header = cur_block = header_re.match(line).group(1)
                    if header in line and header not in OBS_LINES_KEYWORDS and header != "package" and len(line.split()) > 0:
                        line = line.replace(header + " ", header + os.linesep)
                    if cur_block == "package":
                        # change model from INLINE into subpackages
                        state == ST_MAIN
                        subpackages_model = True
                    elif cur_block.startswith("files"):
                        header = cur_block = "files"
                        items[cur_block] = line + os.linesep
                        opt = line.split()
                        if len(opt) > 1:
                            files_input = opt[1:]
                            files_input_value = ""
                            while '-f' in files_input:
                                this_files_input = files_input[files_input.index('-f') + 1].strip()
                                files_input_value += this_files_input + os.linesep
                                files_input.remove("-f")
                                opt.remove("-f")
                                if this_files_input != "":
                                    files_input.remove(this_files_input)
                                    opt.remove(this_files_input)
                            if files_input_value != "":
                                items['FilesInput'] = files_input_value
                            if len(opt) == 1 and opt[0] == "%files":
                                if self.items != items and "files" not in self.items:
                                    items = self.items
                                    items["files"] = line + os.linesep
                        elif len(opt) == 1 and opt[0] == "%files":
                            if self.items != items:
                                items = self.items
                            if "files" not in items:
                                items["files"] = ""
                    else:
                        if cur_block in OBS_LINES_KEYWORDS:
                            line += os.linesep
                        if cur_block not in items.keys():
                            if len(_if_cond_part) > 0:
                                while_next_true = 0
                                if_cond_part += _if_cond_part
                                _if_cond_part.clear()
                            if len(_else_cond_part) > 0:
                                while_next_true = 0
                                else_cond_part += _else_cond_part
                                _else_cond_part.clear()
                            if if_cond_part and cur_block not in self.keywords_if_config:
                                self.keywords_if_config[header] = [os.linesep.join(if_cond_part)]
                            items[cur_block] = line + os.linesep
                        else:
                            items[cur_block] += line + os.linesep
                        continue
                # change model from INLINE into MAIN
                elif single_re.match(line) and single_re.match(line).group(1) not in items:
                    state = ST_MAIN
                    keywords_type = "single"
                    line_suffix = get_line_suffix()
                    cur_block = single_re.match(line).group(0)
                    line = self.resolve_inner_quotes(line)
                    items[cur_block] = line + os.linesep + line_suffix
                    continue
                elif require_re.match(line) and require_re.match(line).group(1) not in items:
                    state = ST_MAIN
                    keywords_type = "list"
                    cur_block = require_re.match(line).group(0)
                    if ":" in line:
                        member_content = ":".join(line.split(':')[1:])
                    else:
                        logger.warn("this line missing the colon: " + line)
                        continue
                    if cur_block not in items.keys():
                        items[cur_block] = [member_content]
                    else:
                        items[cur_block].append(member_content)
                    continue
                elif cond_if.match(line):
                    _if_cond_part.append(line)
                    if _else_status:
                        _else_status = False
                        if while_next:  # inline模式下当else过后紧接着又是if时，else加到if前面再进入下一行
                            _if_cond_part[-1] = _else_cond_part[-1] + os.linesep + _if_cond_part[-1]
                    while_next = True
                    while_next_true += 1
                elif cond_else.match(line) or cond_endif.match(line):
                    if cond_else.match(line):
                        _else_cond_part.append(line)
                        if while_next and not _else_status:
                            _else_cond_part[-1] = _if_cond_part[-1] + os.linesep + _else_cond_part[-1]
                        _else_status = True
                        while_next = True
                        while_next_true += 1
                    if len(_if_cond_part) == 0 and len(if_cond_part) > 0:
                        state = ST_MAIN
                    elif len(_if_cond_part) > 0 and cond_endif.match(line) and len(_else_cond_part) == 0:
                        _if_cond_part.pop()
                        items[header] += line + os.linesep
                        while_next = False
                        while_next_true = 0
                    elif len(_else_cond_part) > 0 and cond_endif.match(line):
                        _if_cond_part.pop()
                        _else_cond_part.pop()
                        items[header] += line + os.linesep
                        while_next = False
                        while_next_true = 0
                else:
                    if keywords_type == "lines":
                        if re.search("cat\s*>\s*.*\s*<<\s*EOF", line) is not None:
                            cat_eof_model = True
                        if len(_if_cond_part) > 0 and while_next and len(_else_cond_part) == 0:
                            if not line:
                                continue
                            items[header] += os.linesep.join(_if_cond_part[-while_next_true:]) + os.linesep
                            while_next = False
                            while_next_true = 0
                        elif len(_if_cond_part) > 0 and while_next and len(_else_cond_part) > 0 and while_next_true > 1:
                            if not line:
                                continue
                            last_line_cond_part = _else_cond_part[-1] if _else_status else _if_cond_part[-1]
                            items[header] += last_line_cond_part + os.linesep
                            while_next = False
                            while_next_true = 0
                        elif len(_if_cond_part) > 0 and while_next and len(_else_cond_part) > 0 and \
                                while_next_true == 1 and _else_status:
                            items[header] += "%else" + os.linesep
                            while_next = False
                            while_next_true = 0
                        elif len(_if_cond_part) > 0 and while_next and len(_else_cond_part) > 0 and \
                                while_next_true == 1 and not _else_status:
                            items[header] += _if_cond_part[-1] + os.linesep
                            while_next = False
                            while_next_true = 0
                        if items is None:
                            items = {}
                        if header not in items:
                            items[header] = ""
                        if re.match(r"%patch\d*", line) is not None or re.search("%\{PATCH\d*\}", line) is not None:
                            line = self.modify_patch_serial_number(line)
                        if re.search(r"%\{SOURCE\d*\}", line) is not None or re.search("%SOURCE\d*", line) is not None \
                                or re.search("%\{S:\d*\}", line) is not None:
                            line = self.modify_source_number(line)
                        if header == "prep" and line.startswith("%setup"):
                            if re.search("-b\d+", line):
                                line = line.replace("-b", "-b ")
                            if re.search("\d+", line):
                                setup_list = line.split()
                                new_setup = ""
                                for s in setup_list:
                                    if re.match("^\d+", s):
                                        num = re.sub("^0+", "", s)
                                        if num == "":
                                            num = "0"
                                        val = self.sources_num_dict["SOURCE" + num]
                                        s = val[6:]
                                    new_setup = new_setup + s + " "
                                line = new_setup.strip()
                        if type(items[header]) == str:
                            while_next = False
                            items[header] += line + os.linesep
                    elif keywords_type == "single":
                        logger.warn("single at error=================>" + line)
                    elif keywords_type == "list":
                        logger.warn("list at error=================>" + line)

            if state == ST_MAIN:
                line = line.strip()
                if header_re.match(line):
                    state = ST_INLINE
                    keywords_type = "lines"
                    header = cur_block = header_re.match(line).group(1)
                    if cur_block == "package":
                        # change model from MAIN into subpackages
                        subpackages_model = True
                    elif not subpackages_model:
                        if cur_block not in items.keys():
                            items[cur_block] = line
                        else:
                            items[cur_block] += line
                        if if_cond_part:
                            self.keywords_if_config[header] = [os.linesep.join(if_cond_part)]
                        continue
                if cond_if.match(line):
                    if_cond_part.append(line)
                elif cond_else.match(line):
                    else_cond_part.append(line)
                    else_status = True
                elif cond_endif.match(line):
                    if_cond_part.pop()
                    if else_status:
                        else_cond_part.pop()
                        if len(else_cond_part) == 0:
                            else_status = False
                line_suffix = get_line_suffix()
                directive_match = directive.match(line)
                header_match = header_re.match(line) if not directive_match else None
                if directive_match:
                    key = directive_match.group(1) if real_key == "" else real_key
                    if key.lower().startswith("source"):
                        if len(else_cond_part) == 0:
                            new_key = key.upper()
                            source = new_key[0:6]
                            num = re.sub("^0+", "", new_key[6:])
                            if num == "":
                                num = "0"
                            new_key = source + num
                            self.sources_num_dict[new_key] = new_key[0:6] + str(source_number)
                            source_number += 1
                    if key.lower().startswith("patch"):
                        new_key = key.lower()
                        patch = new_key[0:5]
                        num = re.sub("^0+", "", new_key[5:])
                        if num == "":
                            num = "0"
                        new_key = patch + num
                        self.patches_num_dict[new_key] = new_key[0:5] + str(patch_number)
                        patch_number += 1
                    val = directive_match.group(2)
                    key = self.update_keywords(key, val)
                    case_spell_result = self.parse_case_spell(key)
                    key = key.replace("requires", "Requires") if case_spell_result else key
                    if key not in SINGLES and key not in REQUIRES and key not in ORDER_ENTRIES and key not in SKIPS:
                        may_parse = not (self.parse_case_spell(key))
                        if not may_parse:
                            key = key.capitalize()

                    # special case for Source and Patch
                    key = self.update_keywords(key)
                    val = self.find_quotes_from_words(val + line_suffix)
                    if key not in items:
                        items[key] = [val]
                    else:
                        items[key].append(val)

                elif header_match:
                    header = header_match.group(1)
                    opt = header_match.group(2)
                    if if_cond_part and header in SHELL_KEYWORDS and opt is not None:  # key外部的判断语句
                        if_cond_part[0] = if_cond_part[0].replace(os.linesep, "{" + header + "}" + os.linesep)
                    if header not in HEADERS:
                        raise SpecUnknowHeaderError(state, self.cur_pkg, header)
                    if header == 'package':
                        subpackages_model = True
                        state = ST_MAIN
                        if not opt:
                            raise SpecFormatError(line)
                        if if_cond_part:
                            items = self._switch_subpkg(opt, True, if_cond_part)
                        else:
                            items = self._switch_subpkg(opt, True, if_cond_part)
                    else:
                        # inline sections of other headers
                        state = ST_INLINE
                        if "-p" in opt.split():
                            line = line.replace(" -p ", os.linesep + "-p ")
                        sub_files = False
                        if "SubPackages" in self.items:
                            for sub_name in self.items["SubPackages"]:
                                if "AsWholeName" not in self.items["SubPackages"][sub_name] and "-n" in opt.split():
                                    sub_name = self.items["Name"][0] + "-" + sub_name
                                if sub_name.replace("%{name}", self.items["Name"][0]) in opt.replace(
                                        "%{name}", self.items["Name"][0]) and header == "files":
                                    if sub_name == "file":
                                        if len(line.split()) > 1 and line.split()[1] == "file":
                                            sub_files = True
                                    else:
                                        sub_files = True
                                        break
                        if opt and (not opt.startswith('-') or '-n' in opt) or sub_files:
                            # section with sub-pkg specified
                            items = self._switch_subpkg(opt, cond_part=if_cond_part)
                            ls = opt.split()
                            if "-n" in ls:
                                sub_pkg = ls[ls.index('-n') + 1]
                                if sub_pkg == "%{name}" or sub_pkg == filename.replace(".spec", ""):
                                    line = line.replace(" -n ", "").replace(sub_pkg, "")
                            if len(if_cond_part) > 0:
                                if type(items) is dict and "FilesJudgement" not in items.keys():
                                    items["FilesJudgement"] = copy.deepcopy(if_cond_part)
                        else:
                            # for 'main' package
                            # 'InputFile' in 'main' package
                            items = self.items
                            if opt and '-f ' in opt:
                                files_input = opt.split("-f ")
                                files_input_value = ""
                                for f in files_input:
                                    if f.strip() == "":
                                        continue
                                    files_input_value = files_input_value + f.strip() + os.linesep
                                if "FilesInput" not in items:
                                    items["FilesInput"] = files_input_value
                                else:
                                    items["FilesInput"] += files_input_value

                        if items:
                            if header not in self.keywords_if_config:
                                if if_cond_part:
                                    self.keywords_if_config[header] = [os.linesep.join(if_cond_part)]
                            cur_block = header
                            if cur_block not in items:
                                items[cur_block] = line + os.linesep
        self.revise_macros()
        self.collation_original_data(self.items, filename)

    def collation_original_data(self, original_data: dict, file_name: str):
        """
        整理原始数据
        :param original_data:
        :param file_name:
        :return:
        """
        if "changelog" in original_data:
            self.changelog = original_data["changelog"]
            with open("changelog.md", "w") as f:
                self.changelog = os.linesep.join(self.changelog.split(os.linesep)[1:])
                f.write(self.changelog)
        if "Release" in original_data.keys():
            if type(original_data["Release"]) is list and len(original_data["Release"]) == 1:
                original_data["Release"] = original_data["Release"][0]
        if "Summary" in original_data.keys() and len(original_data["Summary"]) == 1 and \
                original_data["Summary"][0].startswith("`"):
            original_data["Summary"][0] = "_" + original_data["Summary"][0]
        target_data = copy.deepcopy(original_data)
        if "Version" in original_data.keys() and original_data["Version"]:
            if type(original_data["Version"]) == str and original_data["Version"].startswith("%"):
                target_data = self.add_quotation_from_member("Version", target_items=target_data)
            elif type(original_data["Version"]) == list and original_data["Version"][0].startswith("%"):
                target_data = self.add_quotation_from_member("Version", target_items=target_data)
        for _key, _value in original_data.items():
            if _key in NEED_QUOTATION_KEYWORDS:
                target_data = self.add_quotation_from_member(_key, target_items=target_data)
            if _key in SHELL_KEYWORDS:
                if _key == "prep" and _value == "%prep" + os.linesep + "%autosetup -n %{name}-%{version} -p1":
                    continue
                self.divide_into_shell(_key, target_data[_key])
                if type(original_data[_key]) == str:
                    # target_data[_key] = shell_name
                    del target_data[_key]
                elif type(original_data[_key]) == list:
                    # target_data[_key] = [shell_name]
                    del target_data[_key]
                continue
            if _key == "files" and "Name" in original_data:
                files_judgement = ""
                if "FilesJudgement" in original_data:
                    files_judgement += " ".join(original_data["FilesJudgement"])
                    del target_data["FilesJudgement"]
                file_key = original_data["Name"]
                if "%if" in file_key:
                    files_judgement += " rpmWhen %if" + " rpmWhen %if".join(file_key.split(" %if")[1:])
                    main_file_key = "files" + files_judgement
                else:
                    main_file_key = "files"
                self.files[main_file_key] = original_data["files"]
                del target_data["files"]
            if _key == "SubPackages":
                for sub_member_name, sub_member_dict in original_data["SubPackages"].items():
                    whole_name = "AsWholeName" in original_data["SubPackages"][sub_member_name].keys()
                    sub_files_judgement = ""
                    if "FilesJudgement" in sub_member_dict:
                        temp_sub_member_list = copy.deepcopy(sub_member_dict["FilesJudgement"])
                        for judgement_words in temp_sub_member_list:
                            if judgement_words in sub_member_name:
                                sub_member_dict["FilesJudgement"].remove(judgement_words)
                        if sub_member_dict["FilesJudgement"]:
                            sub_files_judgement += " rpmWhen " + " rpmWhen ".join(sub_member_dict["FilesJudgement"])
                        del target_data["SubPackages"][sub_member_name]["FilesJudgement"]
                    if "%if" in sub_member_name:
                        target_data = self.clear_sub_extra_judge(sub_member_name, target_items=target_data)
                    sub_file_name = target_data["Name"][0] + "-" + sub_member_name.split("%if")[0].strip() \
                        if not whole_name else sub_member_name.strip()
                    for member_key, member_value in sub_member_dict.items():
                        if member_key == "files":
                            self.files["subpackage." + sub_file_name + ".files" + sub_files_judgement] = member_value
                            del target_data["SubPackages"][sub_member_name]["files"]
                        if member_key == "Summary" and len(member_value) == 1 and member_value[0].startswith("`"):
                            target_data["SubPackages"][sub_member_name][member_key] = ["_" + member_value[0]]
                        if member_key in NEED_QUOTATION_KEYWORDS:
                            target_data = self.add_quotation_from_member(member_key, sub_name=sub_member_name,
                                                                         target_items=target_data)
                        if member_key in SHELL_KEYWORDS:
                            self.divide_into_shell(member_key, target_data["SubPackages"][
                                sub_member_name][member_key], sub_name=sub_member_name.split()[0].strip(),
                                                   whole=whole_name, main_name=original_data["Name"][0])
                            if type(sub_member_dict[member_key]) == str:
                                # target_data["SubPackages"][sub_member_name][member_key] = shell_name
                                del target_data["SubPackages"][sub_member_name][member_key]
                            elif type(sub_member_dict[member_key]) == list:
                                # target_data["SubPackages"][sub_member_name][member_key] = [shell_name]
                                del target_data["SubPackages"][sub_member_name][member_key]
                    if "%if" in sub_member_name:
                        temp_sub_dict = target_data["SubPackages"][sub_member_name]
                        del target_data["SubPackages"][sub_member_name]
                        target_data["SubPackages"][sub_member_name.replace("%if", "rpmWhen %if")] = temp_sub_dict
        self.items = target_data

    def add_quotation_from_member(self, keywords, sub_name=None, target_items=None):
        """
        list类型的子项统一增加引号
        :param keywords:
        :param sub_name:
        :param target_items:
        :return:
        """
        if target_items is None:
            target_items = self.items
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

    def divide_into_shell(self, keywords, value: str, sub_name=None, whole=False, main_name=None):
        """
        分解到shell中，当前shell的内容存放在变量中
        :param keywords:
        :param value:
        :param sub_name:
        :param whole:False代表子包不带-n，True代表子包带-n
        :param main_name:主包名
        :return:
        """
        if " -n " in value and not whole:
            value = value.split(os.linesep)[0].replace("-n %{name}-", "") + os.linesep + os.linesep.join(
                value.split(os.linesep)[1:])
        value = value.split(os.linesep)[0].replace(" -n", "") + os.linesep + os.linesep.join(value.split(os.linesep)[1:])
        original_sub_name = sub_name
        if sub_name is not None and not whole:
            sub_name = main_name + "-" + sub_name
        if value.startswith("%" + keywords + os.linesep):  # 主包shell语句分解
            function_context = value.replace("%" + keywords + os.linesep, "", 1)
            self.shell_functions[keywords] = function_context
            return True
        elif (sub_name is not None) and value.startswith("%" + keywords + " " + original_sub_name + os.linesep):  # 子包shell语句分解
            function_context = value.lstrip("%" + original_sub_name + " " + keywords).strip(os.linesep) + os.linesep
            self.shell_functions[keywords + ":" + sub_name] = function_context
            return True
        else:
            if sub_name is not None and " -n " in value:
                return False

    def cooked_items(self):
        """
        转换所收集数据的结构的入口
        :return: items
        """
        return self._cook_items('main', self.items, self.keywords_if_config)

    def _cook_items(self, pkg_name, items, keywords_if_config=None, is_sub=False, ):
        """
        转换数据结构
        :param pkg_name:包名称
        :param items:包含所有数据的字典
        :param keywords_if_config:关键字的if配置
        :param is_sub:是否是子包
        :return:经过整理的items
        """
        # pattern of macros
        macro_re = re.compile('%{(\w+)}')

        ck_items = {'extra': {}}
        if pkg_name != 'main':
            ck_items['Name'] = pkg_name

        for k, v in items.items():
            # if k in SKIPS or k in HEADERS or k == 'SubPackages':
            if k in SHELL_KEYWORDS and is_sub:
                ck_items[k] = [v]
                continue
            if k in HEADERS or k == 'SubPackages':
                if k in SHELL_KEYWORDS:
                    ck_items[k] = [v]
                    if k in keywords_if_config and not is_sub:
                        for cond_part in keywords_if_config[k]:
                            quotation = "'" if "\'" not in cond_part else "\""
                            if "\'" in cond_part and "\"" in cond_part:
                                cond_part = cond_part.replace("\"", "\\\"")
                            ck_items[k].append(quotation + cond_part + quotation)
                continue

            if self.table:
                # macro replacing
                nv = []
                for vi in v:
                    while macro_re.search(vi):
                        nvi = vi
                        for m in macro_re.finditer(vi):
                            macro, name = m.group(0, 1)
                            if name in self.table:
                                nvi = nvi.replace(macro, self.table[name])
                        if vi == nvi:
                            break  # break to exit 'while' loop
                        vi = nvi
                    # now nvi is the replaced string
                    nv.append(vi)
                v = nv

            if k in SINGLES:
                ck_items[k] = v[0]
            else:
                ck_items[k] = v

        # handle all sectinos with header, IN-ORDER
        for hdr in HEADERS:
            if hdr in items:
                routine = getattr(self, '_do_' + hdr)
                hdr_line, drop, content = items[hdr].partition(os.linesep)
                if hdr != 'description' and hdr != 'changelog' and content:

                    if hdr in ['build', 'install', 'prep', 'pre', 'post', 'preun', 'postun', 'pretrans', 'posttrans',
                               'check', 'files', 'clean']:
                        content_list = content
                    else:
                        content_list = content.split(os.linesep)
                        while '' in content_list:
                            content_list.remove('')
                    ck_items[hdr] = content_list
                routine(items=ck_items, pkg_name=pkg_name, hdr_line=hdr_line, content=content)
        if pkg_name != 'main':
            # shortcut for subpkg
            return ck_items

        # handle subpackages
        if 'SubPackages' in items:
            ck_items['SubPackages'] = []
            for sub, sub_items in items['SubPackages'].items():
                ck_items['SubPackages'].append(self._cook_items(sub, sub_items, is_sub=True))

        # check must-have keys
        for key, default in MUSTHAVE.items():
            if key not in ck_items:
                ck_items[key] = default

        # check for global macros
        if self.macros:
            ck_items['extra']['macros'] = self.macros

        return ck_items

    def clear_sub_extra_judge(self, sub_name, target_items=None):
        """
        清理子包多余的判断语句
        :param sub_name:
        :param target_items:
        :return:
        """
        if target_items is None:
            target_items = self.items
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
