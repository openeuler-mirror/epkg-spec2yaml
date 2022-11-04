import copy
import csv
import os

import requests
import yaml
from Cheetah.Template import Template
from openEulerTransition.configure.common import *
from openEulerTransition.configure.template import *
from openEulerTransition.configure.date import *
from openEulerTransition.configure.yaml_config import *
from openEulerTransition.actions.utils.toolchain_cmake_template import ToolChainCmakeTemplate
from openEulerTransition.actions.package_manage.download import DownloadWorker
from openEulerTransition.actions.package_manage.folder import *
from openEulerTransition.logs.log import logger
from openEulerTransition.actions.utils.file_operate import Path

# Mandatory keys for main package
MAND_KEYS = ('name',
             'meta.summary',
             'version',
             'meta.license',
             )

ARGS_TRANS_DEFINITION = {
    "${PN}": "%{name}",
    "${PV}": "%{version}",
    "${BPN}": "%{name}",  # "yaml_fpath.partition(\"_\")[0]",
    "${B}": "%{_builddir}",
    "${S}": "%{_sourcedir}",
    "${D}": "%{_buildrootdir}",
    "${WORKDIR}": "%{_builddir}"
}

# Mandatory keys for subpackage
SUB_MAND_KEYS = ('name',
                 'meta.summary',
                 )

# boolean keys with the default 'False' value
# BOOLNO_KEYS = ('check',
BOOLNO_KEYS = ('NoAutoReq',
               'NoAutoProv',
               'NoAutoReqProv',
               'NoSetup',
               'NoAutoLocale',
               'asWholeName',
               'NoFiles',
               'NoDesktop',
               'UpdateDesktopDB',
               'NoIconCache',
               'NoSystemdService',
               )

# boolean keys with the default 'True' value
BOOLYES_KEYS = ('UseAsNeeded',
                'AutoDepend',
                )

# All boolean keys
BOOL_KEYS = BOOLNO_KEYS + BOOLYES_KEYS

# Keys expected to have list type value.
LIST_KEYS = ('source',
             'extraSources',
             'ConfigOptions',
             'QMakeOptions',
             'requires',
             'buildRequires',
             'suggests',
             'requiresPre',
             'requiresPreUn',
             'requiresPreTrans',
             'requiresPost',
             'requiresPostUn',
             'requiresPostTrans',
             'pkgBR',
             'pkgConfigBR',
             'provides',
             'conflicts',
             'buildConflicts',
             'obsoletes',
             'exclusiveArch',
             'autoSubPackages',
             'files',
             'RunFdupes',
             'RpmLintIgnore',
             'rpmMacros',
             'Macros2',
             'buildArch',
             )

# Keys expected to have string value.
STR_KEYS = ('name',
            'meta.summary',
            'meta.description',
            'version',
            'release',
            'epoch',
            'group',
            'meta.license',
            'meta.homepage',
            # "Source Code Management". In this context URL to git repository.
            'SCM',
            # Type of archive that is done when SCM is used.
            'Archive',
            'buildArch',
            'SourcePrefix',
            'Configure',
            'builder',
            'SetupOptions',
            'LocaleName',
            'LocaleOptions',
            # Defines the package name where the *.lang file is added.
            'LocaleFilesPkgName',
            'filesInput',
            'prefix',
            )

# Keys that are only available for subpackages
SUBONLY_KEYS = ('asWholeName',
                'AutoDepend',
                )

# Key that are warned about moving to main package
# if found from subpackages.
SUBWARN_KEYS = ('pkgBR',
                'pkgConfigBR',
                'buildConflicts',
                )

# Keys available for subpackages.
SUBAVAIL_KEYS = ('name',
                 'meta.summary',
                 'recommends',
                 'install',
                 'build',
                 'clean',
                 'post',
                 'prep',
                 'suggests',
                 'meta.description',
                 'group',
                 'meta.license',
                 'files',
                 'prefix',
                 'requires',
                 'requiresPre',
                 'requiresPreUn',
                 'requiresPreTrans',
                 'requiresPost',
                 'requiresPostUn',
                 'requiresPostTrans',
                 'provides',
                 'conflicts',
                 'obsoletes',
                 'NoAutoReq',
                 'NoAutoProv',
                 'NoAutoReqProv',
                 'NoIconCache',
                 'filesInput',
                 # Very rare keys in sub packages
                 'version',
                 'release',
                 'epoch',
                 'meta.homepage',
                 'buildArch',
                 )

# Deprecated keys that are not used anymore and
# should be removed from .yaml
DROP_KEYS = ('PostScripts',
             'Documents',
             'SupportOtherDistros',
             )

# Renamed keys.
RENAMED_KEYS = {'NeedCheckSection': 'check',
                'NoLocale': 'NoAutoLocale',
                }

# Common typos in keys
TYPO_KEYS = {'buildRequires': 'pkgBR or pkgConfigBR',
             'Url': 'meta.homepage',
             }

# Keys that may have archictecture qualifier in front of them.
ARCHED_KEYS = ('requires',
               'suggests',
               'pkgBR',
               'pkgConfigBR',
               'patchset',
               'ConfigOptions',
               'QMakeOptions',
               'files',
               )

# Available architecture qualifiers
ARCHS = {'ix86': '%{ix86}',
         'arm': '%{arm}',
         'armv5': 'armv5el armv5tel armv5tejl',
         'armv6': 'armv6l armv6hl',
         'armv7': 'armv7el armv7tel armv7l armv7hl armv7nhl armv7thl armv7tnhl',
         }

# Different options for "Configure" yaml key.
CONFIGURES = ('configure', 'reconfigure', 'autogen', 'cmake', 'none')

# Different options for "builder" yaml key.
BUILDERS = ('make', 'single-make', 'python', 'python3', 'perl', 'qmake', 'qmake5', 'qtc', 'qtc5', 'cmake', 'none')

# Paths that should be replaced with macros when seen in %files.
# NOTE: Order of this list matters!
PATHMACROS = (('/usr/bin', '%{_bindir}'),
              ('/usr/sbin', '%{_sbindir}'),
              ('/usr/lib', '%{_libdir}'),
              ('/usr/libexec', '%{_libexecdir}'),
              ('/usr/include', '%{_includedir}'),
              ('/usr/share/info', '%{_infodir}'),
              ('/usr/share/man', '%{_mandir}'),
              ('/usr/share', '%{_datadir}'),
              ('/usr', '%{_prefix}'),
              ('/etc/rc.d/init.d', '%{_initddir}'),
              ('/etc/init.d', '%{_initddir}'),
              ('/etc', '%{_sysconfdir}'),
              ('/var/lib', '%{_sharedstatedir}'),
              ('/var', '%{_localstatedir}'),
              )


def _gen_auto_requires(metadata, extra, pkg_name='main'):
    auto_requires = {
        'Lib': {'requiresPost': ['/sbin/ldconfig'],
                'requiresPostUn': ['/sbin/ldconfig'],
                },
        'Icon': {'requiresPost': ['/bin/touch', '%{_bindir}/gtk-update-icon-cache'],
                 },
        # buildRequires doesn't support paths, thus this is mentioned as package.
        'Desktop': {'pkgBR': ['desktop-file-utils'],
                    },
        'DesktopDB': {'requiresPost': ['%{_bindir}/update-desktop-database'],
                      'requiresPostUn': ['%{_bindir}/update-desktop-database'],
                      },
        'Info': {'requiresPost': ['/sbin/install-info'], 'requiresPostTrans': ['/sbin/install-info'],
                 'requiresPostUn': ['/sbin/install-info'],
                 },
        'Service': {'requiresPost': ['/sbin/service', '/sbin/chkconfig'],
                    'requiresPostUn': ['/sbin/service', '/sbin/chkconfig'],
                    'requiresPostTrans': ['/sbin/service', '/sbin/chkconfig'],
                    },
        'SystemdService': {'requiresPost': ['systemd'],
                           'requiresPreUn': ['systemd'],
                           'requiresPostUn': ['systemd'],
                           'requires': ['systemd'],
                           },
        'Schema': {'requiresPost': ['%{_bindir}/gconftool-2'],
                   'requiresPreUn': ['%{_bindir}/gconftool-2'],
                   'requiresPre': ['%{_bindir}/gconftool-2'],
                   },
    }

    for _key, reqs in auto_requires.items():
        if extra[_key]:
            for req, items in reqs.items():
                if req in metadata:
                    for i in items:
                        # e.g. GConf2 >= 0.14
                        yaml_reqs = [s.split()[0] for s in metadata[req]]
                        if i in yaml_reqs:
                            if i in metadata[req]:
                                logger.warn('duplicate item: %s for %s in package %s' % (i, req, pkg_name))
                            # else do nothing
                        else:
                            metadata[req].append(i)
                else:
                    metadata[req] = items


