NEED_QUOTATION_KEYWORDS = ['Provides', 'Obsoletes', 'BuildRequires', 'Requires', 'Requires(postun)', 'BuildRoot',
                           'Requires(pre)', 'PreRequires', 'PreReq', 'Prereq', 'Requires(preun)', 'Provides',
                           'Obsoletes', 'Conflicts', 'BuildConflicts', 'ExclusiveArch', 'OrderWithRequires',
                           'Requires(post)', 'Requires(posttrans)', 'Version']
MAY_QUOTATION_KEYWORDS = ['Version', 'Sources', 'Description', 'Summary', 'Patches', 'Files', 'FilesInput',
                          'Epoch', 'Release', 'License', 'Recommends', 'Suggests', 'ExcludeArch', "Name",
                          "Supplements", 'URL', 'Prefix', 'IncludeSource', 'rpmMacros', "FilesJudgement", "rpmGlobal"]
LIST_KEY_REPLACE = {"BuildRequires": "buildRequires", "Requires": "requires", "Provides": "provides",
                    "Obsoletes": "obsoletes", "Requires(post)": "requiresPost", "Conflicts": "conflicts",
                    "Requires(postun)": "requiresPostUn", "Requires(pre)": "requiresPre",
                    "Requires(preun)": "requiresPreun", "Requires(pretrans)": "requiresPretrans",
                    "Requires(posttrans)": "requiresPosttrans"}
