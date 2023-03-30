import os
import sys
import copy
from openEulerTransition.logs.log import logger
from openEulerTransition.actions.utils.file_operate import Chdir
from openEulerTransition.actions.utils.data_operate import *
from openEulerTransition.configure.spec_config import *
from openEulerTransition.configure.yaml_config import *

# state definition of parser
(
    ST_MAIN,
    ST_INLINE,
    ST_SUBPKG,
) = list(range(3))


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

    def __init__(self, file_type='yaml', opath=None, shell_functions=None, files=None):
        self.format = file_type
        self.opath = opath
        self.shell_functions = shell_functions
        self.files = files
        self.spec_extra = {}

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
            if f_phase != sys.stdout:
                f_phase.write("#!/usr/bin/env bash\n\n")
                lua_file = LuaFile()
                for function_name, function_text in script_data.items():
                    if function_name in ["install", "prep", "build", "clean", "check", "configure"]:
                        lua_file = add_context(function_name, function_text, f_phase, lua_file)
            if f_runtime_phase != sys.stdout:
                f_runtime_phase.write("#!/usr/bin/env bash\n\n")
                lua_runtime_file = LuaFile()
                for function_name, function_text in script_data.items():
                    if function_name not in ["install", "prep", "build", "clean", "check", "configure"]:
                        lua_runtime_file = add_context(function_name, function_text, f_runtime_phase, lua_runtime_file)
        if f_files and files_data:
            for file_member_key, file_member_value in files_data.items():
                f_files.write(file_member_key + ": |" + os.linesep)
                file_member_value = file_member_value.lstrip("%files")
                temp_text_list = file_member_value.split(os.linesep)
                for line in temp_text_list:
                    if line != "":
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
                        nkey = SPEC_EXTRA_KEYS[extra_key][0]
                        nsubkey = SPEC_EXTRA_KEYS[extra_key][1]
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
                        fp.write(cur_indent + "rpmMacros: |" + os.linesep)
                        for item in extra_val:
                            # fp.write(cur_indent + TAB + "%s\n" % item)
                            item = add_tab_in_lines(item)
                            fp.write(cur_indent + "%s\n" % item.replace('\"', '\\"'))
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
                        fp.write(cur_indent + TAB + ("- %s" + os.linesep) % (esc_value(item)))
            elif isinstance(value, bool):
                if value:
                    fp.write(cur_indent + ("%s: yes" + os.linesep) % (key))
                else:
                    fp.write(cur_indent + ("%s: no" + os.linesep) % (key))
            elif isinstance(value, dict):
                if value:
                    if key != "subpackage":
                        fp.write(cur_indent + ("%s:" + os.linesep) % key)
                    for dict_key, dict_value in value.items():
                        if key == "subpackage":
                            dict_key = "subpackage." + dict_key
                        if isinstance(dict_value, list):
                            base = 0
                            if key == "subpackage":
                                fp.write(("%s:" + os.linesep) % dict_key)
                                base = -1
                            else:
                                fp.write(cur_indent + TAB + ("%s:" + os.linesep) % dict_key)
                            for sub_item in dict_value:
                                if isinstance(sub_item, list):
                                    self._dump_yaml(sub_item, fp, cur_indent + TAB*(base+1), cur_pkg=sub_item[0][1])
                                    fp.write(os.linesep)
                                elif isinstance(sub_item, tuple) and len(sub_item) > 1:
                                    if isinstance(sub_item[1], str):
                                        if os.linesep in sub_item[1].strip():
                                            fp.write(cur_indent + TAB * (base+2) + ("%s: |" + os.linesep) % sub_item[0])
                                            line_list = sub_item[1].split(os.linesep)
                                            for line in line_list:
                                                fp.write(cur_indent + TAB * (base+3) + line + os.linesep)
                                        else:
                                            fp.write(cur_indent + TAB * (base+2) + ("%s: %s" + os.linesep) % (
                                                sub_item[0], sub_item[1]))
                                    elif isinstance(sub_item[1], list):
                                        fp.write(cur_indent + TAB * (base+2) + sub_item[0] + ":" + os.linesep)
                                        for line in sub_item[1]:
                                            fp.write(
                                                cur_indent + TAB * (base+3) + ("- %s" + os.linesep) % esc_value(line))
                                else:
                                    fp.write(cur_indent + TAB * (base+2) + ("- %s" + os.linesep) % (esc_value(sub_item)))
                        elif isinstance(dict_value, str):
                            # if dict_key.isdigit() and dict_key not in ["source", "patchset"]:
                            #     dict_key = "\"" + dict_key + "\""
                            fp.write(cur_indent + TAB + ("%s: %s" + os.linesep) % (dict_key, dict_value))
            else:
                lines_to_write = value.splitlines()

                if len(lines_to_write) == 1:
                    try:
                        fp.write(cur_indent + ("%s: %s" + os.linesep) % (key, esc_value(value)))
                    except UnicodeEncodeError:
                        fp.write(cur_indent + ("%s: %s" + os.linesep) % (key, esc_value(value).encode('utf8')))

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
                for function_name in self.shell_functions.keys():
                    if function_name not in ["install", "prep", "build", "clean", "check"]:
                        fs_runtime = open("runtimePhase.sh", "w")
                        break
                files_file = open("files.yaml", "w")
            except IOError:
                logger.warn('Cannot open file %s for writing' % self.opath)
        if self.opath:
            try:
                fp = open(self.opath, 'w')
            except IOError:
                logger.warn('Cannot open file %s for writing' % self.opath)

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

    def convert(self, _dict, need_break=True):
        """
        整理不必要和额外的数据
        :param _dict: 字典类型的输入
        :param need_break: 空关键字会跳过
        :return:
        """
        self._replace_keys(_dict)
        translate_keys(_dict)
        remove_duplicate(_dict)

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
                        if len(_dict[entry].strip().strip(os.linesep).split(os.linesep)) == 1:
                            if not ((_dict[entry].startswith("\"") and _dict[entry].endswith("\"")) or (
                                    _dict[entry].startswith("\'") and _dict[entry].endswith("\'"))):
                                if "\"" not in _dict[entry]:
                                    _dict[entry] = "\"" + _dict[entry].strip() + "\""
                                elif "\'" not in _dict[entry]:
                                    _dict[entry] = "\'" + _dict[entry].strip() + "\'"
                if entry in ["Sources", "Patches"]:
                    target_items = {}
                    the_items = _dict[entry]
                    if isinstance(the_items, dict):
                        for index2, member in the_items.items():
                            target_items[str(index2)] = member
                    items.append((lower_first_word(entry), target_items))
                else:
                    items.append((lower_first_word(entry), _dict[entry]))
                del _dict[entry]

        subpkgs = {}
        if "SubPackages" in _dict:
            subpkgs_list = _dict["SubPackages"]
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
        sb_cv_table = KEY_SYS
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
        dumper = SpectacleDumper(file_type='yaml', opath=out_fpath, shell_functions=spec_parser.shell_functions,
                                 files=spec_parser.files)
        newspec_fpath = dumper.dump(convertor.convert(spec_parser.cooked_items()))

        logger.info('<spec2yaml> Yaml file %s created' % out_fpath)
        if newspec_fpath:
            logger.info('<spec2yaml> New spec file %s was generated by new yaml file,' % newspec_fpath)