def _cleanup_boolkeys(items):
    """ clean up all boolean type keys,
        use the exists status to present bool value
    """
    #   for keys with default value FALSE
    for bopt in BOOLNO_KEYS:
        if bopt in items and not items[bopt]:
            del items[bopt]
    #   for keys with default value TRUE
    for bopt in BOOLYES_KEYS:
        if bopt in items and not items[bopt]:
            del items[bopt]
        else:
            items[bopt] = True


def combine_if_lines(_temp_list):
    """
    合并判断语句
    :param _temp_list: 输入的字符串数组
    :return:
    """
    temp_if_key_lines = []
    temp_combine_str = ""
    for temp_step in _temp_list:
        if "%if" in temp_step and temp_step not in temp_if_key_lines:
            temp_if_key_lines.append(temp_step)
            temp_combine_str += temp_step + os.linesep
        elif "%endif" in temp_step and temp_if_key_lines:
            temp_if_key_lines.pop()
            temp_combine_str += temp_step + os.linesep
        elif "%if" in temp_step and temp_step in temp_if_key_lines:
            continue
        else:
            temp_combine_str += temp_step + os.linesep
    return temp_combine_str


# global helper functions
def arch_split(value):
    m = re.match(r'^(\w+):([^:]+)', value)
    if m:
        arch = m.group(1)
        left = m.group(2)
        if arch in ARCHS:
            return arch, ARCHS[arch], left
        else:
            return arch, arch, left
    else:
        return '', '', value


def update_key_params(text):
    """
    变换$变量，转换为spec特有的%变量
    :param text: 文本
    :return:
    """
    text_lines = text.split(os.linesep)
    for line_index, text_line in enumerate(text_lines):
        for source_content, aim_content in ARGS_TRANS_DEFINITION.items():
            if source_content in text_line:
                text_lines[line_index] = text_line.replace(source_content, aim_content)
    after_trans_text = os.linesep.join(text_lines)
    return after_trans_text


def remove_strings_keywords(origin_dict: dict, keywords=""):
    """
    去除关键字
    :param origin_dict:
    :param keywords:
    :return:
    """
    target_dict = copy.deepcopy(origin_dict)
    for some_key in origin_dict:
        if isinstance(origin_dict[some_key], str):
            target_dict[some_key] = origin_dict[some_key].replace(keywords, "").replace(keywords + " ", "")
        if isinstance(origin_dict[some_key], dict):
            target_dict[some_key] = remove_strings_keywords(origin_dict[some_key], keywords)
        if isinstance(origin_dict[some_key], list):
            for index0, member in enumerate(origin_dict[some_key]):
                if isinstance(member, dict):
                    target_dict[some_key][index0] = remove_strings_keywords(member, keywords)
                elif isinstance(member, str):
                    target_dict[some_key][index0] = origin_dict[some_key][index0].replace(keywords, "").replace(keywords + " ", "")
                elif isinstance(member, list):
                    for index1, member_item in enumerate(member):
                        target_dict[some_key][index0][index1] = member_item.replace(keywords, "").replace(keywords + " ", "")
        if keywords in some_key:
            target_value = origin_dict[some_key]
            del target_dict[some_key]
            target_dict[some_key.replace(keywords, "")] = target_value
    return target_dict


