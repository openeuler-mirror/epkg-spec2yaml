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
# must have keys for 'main' package
MUSTHAVE = {'Release': '1'}

TAB = '    '  # 4space, instead of Tab
KEY_SYS = {
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
            'transfiletrigger\w+': 'transfileTrigger\w+',
            'check': 'Check',
            'prep': 'Prep',
            'include': 'IncludeSource',
            'Autoreq': 'AutoReq',
            'Autoprov': 'AutoProv',
            'Autoreqprov': 'AutoReqProv',
        }