class SpecParser(object):
    """ Parser of SPEC file of rpm package """

    def __init__(self):
        # runtime variables
        self.items = {}
        self.table = {}
        self.cur_pkg = 'main'
        self.macros = ""
        self.rpm_global = {}
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
            if "-f" in ls:
                filesinput += " -f "
            filesinput += this_files_input + os.linesep
            ls.remove("-f")
            if this_files_input != "":
                ls.remove(this_files_input)

        if '-p' in ls:
            create = True
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
        logger.info('the following is the content of PREP in original spec, please compare them with the '
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
        logger.info('Move changelog in %changelog to *.changes file.' + hdr_line)

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

    def add_source_or_patch(self, dict1, keywords, value):
        """
        新增source和patch
        :param dict1:
        :param keywords:
        :param value:
        :return:
        """
        judgement = ""
        keywords = lower_first_word(keywords)
        if "%if %{with" in value:
            with_parts, without_parts = get_if_with_parts(value)
            judgement = " when"
            if len(with_parts):
                judgement += " +" + " +".join(with_parts)
            if len(without_parts):
                judgement += " -" + " -".join(without_parts)
        num_dict = self.sources_num_dict if keywords == "source" else self.patches_num_dict
        count = 6 if keywords == "source" else 5
        if keywords + judgement in dict1:
            if isinstance(dict1[keywords], dict):
                for num, val in num_dict.items():
                    dict1[keywords + judgement][num[count:]] = val
        else:
            for num, val in num_dict.items():
                dict1[keywords + judgement] = {num[count:]: val}
        return dict1

    def read(self, filename):
        """
        读取所有的文件内容和关键字并保存数据
        :param filename:
        :return:
        """
        # comment = re.compile('^#.*')
        cond_if = re.compile('^%if.*')
        cond_else = re.compile('^%else.*')
        cond_endif = re.compile('^%endif.*')
        directive = re.compile('^([\w()]+)[ \t]*:[ \t]*(.*)')
        header_re = re.compile('^%(' + '|'.join(HEADERS) + ')\s*(.*)')
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
        subpackages_mode = False
        while_next = False
        while_next_true = 0
        keywords_type = ""  # 用于多行字段的切换
        last_line = ""  # be used to resolve Line breaks '\'
        # source_number = 0
        # patch_number = 0
        need_left_strip = True
        cat_eof_mode = False
        unclosed_brackets = 0
        in_package_help = False
        macros_mode = False
        lua_mode = False
        for line in open(filename):
            if unclosed_brackets < 0:
                unclosed_brackets = 0
            if cat_eof_mode and header:
                items[header] += line
                if line == "EOF" + os.linesep:
                    cat_eof_mode = False
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
                resolve_special_macros_config(line, self.items)
                if line == MACROS_KEYWORDS[0]:
                    in_package_help = True
                    subpackages_mode = True
                continue
            # if comment.match(line):
            #     # skip comment line and empty line
            #     if len(_if_cond_part) == 0:
            #         continue
            elif state == ST_MAIN and not line:
                continue
            if header == "description" and line == "%package_description":
                items[header] += "%package_description" + os.linesep
                continue
            if line.endswith("\\"):
                need_left_strip = False
            available_key = header_re.match(line) or single_re.match(line) or require_re.match(line)  # parse key spell
            if available_key:
                macros_mode = False
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
                continue
            if re.match("(%define)|(%global)|(%bcond_with)|(%\{\!\?)|(%undefine)|(%\{\?)|(%\{expand:\s*%)", line) is not None:
                if header in SHELL_KEYWORDS + ["files"] and state == ST_INLINE:
                    # shell lines or inline mode pass
                    macros_mode = False
                    pass
                else:
                    if unclosed_brackets != 0:
                        if subpackages_mode:
                            if line.startswith("%global"):
                                items = add_string_to_dict(items, "rpmGlobal", line)
                            else:
                                items = add_string_to_dict(items, "rpmMacros", line)
                        else:
                            self.macros += line + os.linesep
                        continue
                    else:
                        if if_cond_part:
                            if subpackages_mode:
                                items = add_string_to_dict(items, "rpmMacros", if_cond_part[0])
                            else:
                                self.macros += if_cond_part[0]
                            if_cond_part.clear()
                        macros_mode = True
            lua_mode, end_words = check_lua_config(line, lua_mode)
            if lua_mode:
                items = add_lua_config(items, line)
                if line == end_words:
                    lua_mode = False
                continue
            if macros_mode:
                if subpackages_mode:
                    items = add_string_to_dict(items, "rpmMacros", line)
                else:
                    self.macros += line + os.linesep
                continue
            if not available_key:
                if ":" in line:
                    first_key = line.split(":")[0].strip()
                    is_available, real_key = parse_case_spell(first_key, self.items)
                    if not is_available:
                        temp_line = line.replace(line.split(":")[0], line.split(":")[0].capitalize().strip())
                        available_key = header_re.match(temp_line) or single_re.match(
                            temp_line) or require_re.match(temp_line)
                    else:
                        header = real_key
            if available_key:
                if header_re.match(line):
                    if "%package" in line:
                        subpackages_mode = True
                    state = ST_INLINE
                    if subpackages_mode:
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
                        line = resolve_inner_quotes(line)
                elif require_re.match(line):
                    if require_re.match(line).group(1) not in items:
                        state = ST_MAIN

            if state == ST_INLINE:
                if header_re.match(line):
                    state = ST_INLINE
                    keywords_type = "lines"
                    header = cur_block = header_re.match(line).group(1)
                    if header in line and header not in OBS_LINES_KEYWORDS and header != "package" and len(line.split()) > 0:
                        while_next = False
                        line = line.replace(header + " ", header + os.linesep)
                    if cur_block == "package":
                        while_next = False
                        while_next_true = 0
                        # change model from INLINE into subpackages
                        state = ST_MAIN
                        subpackages_mode = True
                        _if_cond_part, if_cond_part = inline_to_mainline(_if_cond_part, if_cond_part)
                        _else_cond_part, else_cond_part = inline_to_mainline(_else_cond_part, else_cond_part)
                        continue
                    elif cur_block.startswith("files"):
                        while_next = False
                        while_next_true = 0
                        _if_cond_part, if_cond_part = inline_to_mainline(_if_cond_part, if_cond_part)
                        _else_cond_part, else_cond_part = inline_to_mainline(_else_cond_part, else_cond_part)
                        header = cur_block = "files"
                        items[cur_block] = line + os.linesep
                        items = parse_files_input(self.items, items, line=line, if_lines=if_cond_part,
                                                  else_lines=else_cond_part, else_status=else_status)
                        continue
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
                    line_suffix = get_line_suffix(if_cond_part, else_cond_part, else_status)
                    cur_block = single_re.match(line).group(0)
                    line = resolve_inner_quotes(line)
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
                        if cond_else.match(line):
                            _else_cond_part, else_cond_part = inline_to_mainline(_else_cond_part, else_cond_part)
                            else_status = True
                            _else_status = False
                            continue
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
                            cat_eof_mode = True
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
                        # if re.match(r"%patch\d*", line) is not None or re.search("%\{PATCH\d*\}", line) is not None:
                        #     if not line.startswith("#"):
                        #         line = self.modify_patch_serial_number(line)
                        # if re.search(r"%\{SOURCE\d*\}", line) is not None or re.search("%SOURCE\d*", line) is not None \
                        #         or re.search("%\{S:\d*\}", line) is not None:
                        #     if not line.startswith("#"):
                        #         line = self.modify_source_number(line)
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
                        subpackages_mode = True
                    elif not subpackages_mode:
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
                line_suffix = get_line_suffix(if_cond_part, else_cond_part, else_status)
                directive_match = directive.match(line)
                header_match = header_re.match(line) if not directive_match else None
                if directive_match:
                    key = directive_match.group(1) if real_key == "" else real_key
                    val = directive_match.group(2)
                    if key.lower().startswith("source"):
                        if len(else_cond_part) == 0:
                            new_key = key.upper()
                            source = new_key[0:6]
                            num = re.sub("^0+", "", new_key[6:])
                            if num == "":
                                num = "0"
                            new_key = source + num
                            self.sources_num_dict[new_key] = val
                    if key.lower().startswith("patch"):
                        new_key = key.lower()
                        patch = new_key[0:5]
                        num = re.sub("^0+", "", new_key[5:])
                        if num == "":
                            num = "0"
                        new_key = patch + num
                        self.patches_num_dict[new_key] = val
                        # patch_number += 1
                    key = update_keywords(key, val)
                    case_spell_result = parse_case_spell(key, self.items)
                    key = key.replace("requires", "Requires") if case_spell_result else key
                    if key not in SINGLES and key not in REQUIRES and key not in ORDER_ENTRIES and key not in SKIPS:
                        may_parse = not (parse_case_spell(key, self.items))
                        if not may_parse:
                            key = key.capitalize()

                    # special case for Source and Patch
                    key = update_keywords(key)
                    val = find_quotes_from_words(val + line_suffix)
                    if key in ["Sources", "Patches"]:
                        items = self.add_source_or_patch(items, key, val)
                    else:
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
                        subpackages_mode = True
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
                                if "AsWholeName" not in self.items["SubPackages"][sub_name]:
                                    sub_name = sub_name if "-n" in opt.split() else self.items["Name"][0] + "-" + sub_name
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
                            items = parse_files_input(self.items, items, line=line, if_lines=if_cond_part,
                                                      else_lines=else_cond_part, else_status=else_status)

                        if items:
                            if header not in self.keywords_if_config:
                                if if_cond_part:
                                    self.keywords_if_config[header] = [os.linesep.join(if_cond_part)]
                            cur_block = header
                            if cur_block not in items:
                                items[cur_block] = line + os.linesep
                else:
                    if len(if_cond_part) == len(else_cond_part) == len(_if_cond_part) == 0 and line == "%endif":
                        continue
                    try:
                        items = add_string_to_dict(items, header, line, True)
                    except Exception as e:
                        logger.info(str(e))
        self.change_several_requires()
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
        self.macros, self.rpm_global = divide_rpm_global(self.macros, self.rpm_global)
        self.produce_use_flag()
        target_data = copy.deepcopy(original_data)
        if "Version" in original_data.keys() and original_data["Version"]:
            if type(original_data["Version"]) == str and original_data["Version"].startswith("%"):
                target_data = add_quotation_from_member("Version", self.items, target_items=target_data)
            elif type(original_data["Version"]) == list and original_data["Version"][0].startswith("%"):
                target_data = add_quotation_from_member("Version", self.items, target_items=target_data)
        for _key, _value in original_data.items():
            if _key in NEED_QUOTATION_KEYWORDS:
                target_data = add_quotation_from_member(_key, self.items, target_items=target_data)
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
                    files_judgement += " when %if" + " when %if".join(file_key.split(" %if")[1:])
                    main_file_key = "files" + files_judgement
                else:
                    main_file_key = "files"
                self.files[main_file_key] = original_data["files"]
                del target_data["files"]
            if _key == "SubPackages":
                for sub_member_name, sub_member_dict in original_data["SubPackages"].items():
                    if "rpmMacros" in sub_member_dict:
                        sub_member_dict["rpmMacros"], sub_member_dict["rpmGlobal"] = divide_rpm_global(
                            sub_member_dict.get("rpmMacros"), {})
                    whole_name = "AsWholeName" in original_data["SubPackages"][sub_member_name].keys()
                    sub_files_judgement = ""
                    if "FilesJudgement" in sub_member_dict:
                        temp_sub_member_list = copy.deepcopy(sub_member_dict["FilesJudgement"])
                        for judgement_words in temp_sub_member_list:
                            if judgement_words in sub_member_name:
                                sub_member_dict["FilesJudgement"].remove(judgement_words)
                        if sub_member_dict["FilesJudgement"]:
                            sub_files_judgement += " when " + " when ".join(sub_member_dict["FilesJudgement"])
                        del target_data["SubPackages"][sub_member_name]["FilesJudgement"]
                    if "%if" in sub_member_name:
                        target_data = clear_sub_extra_judge(sub_member_name, self.items, target_items=target_data)
                    sub_file_name = target_data["Name"][0] + "-" + sub_member_name.split("%if")[0].strip() \
                        if not whole_name else sub_member_name.strip()
                    for member_key, member_value in sub_member_dict.items():
                        if member_key == "files":
                            self.files["subpackage." + sub_file_name + ".files" + sub_files_judgement] = member_value
                            del target_data["SubPackages"][sub_member_name]["files"]
                        if member_key == "Summary" and len(member_value) == 1 and member_value[0].startswith("`"):
                            target_data["SubPackages"][sub_member_name][member_key] = ["_" + member_value[0]]
                        if member_key in NEED_QUOTATION_KEYWORDS:
                            target_data = add_quotation_from_member(member_key, self.items,
                                                                    sub_name=sub_member_name, target_items=target_data)
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
                    if "FilesInput" in sub_member_dict:
                        target_data["SubPackages"][sub_member_name]["files"] = sub_member_dict["files"].replace("%files", "%files" + os.linesep, 1)
                        del target_data["SubPackages"][sub_member_name]["FilesInput"]
                    if "%if" in sub_member_name:
                        temp_sub_dict = target_data["SubPackages"][sub_member_name]
                        del target_data["SubPackages"][sub_member_name]
                        target_data["SubPackages"][sub_member_name.replace("%if", "when %if")] = temp_sub_dict
        self.items = target_data

    def change_several_requires(self):
        for change_key, target_key in LIST_KEY_REPLACE.items():
            if change_key in self.items and isinstance(self.items[change_key], list):
                self.change_requires_struct(change_key, target_key)

    def change_requires_struct(self, origin, target):
        """改变依赖的结构"""
        target_list = self.items[origin].copy()
        for build_rq in self.items[origin]:
            if "%if %{with" in build_rq:
                with_parts, without_parts = get_if_with_parts(build_rq)
                new_key = target + " when"
                without = ""
                if len(with_parts):
                    new_key += " +" + " +".join(with_parts)
                    without = "-"
                if len(without_parts):
                    new_key += " -" + " -".join(without_parts)
                    without = "+"
                value = build_rq.split("%if %{with")[0].strip()
                if new_key in self.items:
                    self.items[new_key].append(without + value)
                else:
                    self.items[new_key] = [without + value]
                target_list.remove(build_rq)
            else:
                pass
        target_list = divide_several_requires(target_list)
        self.items[origin] = target_list

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
        elif (sub_name is not None) and value.startswith("%" + keywords + " " + original_sub_name + os.linesep):  # 子包shell语句分解
            function_context = value.lstrip("%" + original_sub_name + " " + keywords).strip(os.linesep) + os.linesep
            self.shell_functions[keywords + ":" + sub_name] = function_context
        elif value.startswith("%" + keywords) and keywords in RARE_KEYWORDS:
            first_line = value.split(os.linesep)[0]
            if sub_name:
                function_context = value.replace(first_line, "", 1).strip(os.linesep) + os.linesep
                self.shell_functions[keywords + ":" + sub_name] = first_line.replace(
                    "%" + keywords, "", 1) + os.linesep + function_context
            else:
                function_context = value.replace(first_line, "", 1).strip(os.linesep) + os.linesep
                self.shell_functions[keywords] = first_line.replace(
                    "%" + keywords, "", 1) + os.linesep + function_context
        # else:
        #     if sub_name is not None and " -n " in value:
        #         return False
        if "build" in self.shell_functions and "configure" not in self.shell_functions:
            self.shell_functions["configure"], self.shell_functions["build"] = divide_out_configure(
                self.shell_functions["build"])

    def produce_use_flag(self):
        line_list = self.macros.split(os.linesep)
        if_cond = []
        else_cond = []
        target_list = line_list.copy()
        remove_line = []
        back_count = 0
        contain_bcond = False
        for i, line in enumerate(line_list):
            if re.search("%(bcond_with)|(bcond_without) \s+", line) is not None:
                contain_bcond = True
                if line.endswith("\\"):
                    continue
                if if_cond and len(else_cond) == 0:
                    use_flag_key = "useFlag " + if_cond[0].replace("%if", "when %if")
                    remove_line.append(line_list.index(if_cond[0]))
                    back_count += 1
                    if i - back_count not in remove_line:
                        remove_line.append(i - back_count)
                elif if_cond and else_cond:
                    use_flag_key = "useFlag " + get_reverse_judgement(if_cond[0]).replace("%if", "when %if")
                    back_count += 1
                    if i - back_count not in remove_line:
                        remove_line.append(i - back_count)
                else:
                    use_flag_key = "useFlag"
                if use_flag_key not in self.items:
                    self.items[use_flag_key] = [line.split()[-1]]
                else:
                    self.items[use_flag_key].append(line.split()[-1])
                remove_line.append(i)
            elif re.search("(%define)|(%global)|(%bcond_with)|(%\{\!\?)|(%undefine)|(%\{\?)|(%\{expand:\s*%)", line) is not None:
                contain_bcond = False
            if line.startswith("%if"):
                if_cond.append(line)
                back_count = 0
            elif line.startswith("%else"):
                else_cond.append("%else")
                back_count = 0
            elif line.strip() == "%endif":
                if len(if_cond) > 0:
                    if_cond.pop()
                    if contain_bcond:
                        remove_line.append(i)
                else_cond.pop() if else_cond else None
                back_count = 0
        remove_line.reverse()
        for j in remove_line:
            target_list.pop(j)
        self.macros = os.linesep.join(target_list)

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
            self.change_define2global()
            ck_items['extra']['macros'] = self.macros
        if self.rpm_global:
            ck_items['rpmGlobal'] = self.rpm_global

        return ck_items

    def change_define2global(self):
        macros_list = self.macros.split(os.linesep)
        target_list = macros_list.copy()
        remove_line_list = []
        for k, macros_line in enumerate(macros_list):
            if macros_line.endswith("\\"):
                continue
            if re.match("%define \w+ [\s\S]+", macros_line) is not None:
                line_list = macros_line.split()
                self.rpm_global[line_list[1]] = " ".join(line_list[2:])
                remove_line_list.append(k)
        remove_line_list.reverse()
        for line_num in remove_line_list:
            target_list.pop(line_num)
        self.macros = os.linesep.join(target_list)