class SpecWriter:
    """
        The following keys will be generated on the fly based on values from
        YAML, and transfered to spec
    """

    extra_per_pkg = {
        'Desktop': False,
        'DesktopDB': False,
        'Schema': False,
        'Schemas': [],
        'Lib': False,
        'HasStatic': False,
        'Icon': False,
        'Service': False,
        'SystemdService': False,
        'SystemdServices': [],
        'Info': False,
        'Infos': [],
    }

    # Templates for autoSubPackages key
    asp_templates = {
        'devel': {"devel": {
            'meta.description': "Development files for %{name}.",
            'meta.summary': "Development files for %{name}",
            'group': "Development/Libraries",
            'AutoDepend': "True"
        }
        },
        'docs': {"docs": {
            'meta.description': "Documentation files for %{name}.",
            'meta.summary': "Documentation files for %{name}",
            'group': "Development/Libraries",
            'AutoDepend': "True"
        }
        },
        'lang': {"lang": {
            'meta.description': "Translation files for %{name}.",
            'meta.summary': "Translation files for %{name}",
            'group': "Development/Libraries",
            'AutoDepend': "True"
        }
        },
        # Used when package doesn't match any of the above.
        'unknown': {"unknown": {
            'meta.description': "files for %{name}.",
            'meta.summary': "files for %{name}",
            'group': "Development/Libraries",
            'AutoDepend': "True"
        }
        },
    }

    def __init__(self, yaml_fpath, conf_fpath, **kwargs):
        self.new_spec = True
        self.yaml_fpath = yaml_fpath
        self.conf_fpath = conf_fpath
        self.shell_fpath = kwargs["shell_fpath"] if "shell_fpath" in kwargs.keys() else None
        self.python_fpath = kwargs["python_fpath"] if "python_fpath" in kwargs.keys() else None
        self.cross_compile = kwargs["cross_compile"] if "cross_compile" in kwargs.keys() else False
        self.metadata = {}
        self.keywords_if_config = {}
        self.release = None
        self.specfile = os.path.splitext(yaml_fpath)[0] + '.spec'
        self.packages = {}

        # initialize extra info for spec
        self.extra = {'subpkgs': {}, 'content': {}}

        # update extra info for main package
        self.extra.update(copy.deepcopy(self.extra_per_pkg))

        # record filelist from 'extraSources' directive
        self.extras_filelist = []

        try:
            self.stream = open(yaml_fpath, 'r')
        except IOError:
            logger.error('Cannot read file: %s' % yaml_fpath)

    def dump(self):
        # debugging
        import pprint
        pprint.pprint(yaml.dump(yaml.load(self.stream, Loader=yaml.FullLoader)))

    def _modify_arg_value(self, keyword: str):
        """
        修改带$符号的键值对
        :param keyword:键名
        :return:
        """
        data = self.metadata[keyword]
        for arg_and_value in data:
            if type(arg_and_value) == dict and not arg_and_value:
                result_dict = {}
                for _key, value in arg_and_value.items():
                    if "$" in value:
                        value = update_key_params(value)
                    if "$" in _key:
                        for source_word, aim_word in ARGS_TRANS_DEFINITION.items():
                            if source_word in _key:
                                result_dict[_key.replace(source_word, aim_word)] = value
                return result_dict

    def _check_dup_files(self, files):
        # try to remove duplicate '%defattr' in files list
        dup1 = '%defattr(-,root,root,-)'
        dup2 = '%defattr(-,root,root)'
        found_dup = dup1 if dup1 in files else dup2 if dup2 in files else None
        if found_dup:
            logger.warn('found duplicate "%s" in file list, removed!' % found_dup)
            files.remove(found_dup)

    def _check_dup_ldconfig(self, pkg_name=None):
        if not pkg_name:
            pkg_name = 'main'
            if not self.extra['Lib']:
                return
        else:
            if not self.extra['subpkgs'][pkg_name]['Lib']:
                return

        dup1 = '/sbin/ldconfig'
        dup2 = 'ldconfig'

        for sec in ('post', 'postun'):
            try:
                extra = self.extra['content'][sec][pkg_name]
            except KeyError:
                continue
            found_dup = dup1 if dup1 in extra else dup2 if dup2 in extra else None
            if found_dup:
                extra.remove(found_dup)
                logger.warn(
                    'Found duplicate "%s" calling in "%%%s" of %s package, removed!' % (found_dup, sec, pkg_name))

    def _check_dup_scriptlets(self, pkg_name=None):
        if not pkg_name:
            pkg_name = 'main'
            extra = self.extra
        else:
            extra = self.extra['subpkgs'][pkg_name]

        if extra['Desktop']:
            re_idstr = re.compile('^desktop-file-install\s+')
            try:
                lines = extra['content']['install']['pre'] + \
                        extra['content']['install']['post']
            except KeyError:
                pass
            else:
                for line in lines:
                    if re_idstr.match(line):
                        logger.warn('Found possible duplicate "desktop-file-install" script in post install')
                        break

            if extra['DesktopDB']:
                re_idstr = re.compile('^update-desktop-database\s+')
                for sec in ('post', 'postun'):
                    try:
                        lines = self.extra['content'][sec][pkg_name]
                    except KeyError:
                        continue

                    for line in lines:
                        if re_idstr.match(line):
                            logger.warn(
                                'Found possible duplicate "update-desktop-database" script in %%%s of %s package' % (
                                    sec, pkg_name))
                            break

        if extra['Info']:
            re_idstr = re.compile('^%install_info')
            for sec in ('post', 'postun'):
                try:
                    lines = self.extra['content'][sec][pkg_name]
                except KeyError:
                    continue

                for line in lines:
                    if re_idstr.match(line):
                        logger.warn('Found possible duplicate "%%install_info..." script in %%%s of %s package' % (
                            sec, pkg_name))
                        break

        if extra['Icon']:
            re_idstr = re.compile('^/bin/touch\s+.*%{_datadir}/icons/hicolor.*')
            re_idstr2 = re.compile('gtk-update-icon-cache\s+')
            for sec in ('post', 'postun'):
                try:
                    lines = self.extra['content'][sec][pkg_name]
                except KeyError:
                    continue

                for line in lines:
                    if re_idstr.match(line):
                        logger.warn(
                            'Found possible duplicate script to touch icons in %%%s of %s package' % (sec, pkg_name))
                    elif re_idstr2.search(line):
                        logger.warn(
                            'Found possible duplicate "gtk-update-icon-cache" script in %%%s of %s package' % (
                                sec, pkg_name))

        if extra['Schema']:
            re_idstr = re.compile('gconftool-2\s+')
            for sec in ('post', 'pre', 'preun'):
                try:
                    lines = self.extra['content'][sec][pkg_name]
                except KeyError:
                    continue

                for line in lines:
                    if re_idstr.search(line):
                        logger.warn(
                            'Found possible duplicate "gconftool-2" script in %%%s of %s package' % (sec, pkg_name))
                        break

    def sanity_check(self):
        """
        整理metadata数据，包含大量私有函数
        :return:
        """

        def _check_empty_keys(metadata):
            """ return the empty keys """
            _keys = []
            for _key_ in list(metadata.keys()):
                if metadata[_key_] is None:
                    _keys.append(_key_)
                    del metadata[_key_]
            return _keys

        def _check_mandatory_keys(metadata, subpkg=False):
            """ return [] if all mandatory keys found, otherwise return the lost keys """
            _keys = list(SUB_MAND_KEYS) if subpkg else list(MAND_KEYS)

            for key_member in metadata:
                if key_member in _keys:
                    _keys.remove(key_member)
                    if not _keys:
                        break
            return _keys

        def _check_invalid_keys(metadata, subpkg=None):
            """ return list of invalid keys """
            if not subpkg:
                # main package
                all_keys = list(LIST_KEYS + STR_KEYS + BOOL_KEYS)
                all_keys += list(RENAMED_KEYS.keys())
                all_keys.append('subpackage')
                for key_member in SUBONLY_KEYS:
                    all_keys.remove(key_member)
            else:
                # sub package
                all_keys = list(SUBAVAIL_KEYS + SUBWARN_KEYS + SUBONLY_KEYS)

            new_keys = []
            for _key_ in metadata:
                if _key_ not in all_keys:
                    new_keys.append(_key_)

            # whether the invalid keys are common typo
            for _key_ in new_keys[:]:
                if _key_ in TYPO_KEYS:
                    logger.warn('"%s" might be a typo of %s, please fix it' % (_key_, TYPO_KEYS[_key_]))
                    new_keys.remove(_key_)

            return new_keys

        def _check_subwarn_keys(metadata, subpkg):
            """ return """
            _keys = []
            for _key_ in SUBWARN_KEYS:
                if _key_ in metadata:
                    logger.warn(
                        '"%s" found in sub-pkg: %s, please consider to move it to main package' % (_key_, subpkg))
                    _keys.append(_key_)
            return _keys

        def _check_key_group(metadata):
            if "group" in metadata:
                try:
                    for line in open(date_path + '/GROUPS'):
                        if metadata['group'] in line:
                            warn = False
                            break
                except IOError:
                    logger.error(
                        'Cannot open GROUPS, maybe the package was not installed correctly.')

        def _check_key_license(metadata):
            # warning for gplv3
            gpl3_re = re.compile(r'L?GPL\s*v3', re.I)
            if "meta.license" in metadata:
                if gpl3_re.search(metadata['meta.license']):
                    logger.warn('GPLv3 related license might be unacceptable.')

        def _check_key_epoch(metadata):
            if 'epoch' in metadata:
                logger.warn('Please consider to remove "epoch"')

        def _check_pkgconfig():
            try:
                pkg_cfg = csv.reader(
                    open(date_path + '/pkgconfig-provides.csv'),
                    delimiter=',')
                for row in pkg_cfg:
                    pc = re.search(r'pkgconfig\(([^)]+)\)', row[1])
                    m = pc.group(1)
                    if row[0] in self.packages:
                        ll = self.packages[row[0]]
                        ll.append(m)
                        self.packages[row[0]] = ll
                    else:
                        self.packages[row[0]] = [m]
            except IOError:
                logger.error(
                    'Cannot open pkgconfig-provides.csv, '
                    'maybe the package was not installed correctly.')

        def _check_listkey(metadata, _key):
            """ sub-routine for LIST typed keys checking
                and will remove all empty and None values
            """
            if _key in metadata and not isinstance(metadata[_key], list):
                return False

            if _key not in metadata:
                return True

            try:
                while True:
                    metadata[_key].remove(None)
            except ValueError:
                pass

            try:
                while True:
                    metadata[_key].remove('')
            except ValueError:
                return True

        def _check_strkey(metadata, _key):
            """ sub-routine for STR typed keys checking """
            if _key in metadata and not isinstance(metadata[_key], str):
                return False
            return True

        def _check_boolkey(metadata, _key):
            """ sub-routine for boolean typed keys checking """
            if _key in metadata and not isinstance(metadata[_key], bool):
                return False
            return True

        def _check_arched_keys(metadata):
            """ sub-routine for ARCH namespace available keys """

            def _check_arch(_key, _item):
                if isinstance(_item, dict):
                    logger.warn(
                        'For arch prefixed %s value "%s", please do NOT leave extra spaces after ":", skipped!' %
                        (_key, ':'.join(map(str, _item.popitem()))))
                    return False

                first_arch = arch_split(_item)[0]
                if first_arch and first_arch not in ARCHS:
                    logger.warn('unsupport arch namespace: %s in key %s' % (first_arch, _key))

                return True

            for _key_ in ARCHED_KEYS:
                if _key_ in metadata:
                    if _key_ in STR_KEYS:
                        if not _check_arch(_key_, metadata[_key_]):
                            del metadata[_key_]
                    elif _key_ in LIST_KEYS:
                        # if metadata[_key_]
                        for item in metadata[_key_]:
                            if not _check_arch(_key_, item):
                                metadata[_key_].remove(item)
                                if not metadata[_key_]:
                                    del metadata[_key_]

        def _check_key_localename(metadata):
            """ sub-routine for 'LocaleName' checking """
            if 'LocaleOptions' in metadata and 'LocaleName' not in metadata:
                return False
            return True

        def _check_dropped_keys(metadata):
            for _key_ in DROP_KEYS:
                if _key_ in metadata:
                    logger.warn('Deprecated key: %s found, please use other valid keys' % _key_)

        def _check_renamed_keys(metadata):
            for _key_ in RENAMED_KEYS:
                if _key_ in metadata:
                    metadata[RENAMED_KEYS[_key_]] = metadata[_key_]
                    del metadata[_key_]
                    logger.warn('Renamed key: %s found, please use %s instead' % (_key_, RENAMED_KEYS[_key_]))

        def _check_key_setups(metadata):
            if 'NoSetup' in metadata:
                if 'SetupOptions' in metadata:
                    logger.warn('"SetupOptions" will have NO effect when "NoSetup" specified in YAML')
                if 'SourcePrefix' in metadata:
                    logger.warn('"SourcePrefix" will have NO effect when "NoSetup" specified in YAML')
            else:
                if 'SetupOptions' in metadata and 'SourcePrefix' in metadata:
                    logger.warn('"SourcePrefix" will have NO effect when "SetupOptions" specified in YAML')
                else:
                    self.metadata['SourcePrefix'] = '%{name}-%{version}'

        def _check_key_nofiles(metadata):
            if 'files' in metadata:
                logger.warn('both "NoFiles" and "files" exist in YAML file, please fix it')
            for req in ('requires',
                        'suggests',
                        'requiresPre',
                        'requiresPreUn',
                        'requiresPreTrans',
                        'requiresPost',
                        'requiresPostUn',
                        'requiresPostTrans',
                        'provides',
                        'conflicts',
                        'buildConflicts',
                        'obsoletes'):
                if req in metadata and metadata[req]:
                    logger.warn('"NoFiles" exists, key %s has no effect any more' % req)

        def _check_key_configure(metadata):
            cfg = metadata['Configure']
            if cfg not in CONFIGURES:
                logger.warn('"%s" is not a valid choice of Configure(%s)' % (cfg, '/'.join(CONFIGURES)))

        def _check_key_builder(metadata):
            builder = metadata['builder']
            if builder not in BUILDERS:
                logger.warn('"%s" is not a valid choice of builder(%s)' % (builder, '/'.join(BUILDERS)))
            # checking invalid 'Configure' for special builder
            if builder in ('python', 'perl', 'qmake', 'cmake') and \
                    'Configure' in metadata and metadata['Configure'] != 'none':
                logger.warn('"%s" need no "Configure" setting which will be ignored' % builder)

        # checking for empty keys
        keys = _check_empty_keys(self.metadata)
        if keys:
            logger.warn('Please remove empty keys in main package: %s' % ', '.join(keys))
        if "subpackage" in self.metadata:
            for sp in self.metadata["subpackage"]:
                keys = _check_empty_keys(sp)
                if keys:
                    logger.warn('Please remove empty keys in %s subpackage: %s' % (sp['name'], ', '.join(keys)))

        # checking for mandatory keys
        keys = _check_mandatory_keys(self.metadata)
        if keys:
            logger.warn('Missing mandatory keys for main package: %s' % ', '.join(keys))
        if "subpackage" in self.metadata:
            for sp in self.metadata["subpackage"]:
                keys = _check_mandatory_keys(sp, True)
                if keys:
                    if 'name' in keys:
                        logger.warn('Missing mandatory keys for sub-pkg: name')
                    else:
                        logger.warn('Missing mandatory keys for sub-pkg "%s": %s' % (sp['name'], ', '.join(keys)))

        # checking for unexpected keys
        keys = _check_invalid_keys(self.metadata)
        if keys:
            logger.warn('Unexpected keys found: %s' % ', '.join(keys))
        if "subpackage" in self.metadata:
            for index, sp in enumerate(self.metadata["subpackage"]):
                if "files" in sp.keys():
                    temp_list = self.metadata["subpackage"][index]["files"].split(os.linesep)
                    combine_str = combine_if_lines(temp_list)
                    self.metadata["subpackage"][index]["files"] = combine_str.strip().strip(os.linesep)
                keys = _check_invalid_keys(sp, sp['name'])
                if keys:
                    logger.warn('Unexpected keys for sub-pkg %s found: %s' % (sp['name'], ', '.join(keys)))

        # checking for questionable sub-package keys
        if "subpackage" in self.metadata and 'NoFiles' not in self.metadata:
            for sp in self.metadata["subpackage"]:
                keys = _check_subwarn_keys(sp, sp['name'])
                if keys:
                    logger.warn('Questionable keys for sub-pkg %s found: %s' % (sp['name'], ', '.join(keys)))

        # checking for deprecated keys
        _check_dropped_keys(self.metadata)

        # checking for renamed keys
        _check_renamed_keys(self.metadata)

        ######### Type checkings ##########
        # checking for LIST expected keys
        for _key in LIST_KEYS:
            if not _check_listkey(self.metadata, _key):
                logger.warn('the value of "%s" in main package is expected as list typed' % _key)
                self.metadata[_key] = [self.metadata[_key]]
            if "subpackage" in self.metadata:
                for sp in self.metadata["subpackage"]:
                    if not _check_listkey(sp, _key):
                        logger.warn(
                            'the value of "%s" in "%s" sub-package is expected as list typed' % (_key, sp['name']))
                        sp[_key] = [sp[_key]]

        # checking for STR expected keys
        for _key in STR_KEYS:
            if not _check_strkey(self.metadata, _key):
                logger.warn('the value of "%s" in main package is expected as string typed' % _key)
                if isinstance(self.metadata[_key], list):
                    self.metadata[_key] = ' '.join(self.metadata[_key])
                else:
                    del self.metadata[_key]
            if "subpackage" in self.metadata:
                for sp in self.metadata["subpackage"]:
                    if not _check_strkey(sp, _key):
                        logger.warn(
                            'the value of "%s" in "%s" sub-package is expected as string typed' % (_key, sp['name']))
                        if isinstance(sp[_key], list):
                            if len(sp[_key]) == 1 and sp[_key][0] is None:
                                del sp[_key]
                                continue
                            sp[_key] = ' '.join(sp[_key])
                        else:
                            del sp[_key]

        # checking for BOOL expected keys
        for _key in BOOL_KEYS:
            if not _check_boolkey(self.metadata, _key):
                logger.warn('the value of "%s" in main package is expected as bool typed, dropped!' % _key)
                # just drop it
                del self.metadata[_key]
            if "subpackage" in self.metadata:
                for sp in self.metadata["subpackage"]:
                    if not _check_boolkey(sp, _key):
                        logger.warn('the value of "%s" in "%s" sub-package is expected as bool typed, dropped!' % (
                            _key, sp['name']))
                        del sp[_key]

        ######### checkings for special keys ##########
        # checking for arch namespace enabled keys
        _check_arched_keys(self.metadata)
        if "subpackage" in self.metadata:
            for sp in self.metadata["subpackage"]:
                _check_arched_keys(sp)

        # checking for proposal pkgconfig requires
        if "pkgBR" in self.metadata:
            _check_pkgconfig()
            pcbr = []
            br = []
            for p in self.metadata['pkgBR']:
                px = p.split()[0]
                for arch in ARCHS:
                    prefix = arch + ':'
                    if px.startswith(prefix):
                        px = px[len(prefix):]
                pl = self.packages
                if px in pl:
                    if len(pl[px]) == 1:
                        pcbr.append(pl[px][0])
                    else:
                        br.append(p)
                    logger.warn("""Please use one of the followings:
                    - %s
                    in pkgConfigBR instead of %s in pkgBR""" % ('\n           - '.join(pl[px]), px))
                else:
                    br.append(p)

            if len(pcbr) > 0:
                if 'pkgConfigBR' in self.metadata:
                    pcbr.extend(self.metadata['pkgConfigBR'])
                logger.info("""Proposal (multiple values skipped, please insert them manually):
                pkgConfigBR:
                - %s
                pkgBR:
                - %s
                    """ % ('\n    - '.join(pcbr), '\n    - '.join(br)))

        _check_key_epoch(self.metadata)

        # checking for meego valid groups
        _check_key_group(self.metadata)
        if "subpackage" in self.metadata:
            for sp in self.metadata["subpackage"]:
                _check_key_group(sp)

        # checking for meego invalid licenses
        _check_key_license(self.metadata)
        if "subpackage" in self.metadata:
            for sp in self.metadata["subpackage"]:
                _check_key_license(sp)

        # By default make meta.description equal to %{summary}.
        if "meta.description" not in self.metadata and 'meta.summary' in self.metadata:
            self.metadata["meta.description"] = "%{summary}."
        if "subpackage" in self.metadata:
            for sp in self.metadata["subpackage"]:
                if 'meta.description' not in sp and 'meta.summary' in sp:
                    sp['meta.description'] = "%{summary}."

        # checking for validation of 'LocaleName' and 'LocaleOptions'
        if not _check_key_localename(self.metadata):
            self.metadata['LocaleName'] = "%{name}"
            logger.warn('lost "LocaleName" keyword, use "%{name}" as default')

        # checking for validation of 'NoSetup', 'SetupOptions' and 'SourcePrefix'
        _check_key_setups(self.metadata)

        # We recommend adding URL for each package
        if 'meta.homepage' not in self.metadata:
            logger.warn(
                "You should consider adding meta.homepage to the main package that points to website or git tree of the package.")

        # checking for validation of 'NoFiles'
        if 'NoFiles' in self.metadata:
            _check_key_nofiles(self.metadata)

        if "BaseArgValue" in self.metadata:
            self._modify_arg_value("BaseArgValue")
        # checking duplicate 'files' items
        if 'files' in self.metadata:
            self._check_dup_files(self.metadata['files'])
        if "subpackage" in self.metadata:
            self._modify_arg_value("subpackage")
            for sp in self.metadata["subpackage"]:
                if 'files' in sp:
                    self._check_dup_files(sp['files'])

        # checking for validation of 'Configure and builder'
        if 'Configure' in self.metadata:
            _check_key_configure(self.metadata)
        if 'builder' in self.metadata:
            _check_key_builder(self.metadata)

    def trans_compile_args(self):
        """
        转换编译选项
        :return:
        """
        if "build" in self.metadata:
            # check is only make or not
            build_info_list = self.metadata["build"].split(os.linesep)
            only_make = False
            configure_make = False
            for line in build_info_list:
                if re.search("#.*make", line) is None and "make" in line and "cmake" not in line and not configure_make:
                    only_make = True
                if re.search("#.*configure", line) is None and ("/configure" in line or "%configure" in line):
                    only_make = False
                    configure_make = True
            if "env.CC" in self.metadata:
                self.metadata["build"] = "export CC=" + self.metadata["env.CC"] + os.linesep + self.metadata["build"]
            if "env.CFLAGS" in self.metadata:
                if configure_make:
                    self.metadata["build"] = "export CFLAGS=" + self.metadata["env.CFLAGS"] + os.linesep + self.metadata["build"]
                elif only_make:
                    if "rpmMacros" in self.metadata:
                        self.metadata["rpmMacros"].append("%global optflags %optflags " + self.metadata["env.CFLAGS"])
                    else:
                        self.metadata["rpmMacros"] = ["%global optflags %optflags " + self.metadata["env.CFLAGS"]]
            if "env.LDFLAGS" in self.metadata:
                if configure_make:
                    self.metadata["build"] = "export LDFLAGS=" + self.metadata["env.LDFLAGS"] + os.linesep + \
                                             self.metadata["build"]
                elif only_make:
                    if "rpmMacros" in self.metadata:
                        self.metadata["rpmMacros"].append("%global build_optflags %build_optflags " + self.metadata["env.LDFLAGS"])
                    else:
                        self.metadata["rpmMacros"] = "%global build_optflags %build_optflags " + self.metadata["env.LDFLAGS"]

    def parse(self):
        """
        yaml转spec入口
        :return:
        """

        # customized int/float constructor for Loader of in PyYAML
        # to regard all numbers as plain string
        def _no_number(self, node):
            return str(self.construct_scalar(node))

        yaml.add_constructor('tag:yaml.org,2002:int', _no_number)
        yaml.add_constructor('tag:yaml.org,2002:float', _no_number)

        # loading data from YAML
        try:
            self.metadata.update(yaml.load(self.stream, Loader=yaml.FullLoader))
        except ValueError:
            logger.error('Please check if the input file is in YAML format')
        except TypeError:
            # empty can lead here
            logger.error('Empty yaml file: %s' % self.yaml_fpath)
        self.read_configures_file(self.conf_fpath)
        # 查找特殊段落，主包字段带判断时，不在模板中处理，根据单个字段拆解判断语句
        special_tmp_lines = []
        if "use.nativeCommands" in self.metadata.keys() and isinstance(self.metadata["use.nativeCommands"], list):
            with open("nativeCommands.json", "w") as f:
                for line in self.metadata["use.nativeCommands"]:
                    f.write(line)
        # remove rpmWhen
        self.metadata = remove_strings_keywords(origin_dict=self.metadata, keywords="rpmWhen ")
        # remove runtimePhase.
        self.metadata = remove_strings_keywords(origin_dict=self.metadata, keywords="runtimePhase.")
        # remove phase.
        self.metadata = remove_strings_keywords(origin_dict=self.metadata, keywords="phase.")
        # change struct of subpackage
        if "subpackage" in self.metadata and isinstance(self.metadata["subpackage"], dict):
            subpackage_list = []
            for sp_name, sp in self.metadata["subpackage"].items():
                if isinstance(sp, dict):
                    sp["name"] = sp_name
                    if "asWholeName" not in sp:
                        sp["asWholeName"] = True
                    subpackage_list.append(sp)
            self.metadata["subpackage"] = subpackage_list
        for some_key in LIST_KEYS:
            if some_key in self.metadata.keys() and some_key not in ["rpmMacros", "source", "patchset"]:
                if not self.metadata[some_key]:
                    self.metadata[some_key] = ""
                for index1, some_line in enumerate(self.metadata[some_key]):
                    temp_line = ""
                    temp_line_list = some_line.split("%if") if "%if" in some_line or "%else" in some_line else []
                    if "%if" in some_line or "%else" in some_line:
                        while len(temp_line_list):
                            if "%else" in temp_line_list[-1]:
                                if len(temp_line_list) > 1:
                                    temp_line += "%else" + os.linesep + "%if " + temp_line_list[-1].replace(
                                        "%else ", "") + os.linesep
                                    temp_line_list.pop()
                                else:
                                    temp_line += "%else" + os.linesep + some_key + ": " + temp_line_list[-1].replace(
                                        "%else ", "") + os.linesep
                                    temp_line_list.pop()
                            else:
                                if len(temp_line_list) > 1:
                                    temp_line += "%if" + temp_line_list[-1] + os.linesep
                                    temp_line_list.pop()
                                else:
                                    temp_line += some_key + ": " + temp_line_list[-1] + os.linesep
                                    temp_line_list.pop()
                        if_count = len(re.findall("%if", some_line))
                        for _ in range(if_count):
                            temp_line += "%endif" + os.linesep
                        self.metadata[some_key][index1] = ""
                        special_tmp_lines.append(temp_line)
        final_paragra_key = os.linesep.join(special_tmp_lines)
        for requires_key, requires_new_key in REQUIRES_REPLACE.items():
            final_paragra_key = final_paragra_key.replace(requires_key, requires_new_key)
        final_paragra_key += os.linesep
        if "SpecialKey" in self.metadata:
            self.metadata["SpecialKey"] += final_paragra_key
        else:
            self.metadata["SpecialKey"] = final_paragra_key
        # verifying the sanity
        self.sanity_check()
        # change compile args
        self.trans_compile_args()
        if "prep" not in self.metadata.keys():
            logger.warn("no keywords prep, target spec file can't unzip package")

        # for convenience
        for mand_keywords in MAND_KEYS:
            if mand_keywords not in self.metadata.keys():
                logger.error("no keywords %s, target spec file can't run" % mand_keywords)
                return
        downloader = DownloadWorker(name=self.metadata["name"], package=self.metadata["name"])
        if "RpmLintIgnore" in self.metadata:
            rpmlintrc = "%s-rpmlintrc" % self.metadata['name']
            rpmlint = "from Config import *" + os.linesep
            for lint in self.metadata['RpmLintIgnore']:
                rpmlint = rpmlint + "addFilter(\"%s\")" + os.linesep % lint

            file = open(rpmlintrc, "w")
            file.write(rpmlint)
            file.close()
        # handling 'extraSources', extra separated files which need to be install
        # specific paths
        if 'source' in self.metadata and type(self.metadata['source'][0]) is dict:
            source_list = []
            for item_key, item in self.metadata['source'][0].items():
                source_list.append(item)
            self.metadata['source'] = source_list
        if "extraSources" in self.metadata:
            # confirm 'source' valid
            if 'source' not in self.metadata:
                self.metadata['source'] = []
            extra_srcs = []
            extra_install = ''
            count = len(self.metadata['source'])
            if count:
                for source in self.metadata['source']:
                    if "%{name}" in source and "name" in self.metadata:
                        source = source.replace("%{name}", self.metadata["name"])
                    if "%{version}" in source and "version" in self.metadata:
                        source = source.replace("%{version}", self.metadata["version"])
                    downloader.download(source)

            for extra_src in self.metadata['extraSources']:
                try:
                    file, path = list(map(str.strip, extra_src.split(';')))
                except:
                    file = extra_src.strip()
                    path = ''
                self.extras_filelist.append(os.path.join(path, file))
                extra_srcs.append(file)
                if path:
                    extra_install += ("mkdir -p %%{buildroot}%s" + os.linesep) % (path)
                extra_install += ("cp -a %%{SOURCE%s} %%{buildroot}%s" + os.linesep) % (count, path)
                count = count + 1
                downloader.download(extra_src)
            self.metadata['source'].extend(extra_srcs)
            self.metadata['ExtraInstall'] = extra_install

        # handle patches with extra options
        if "patchset" in self.metadata:
            patches = self.metadata['patchset']

            self.metadata['patchset'] = []
            self.metadata['PatchOpts'] = []
            for patch in patches:
                if isinstance(patch, str):
                    if isinstance(patches, dict) and isinstance(patches[patch], str):
                        self.metadata['patchset'].append(patches[patch])
                    else:
                        self.metadata['patchset'].append(patch)
                    self.metadata['PatchOpts'].append('-p1')
                elif isinstance(patch, dict):
                    self.metadata['patchset'].append(list(patch.keys())[0])
                    self.metadata['PatchOpts'].append(list(patch.values())[0])
                elif isinstance(patch, list):
                    self.metadata['patchset'].append(patch[0])
                    self.metadata['PatchOpts'].append(' '.join(patch[1:]))

        # clean up all boolean type keys, use the exists status to present bool value
        _cleanup_boolkeys(self.metadata)
        if "subpackage" in self.metadata:
            for sp in self.metadata["subpackage"]:
                _cleanup_boolkeys(sp)

        # check duplicate requires for base package
        if "subpackage" in self.metadata:
            autodep = "%{name} = %{epoch}:%{version}-%{release}" if 'epoch' in self.metadata else \
                "%{name} = %{version}-%{release}"

            for sp in self.metadata["subpackage"]:
                if 'requires' in sp and autodep in sp['requires'] and 'AutoDepend' in sp:
                    logger.warn(
                        'found duplicate requires for %s in sub-pkg:%s, please remove it' % (autodep, sp['name']))
                    sp['requires'].remove(autodep)
                    if not sp['requires']:
                        del sp['requires']

        # initialize extra flags for subpkgs
        if "subpackage" in self.metadata:
            for sp in self.metadata["subpackage"]:
                self.extra['subpkgs'][sp['name']] = copy.deepcopy(self.extra_per_pkg)
        if "autoSubPackages" in self.metadata:
            if 'subpackage' not in self.metadata:
                self.metadata['subpackage'] = []
            for asp in self.metadata["autoSubPackages"]:
                self.extra['subpkgs'][asp] = copy.deepcopy(self.extra_per_pkg)
                if asp in self.asp_templates:
                    self.metadata['subpackage'].append(self.asp_templates[asp])
                    # By default if the LocaleFilesPkgName isn't defined and we have
                    # lang subpackage the .lang file is assigned to lang package.
                    if asp == "lang" and 'LocaleFilesPkgName' not in self.metadata:
                        self.metadata['LocaleFilesPkgName'] = asp
                else:
                    unknown_asp_tmp = copy.deepcopy(self.asp_templates['unknown'])
                    unknown_asp_tmp['name'] = asp
                    self.metadata['subpackage'].append(unknown_asp_tmp)

        # detect the using UI widget, QT or Gtk2
        all_pkgbr = []
        if 'pkgBR' in self.metadata:
            all_pkgbr += self.metadata['pkgBR']
        if 'pkgConfigBR' in self.metadata:
            all_pkgbr += self.metadata['pkgConfigBR']

        if 'LocaleName' not in self.metadata and 'NoAutoLocale' not in self.metadata:
            # If LocaleName or NoAutoLocale isn't set lets search if there is 'intltool' build requirement
            # and set LocaleName to name.
            if "pkgBR" in self.metadata:
                for br in self.metadata['pkgBR']:
                    if br == 'intltool':
                        self.metadata['LocaleName'] = self.metadata['name']
                        break
        """ NOTE
        we need NOT to do the following checking:
         * whether auto-added requires(include pre/post/preun/postun) duplicated

        They should be checked by users manually.
        """

    def _lookup_pkgmeta(self, pkgname):
        """
        给空的子包赋予Name
        :param pkgname:
        :return:
        """
        if pkgname == 'main':
            return self.metadata

        try:
            for sp in self.metadata['subpackage']:
                if sp['Name'] == pkgname:
                    return sp
        except KeyError:
            # Not a available subpackage for 'pkgname'
            return {}

        # not found
        return {}

    def parse_files(self, files):
        """
        解析files字段
        :param files: 字段来源
        :return:
        """
        py_path_check = False
        if 'builder' in self.metadata and self.metadata['builder'] == 'python':
            py_path_check = True
            if 'buildArch' in self.metadata and self.metadata['buildArch'] == 'noarch':
                py_path = '%{python_sitelib}'
            else:
                py_path = '%{python_sitearch}'

        for pkg_name, v in files.items():
            pkg_meta = self._lookup_pkgmeta(pkg_name)

            if pkg_name == 'main':
                pkg_extra = self.extra
            else:
                pkg_extra = self.extra['subpkgs'][pkg_name]

            for l in v:
                # check and warn improper file path
                for prefix, macro in PATHMACROS:
                    if l.startswith(prefix):
                        logger.warn(('for %%files line: "%s"' + os.linesep) % (l,) + \
                                    '\tplease use %s to replace the leading path %s' % (macro, prefix))
                        break

                if re.match('\s*%exclude\s.*', l):
                    pass  # not match anyting excluded files
                elif re.match('.*\.info\..*', l) or re.match('.*(usr/share/info|%{_infodir}).*info\..*$', l):
                    p1 = re.compile('^%doc\s+(.*)')
                    l1 = p1.sub(r'\1', l)
                    pkg_extra['Infos'].append(l1)
                    pkg_extra['Info'] = True

                elif re.match('.*(usr/share|%{_datadir})/applications/.*\.desktop$', l):
                    if 'NoDesktop' not in self.metadata:
                        # any pkg (main and every sub-pkg) will affect global settings
                        self.extra['Desktop'] = True

                elif re.match('.*(/etc|%{_sysconfdir})/rc.d/init.d/.*', l) or \
                        re.match('.*(/etc|%{_sysconfdir})/init.d/.*', l) or \
                        re.match('.*%{_initddir}/.*', l) or \
                        re.match('.*%{_initrddir}/.*', l):
                    # legacy init scripts
                    pkg_extra['Service'] = True

                elif re.match('^/(lib|%{_lib})/systemd/system/[^/*]*.service$', l):
                    # new service for systemd
                    if 'NoSystemdService' not in self.metadata:
                        pkg_extra['SystemdService'] = True
                        service = l.split('systemd/system/')[-1]
                        if service not in pkg_extra['SystemdServices']:
                            pkg_extra['SystemdServices'].append(service)

                elif re.match('.*(%{_libdir}|%{_lib}|/lib|/usr/lib)/[^/]*[.*?]+so([.*?]+.*$|$)', l) or \
                        re.match('.*(/ld.so.conf.d/).*', l):
                    if pkg_name != 'devel' and not pkg_name.endswith('-devel'):
                        # 'devel' sub pkgs should not set Lib flags
                        pkg_extra['Lib'] = True

                elif re.match('.*(%{_libdir}|%{_lib}).*', l) and re.match('.*\.a$', l):
                    # if *.a found, set 'HasStatic' flag for MAIN pkg
                    self.extra['HasStatic'] = True

                elif re.match('.*\.schema.*', l):
                    comp = l.split()
                    if len(comp) > 1:
                        l = comp[1]
                    pkg_extra['Schema'] = True
                    pkg_extra['Schemas'].append(l)

                elif re.match('.*\/icons\/.*', l):
                    if 'NoIconCache' in pkg_meta and pkg_meta['NoIconCache'] == True:
                        # using "NoIconCache" to avoid cache explicitly
                        continue


                    pkg_extra['Icon'] = True

                # special checking for python packages
                if py_path_check:
                    if '%{python_sitelib}' in l or '%{python_sitearch}' in l:
                        if py_path not in l:
                            logger.error('please use %s in %%files to specify module installation path' % py_path)

        # check whether need to update desktop database
        if 'UpdateDesktopDB' in self.metadata:
            self.extra['DesktopDB'] = True
            if self.extra['Desktop'] is not True:
                logger.warn('"UpdateDesktopDB" specified but found no desktop files')

    def parse_existing(self, spec_fpath):
        """
        解析额外信息中的字段
        :param spec_fpath: spec文件
        :return:
        """
        sin = re.compile(r"^# >> ([^\s]+)\s*(.*)")
        sout = re.compile(r"^# << ([^\s]+)\s*(.*)")

        # temp vars
        recording = []
        record = False
        ingroup1 = ingroup2 = None
        files = {}
        install = {}
        build = {}
        clean = {}
        suggests = {}
        recommends = {}
        macros = {}  # macros added after name: field in .spec
        macros2 = {}  # macros added before %prep section in .spec
        setup = {}
        pre = {}
        preun = {}
        post = {}
        postun = {}
        check = {}  # extra headers
        start_line_num = 0
        line_num = 0
        for i in open(spec_fpath):
            line_num += 1
            i = i.strip()
            matchin = sin.match(i)
            matchout = sout.match(i)

            if matchin:
                ingroup1 = matchin.group(1)
                ingroup2 = matchin.group(2)
                if record:
                    logger.error('%s:%d "%s %s" placeholder starting without ending previous %s:%d "%s %s"' %
                                 (spec_fpath, line_num, matchin.group(1), matchin.group(2), spec_fpath,
                                  start_line_num, ingroup1, ingroup2))
                record = True
                recording = []
                start_line_num = line_num
                continue

            if matchout:
                if not record:
                    logger.error('%s:%d "%s %s" placeholder ending whithout starting' %
                                 (spec_fpath, line_num, matchout.group(1), matchout.group(2)))
                record = False

                if matchout.group(1) != ingroup1 or matchout.group(2) != ingroup2:
                    logger.error('%s:%d "%s %s" placeholder ending not match starting %s:%d "%s %s"' %
                                 (spec_fpath, line_num, matchout.group(1), matchout.group(2),
                                  spec_fpath, start_line_num, ingroup1, ingroup2))

                if not recording:
                    continue  # empty

                if matchout.group(2) and matchout.group(1) in ["files", "post", "postun", "pre", "preun"]:
                    if not matchout.group(2) in self.extra['subpkgs']:
                        logger.error('In %s:%d %s section for lost sub-package: %s. Please fix it and try again.' %
                                     (spec_fpath, line_num, matchout.group(1), matchout.group(2)))

                if matchout.group(1) == "files":
                    if matchout.group(2):
                        if matchout.group(2) in files:
                            logger.error('%s:%d two files %s section.' % (spec_fpath, line_num, matchout.group(2)))
                        files[matchout.group(2)] = recording
                    else:
                        if 'main' in files:
                            logger.error('%s:%d two files section.' % (spec_fpath, line_num))
                        files['main'] = recording
                elif matchout.group(1) == "post":
                    if matchout.group(2):
                        if matchout.group(2) in post:
                            logger.error('%s:%d two post %s section.' % (spec_fpath, line_num, matchout.group(2)))
                        post[matchout.group(2)] = recording
                    else:
                        if 'main' in post:
                            logger.error('%s:%d two post section.' % (spec_fpath, line_num))
                        post['main'] = recording
                elif matchout.group(1) == "postun":
                    if matchout.group(2):
                        if matchout.group(2) in postun:
                            logger.error('%s:%d two postun %s section.' % (spec_fpath, line_num, matchout.group(2)))
                        postun[matchout.group(2)] = recording
                    else:
                        if 'main' in postun:
                            logger.error('%s:%d two postun section.' % (spec_fpath, line_num))
                        postun['main'] = recording
                elif matchout.group(1) == "pre":
                    if matchout.group(2):
                        if matchout.group(2) in pre:
                            logger.error('%s:%d two pre %s section.' % (spec_fpath, line_num, matchout.group(2)))
                        pre[matchout.group(2)] = recording
                    else:
                        if 'main' in pre:
                            logger.error('%s:%d two pre section.' % (spec_fpath, line_num))
                        pre['main'] = recording
                elif matchout.group(1) == "preun":
                    if matchout.group(2):
                        if matchout.group(2) in preun:
                            logger.error('%s:%d two preun %s section.' % (spec_fpath, line_num, matchout.group(2)))
                        preun[matchout.group(2)] = recording
                    else:
                        if 'main' in preun:
                            logger.error('%s:%d two preun section.' % (spec_fpath, line_num))
                        preun['main'] = recording
                elif matchout.group(1) == "install":
                    if matchout.group(2) in install:
                        logger.error('%s:%d two install %s section.' % (spec_fpath, line_num, matchout.group(2)))
                    install[matchout.group(2)] = recording
                elif matchout.group(1) == "build":
                    if 'main' in build:
                        logger.error('%s:%d two build section.' % (spec_fpath, line_num))
                    build[matchout.group(2)] = recording
                elif matchout.group(1) == "clean":
                    if 'main' in clean:
                        logger.error('%s:%d two clean section.' % (spec_fpath, line_num))
                    clean[matchout.group(2)] = recording
                elif matchout.group(1) == "recommends":
                    if 'main' in recommends:
                        logger.error('%s:%d two clean section.' % (spec_fpath, line_num))
                    recommends[matchout.group(2)] = recording
                elif matchout.group(1) == "suggests":
                    if 'main' in suggests:
                        logger.error('%s:%d two clean section.' % (spec_fpath, line_num))
                    suggests[matchout.group(2)] = recording
                elif matchout.group(1) == "macros":
                    if 'main' in macros:
                        logger.error('%s:%d two macros section.' % (spec_fpath, line_num))
                    macros['main'] = recording
                elif matchout.group(1) == "macros2":
                    if 'main' in macros2:
                        logger.error('%s:%d two macros2 section.' % (spec_fpath, line_num))
                    macros2['main'] = recording
                elif matchout.group(1) == "setup":
                    if 'main' in setup:
                        logger.error('%s:%d two setup section.' % (spec_fpath, line_num))
                    setup['main'] = recording
                elif matchout.group(1) == "check" or \
                        matchout.group(1) == "check_scriptlets":
                    if 'main' in check:
                        logger.error('%s:%d two check section.' % (spec_fpath, line_num))
                    check['main'] = recording
                else:
                    logger.error('%s:%d unknown section.' % (spec_fpath, line_num))

            if record:
                recording.append(i)

        if record:
            logger.error('%s:%d "%s %s" placeholder starting without ending' %
                         (spec_fpath, start_line_num, ingroup1, ingroup2))

        content = {"files": files,
                   "install": install,
                   "build": build,
                   }

        if macros:
            content["macros"] = macros
        if macros2:
            content["macros2"] = macros2
        if setup:
            content["setup"] = setup
        if post:
            content["post"] = post
        if postun:
            content["postun"] = postun
        if pre:
            content["pre"] = pre
        if preun:
            content["preun"] = preun
        if clean:
            content["clean"] = clean
        if recommends:
            content["recommends"] = recommends
        if suggests:
            content["suggests"] = suggests

        if check and 'check' in self.metadata:
            content["check"] = check

        # checking whether both 'files' key and inline files exists
        if files:
            files_yaml = False
            if 'files' in self.metadata and self.metadata['files']:
                files_yaml = True
            elif 'subpackage' in self.metadata:
                for spkg in self.metadata['subpackage']:
                    if 'files' in spkg:
                        files_yaml = True
                        break

            if files_yaml:
                logger.warn('both "files" keyword and inline %file content in spec present')

        # try to remove duplicate '%defattr' in files list
        for _key in content['files']:
            self._check_dup_files(content['files'][_key])

        # checking duplicate 'rm -rf %{buildroot}'
        re_cleanup = re.compile(r'^(?:rm|\%\{__rm\})\W+-rf\W+(?:\$RPM_BUILD_ROOT|\%\{buildroot\})/?$')
        if 'install' in content and 'post' in content['install']:
            if re_cleanup.match(content['install']['post'][0]):
                logger.warn('duplicate buildroot cleanup found in the first line of install_post, remove it')

        return content

    def process(self, extra_content):
        """
        阅读老的spec文件并记录规则，并自动检测文件列表中的额外信息
        :param extra_content:额外信息
        :return:
        """
        # backup old spec file if needed
        if os.path.exists(self.specfile):
            self.new_spec = False

        specfile = self.specfile
        if not self.new_spec:
            self.extra['content'] = self.parse_existing(specfile)

        if extra_content:
            self.extra['content'].update(extra_content)

        if 'files' in self.extra['content']:
            files = copy.deepcopy(self.extra['content']['files'])
        else:
            files = {}

        if 'files' in self.metadata:
            if 'main' in files:
                files['main'] += self.metadata['files']
            else:
                files['main'] = self.metadata['files']
        if "subpackage" in self.metadata:
            for sp in self.metadata["subpackage"]:
                if 'files' in sp:
                    if sp['name'] in files:
                        files[sp['name']] += sp['files']
                    else:
                        files[sp['name']] = sp['files']

        self.parse_files(files)

        # adding automatic requires according %files
        _gen_auto_requires(self.metadata, self.extra)
        if "subpackage" in self.metadata:
            for sp in self.metadata["subpackage"]:
                _gen_auto_requires(sp, self.extra['subpkgs'][sp['name']], sp['name'])

        self._check_dup_ldconfig()
        if "subpackage" in self.metadata:
            for sp in self.metadata["subpackage"]:
                self._check_dup_ldconfig(sp['name'])

        # check duplicate other auto-scriptlets in %post/%postun
        self._check_dup_scriptlets()
        if "subpackage" in self.metadata:
            for sp_index, sp in enumerate(self.metadata["subpackage"]):
                for Sub_key in sp.keys():
                    if Sub_key in YAML_LINES_KEYWORDS:
                        temp_list = sp[Sub_key].split(os.linesep)
                        combine_str = combine_if_lines(temp_list)
                        self.metadata["subpackage"][sp_index][Sub_key] = combine_str.strip().strip(os.linesep)
                self._check_dup_scriptlets(sp["name"])
        if "rpmMacros" in self.metadata:
            for macros_index, macros_line in enumerate(self.metadata["rpmMacros"]):
                if "{os.linesep}" in macros_line:
                    self.metadata["rpmMacros"][macros_index] = macros_line.replace("{os.linesep}", os.linesep)

        self.metadata["builder"] = ""
        necessary_keys = ["name", "version", "meta.summary", "meta.license", "release", "meta.description"]
        for necessary_key in necessary_keys:
            if necessary_key not in self.metadata.keys():
                self.metadata[necessary_key] = ""
                logger.error("no such necessary key:" + necessary_key)
        target_metadata = self.metadata.copy()
        for some_key in self.metadata:
            if some_key.startswith("meta."):
                the_value = self.metadata[some_key]
                del target_metadata[some_key]
                real_key = some_key.replace("meta.", "")
                target_metadata[real_key] = the_value
            if some_key == "subpackage":
                for index0, sp in enumerate(self.metadata["subpackage"]):
                    if isinstance(sp, dict):
                        target_sp = sp.copy()
                        for sp_key in sp:
                            if sp_key.startswith("meta."):
                                this_value = sp[sp_key]
                                del target_sp[sp_key]
                                real_sp_key = sp_key.replace("meta.", "")
                                target_sp[real_sp_key] = this_value
                            if sp_key.startswith("files") and "%if" in sp_key and "filesJudgement" not in sp:
                                judge_list = sp_key.split("%if")[1:]
                                this_value = sp[sp_key]
                                del target_sp[sp_key]
                                target_sp["files"] = this_value
                                target_sp["filesJudgement"] = map(lambda x: ("%if" + x).strip(), judge_list)
                        target_metadata["subpackage"][index0] = target_sp
        self.metadata = target_metadata

        spec_content = Template(file=template_path + "/spec.tmpl",
                                searchList=[{
                                    'metadata': self.metadata,
                                    'extra': self.extra,
                                    'arch_split': arch_split,
                                    'keywords_if_config': self.keywords_if_config,
                                }]).respond()
        spec_content = self.collation_spec_content(spec_content)
        file = open(specfile, "w")
        file.write(spec_content)
        file.close()

    def collation_spec_content(self, content):
        """
        整理模板引擎处理过后的spec数据
        :param content:
        :return:
        """
        while "\n\n\n\n" in content:
            content = content.replace("\n\n\n\n", "\n\n\n")
        if "\n%endif\n%endif\n" in content:
            temp_text = content.split("\n%endif\n%endif\n")[0]
            if re.search("\n%if.*\n%if.*\n", temp_text) is not None:
                cutter1 = re.findall("\n%if.*\n%if.*\n", temp_text)[0]
                temp_text = temp_text.split(cutter1)[1]
                body_text = temp_text.replace("%endif\n", "")
                content = content.replace(temp_text, body_text)
        if re.search(r"\n\s*\\b", content) is not None:
            some_texts = re.findall(r"\n\s*\\b", content)
            for some_text in some_texts:
                content = content.replace(some_text, " ")
        # content = content.replace("\\\\\n", "\\\n")
        return content

    def read_configures_file(self, conf):
        """
        读取配置文件
        :param conf: 配置文件
        :return:
        """
        if os.path.exists(conf):
            try:  # 读取conf文件内容
                conf_content_f = open(conf, 'r')
                conf_content = conf_content_f.read()
                conf_content_f.close()
            except Exception as e:
                logger.info(str(e))
                conf_content = ""
        else:
            conf = "env.conf"
            conf_content = CONF_CONTENT
        cmake_text_worker = ToolChainCmakeTemplate()
        if "CmakeSet" in self.metadata.keys():
            cmake_text_worker.add_set_order(self.metadata["CmakeSet"])
        if "ConfigureOptions" in self.metadata.keys():
            conf_content += "export CONFIGURE_OPT" + "=" + self.metadata["ConfigureOptions"] + os.linesep
        if "MakeOptions" in self.metadata.keys():
            conf_content += "export MAKE_OPT" + "=" + self.metadata["MakeOptions"] + os.linesep
        conf_content_plus = cmake_text_worker.get_final_context()
        conf_content += conf_content_plus
        env_conf = open(os.path.basename(conf), "w")
        env_conf.write(conf_content)
        env_conf.close()

    def get_append_content(self, includes):
        """
        获取继承包的内容
        :param includes: 继承的包list
        :return:
        """
        # 读取Include中所继承的文件
        for include_member in includes:
            # 或者再定义一个map,key为字段，值为相对路径，如果key相同，就获取值 这样可以来获取到shell的相对位置
            if include_member["Repo"] == self.metadata["name"]:
                file_url = STOREHOUSE_URL + self.metadata["name"] + "/" + include_member["File"]
            else:
                file_url = STORE_FRAMEWORK_URL + include_member["Repo"] + "/" + include_member["File"]
            content_add = requests.get(file_url)
            include_content = yaml.load(content_add.text, Loader=yaml.FullLoader)
            if "Include" in include_content.keys() and include_content["Include"]:
                self.get_append_content(include_content["Include"])
            shell_url = change_yaml2sh_file(file_url)
            try:
                shell_include_f = requests.get(shell_url)
                shell_include = shell_include_f.text
            except Exception as e:
                logger.info(str(e))
                shell_include = ""
            if self.shell_fpath is None:
                try:
                    shell_content_f = open(change_yaml2sh_file(self.yaml_fpath), "r")
                    shell_content = shell_content_f.read()
                except IOError:
                    shell_content = ""
            else:
                shell_content_f = open(self.shell_fpath, "r")
                shell_content = shell_content_f.read()
            shell_content = update_shell_include(shell_content, shell_include)
            for _key in include_content.keys():
                if _key in YAML_CHAIN_SHELL_KEYWORDS or (_key == "Include" and shell_include):
                    if _key in self.metadata.keys():
                        self.update_shell_content(shell_content, _key)
                        continue
                    self.update_shell_content(shell_include, _key)
                    continue
                if _key in self.metadata.keys():
                    if type(include_content[_key]) != list:
                        continue
                    for item in include_content[_key]:
                        if item not in self.metadata[_key]:
                            self.metadata[_key].append(item)
                else:
                    self.metadata[_key] = include_content[_key]
            self.iterate_keys_sub(shell_content)
            break

    def iterate_keys_sub(self, content):
        """
        更新主包和子包中指向shell脚本的内容到主变量中
        :param content:
        :return:
        """
        for _key in YAML_CHAIN_SHELL_KEYWORDS:
            if _key in self.metadata.keys() and self.metadata[_key][0] == change_yaml2sh_file(
                    os.path.basename(self.yaml_fpath)):
                if len(self.metadata[_key]) == 2:
                    self.keywords_if_config[_key] = self.metadata[_key][1].replace("%if", os.linesep + "%if")
                self.update_shell_content(content, _key)
                if type(self.metadata[_key]) is str and self.metadata[_key].startswith("-p"):
                    self.metadata[_key] = "\\b" + self.metadata[_key]
            if "subpackage" in self.metadata.keys():
                for sub_package in self.metadata["subpackage"]:
                    if type(sub_package) == dict and _key in sub_package.keys() and sub_package[_key][0] == \
                            change_yaml2sh_file(os.path.basename(self.yaml_fpath)):
                        self.update_shell_content(content, _key, is_sub=True, sub_name=sub_package["name"])
                    elif type(sub_package) == dict and _key in sub_package.keys() and type(sub_package[_key]) == str:
                        sub_package[_key] = sub_package[_key].strip(os.linesep)
                    if _key in sub_package.keys() and type(sub_package[_key]) is str and sub_package[_key].startswith("-p"):
                        sub_package[_key] = "\\b" + sub_package[_key]

    def update_shell_content(self, shell_data, keywords, is_sub=False, sub_name=""):
        """
        更新shell函数字段继承而来的值
        :param shell_data: shell数据
        :param keywords: 关键字
        :param is_sub:
        :param sub_name:
        :return:
        """
        lower_keywords = keywords.lower()
        if "%if" in sub_name:
            sub_name = sub_name.split("%if")[0].strip()
        if is_sub and sub_name != "":
            lower_keywords = (lower_keywords + "_" + sub_name).strip()
        if "+" in lower_keywords and "\\+" not in lower_keywords:
            lower_keywords = lower_keywords.replace("+", "\\+")
        if "*" in lower_keywords and "\\*" not in lower_keywords:
            lower_keywords = lower_keywords.replace("*", "\\*")
        if re.search(lower_keywords + "\s*\(\)\s*\{", shell_data) is not None:
            cutter1 = re.findall(lower_keywords + "\s*\(\)\s*\{", shell_data)[0]
            temp_text = cutter1.join(shell_data.split(cutter1)[1:])
            temp_shell_keywords = SHELL_KEYWORDS.copy()
            temp_shell_keywords.remove(keywords.lower())
            for key2 in temp_shell_keywords:
                while re.search(os.linesep + key2 + ".*\(\)\s*\{", temp_text) is not None:
                    cutter2 = re.findall(os.linesep + key2 + ".*\(\)\s*\{", temp_text)[0]
                    temp_text = temp_text.split(cutter2)[0]
            if re.search(keywords.lower() + ".*\(\)\s*\{", temp_text) is not None:
                cutter3 = "}\n\n" + re.findall(keywords.lower() + ".*\(\)\s*\{", temp_text)[0]
                temp_text = temp_text.split(cutter3)[0]
            function_body = temp_text.strip(os.linesep).strip("}").strip(os.linesep)
            if is_sub:
                for sub in self.metadata["subpackage"]:
                    if (sub["name"] == sub_name or sub["name"].startswith(sub_name + " %if")) and sub[keywords][0] == change_yaml2sh_file(os.path.basename(self.yaml_fpath)):
                        sub[keywords] = function_body
            else:
                self.metadata[keywords] = function_body
        if keywords == "build":
            # 将configure函数的内容合并到build函数中
            if re.search(r"\nconfigure\(\)\s*\{\n", shell_data) is not None:
                cutter3 = re.findall("\nconfigure\(\)\s*\{", shell_data)[0]
                temp_text = split_shell_content(cutter3, shell_data, "configure")
                function_body = temp_text.strip(os.linesep).strip("}").strip(os.linesep)
                if type(self.metadata["build"]) == list:
                    self.metadata["build"] = ""
                self.metadata[keywords] = function_body + os.linesep + self.metadata[keywords]
