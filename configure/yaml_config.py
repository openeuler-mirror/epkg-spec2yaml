import os.path

YAML_CHAIN_SHELL_KEYWORDS = ["install", "prep", "build", "pre", "preun", "post", "postun", "check", "petrans",
                             "posttrans", "clean"]
YAML_LINES_KEYWORDS = ["meta.description"]
NEED_QUOTATION_KEYWORDS = ['provides', 'obsoletes', 'buildRequires', 'requires', 'requires(postun)', 'buildRoot',
                           'requires(pre)', 'preRequires', 'preReq', 'prereq', 'requires(preun)', 'provides',
                           'obsoletes', 'conflicts', 'buildConflicts', 'exclusiveArch', 'macros', 'orderWithRequires',
                           'requires(post)', 'requires(posttrans)', ]
MAY_QUOTATION_KEYWORDS = ['version', 'source', 'meta.description', 'meta.summary', 'patchset', 'files', 'filesInput',
                          'epoch', 'release', 'meta.license', 'recommends', 'suggests', 'excludeArch', "name",
                          "supplements", 'meta.homepage', 'prefix', 'includeSource', "filesJudgement"]

CONF_CONTENT = "export CC=/usr/bin/gcc" + os.linesep + "export CXX=/usr/bin/g++" + os.linesep + \
               "export BUILD_SYS=`uname -m`-openeuler-`uname -s`-gnu" + os.linesep + \
               "export HOST_SYS=`uname -m`-openeuler-`uname -s`-gnu"

REQUIRES_REPLACE = {"requiresPost:": "requires(post):", "requiresPostUn:": "requires(postun):",
                    "requiresPre:": "requires(pre):", "requiresPreUn:": "requires(preun):",
                    "requiresPretrans:": "requires(pretrans):", "requiresPosttrans:": "requires(posttrans):"}
