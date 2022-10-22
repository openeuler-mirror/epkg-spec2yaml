import os.path

YAML_CHAIN_SHELL_KEYWORDS = ["install", "prep", "build", "pre", "preun", "post", "postun", "check", "petrans",
                             "posttrans", "clean"]
YAML_LINES_KEYWORDS = ["meta.description"]
NEED_QUOTATION_KEYWORDS = ['Provides', 'Obsoletes', 'BuildRequires', 'Requires', 'Requires(postun)', 'BuildRoot',
                           'Requires(pre)', 'PreRequires', 'PreReq', 'Prereq', 'Requires(preun)', 'Provides',
                           'Obsoletes', 'Conflicts', 'BuildConflicts', 'ExclusiveArch', 'Macros', 'OrderWithRequires',
                           'Requires(post)', 'Requires(posttrans)', ]
MAY_QUOTATION_KEYWORDS = ['Version', 'Sources', 'Description', 'Summary', 'Patches', 'Files', 'FilesInput',
                          'Epoch', 'Release', 'License', 'Recommends', 'Suggests', 'ExcludeArch', "Name",
                          "Supplements", 'URL', 'Prefix', 'IncludeSource', "FilesJudgement"]

CONF_CONTENT = "export CC=/usr/bin/gcc" + os.linesep + "export CXX=/usr/bin/g++" + os.linesep + \
               "export BUILD_SYS=`uname -m`-openeuler-`uname -s`-gnu" + os.linesep + \
               "export HOST_SYS=`uname -m`-openeuler-`uname -s`-gnu"

REQUIRES_REPLACE = {"requiresPost:": "requires(post):", "requiresPostUn:": "requires(postun):",
                    "requiresPre:": "requires(pre):", "requiresPreUn:": "requires(preun):",
                    "requiresPretrans:": "requires(pretrans):", "requiresPosttrans:": "requires(posttrans):"}
