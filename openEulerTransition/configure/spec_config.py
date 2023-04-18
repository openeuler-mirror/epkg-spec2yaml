SHELL_KEYWORDS = ["build", "install", "prep", "check", "clean", "pre", "preun", "pretrans", "post", "postun",
                  "posttrans", "configure", "transfiletriggerin", "transfiletriggerpostun", "triggerun"]
OBS_LINES_KEYWORDS = ["description", "files"]
RARE_KEYWORDS = ["triggerun", "transfiletriggerin", "transfiletriggerpostun"]
MAIN_SHELL_KEYWORDS = ["build", "install", "prep", "check", "clean"]
MACROS_KEYWORDS = ["%package_help"]

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
           'triggerun',
           'transfiletriggerin',
           'transfiletriggerpostun',
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
           'Prefix',
           'License',
           "Release",
           "Recommends",
           "ExclusiveArch")
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
                 'BuildArch',
                 'ExclusiveArch',
                 'LocaleName',
                 'LocaleOptions',
                 'Files',
                 'FilesInput',
                 'SupportOtherDistros',
                 'ExcludeArch',
                 'Recommends',
                 'Supplements',
                 'Prefix',
                 'OrderWithRequires',
                 'Suggests',
                 'IncludeSource',
                 'FilesJudgement',
                 'rpmMacros',
                 'rpmGlobal',
                 'useFlag'
                 ]

SPEC_EXTRA_KEYS = {
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

RPM_GLOBAL_MACROS = {
    "GNAT_arches": "%{GPRbuild_arches} %{generic_arches}",
    "GPRbuild_arches": "%{generic_arches}",
    "__7zip": "/usr/bin/7za",
    "___build_args": "-e",
    "___build_cmd": "%{?_sudo:%{_sudo} }%{?_remsh:%{_remsh} %{_remhost} }%{?_remsudo:%{_remsudo} }%{?_remchroot:"
                    "%{_remchroot} %{_remroot} }%{___build_shell} %{___build_args}",
    "___build_post": "RPM_EC=$?"
                     "for pid in $(jobs -p); do kill -9 ${pid} || continue; done"
                     "exit ${RPM_EC}"
                     "%{nil}",
    "___build_shell": "%{?_buildshell:%{_buildshell}}%{!?_buildshell:/bin/sh}",
    "___build_template": "#!%{___build_shell}"
                         "%{___build_pre}"
                         "%{nil}",
    "__apply_patch(qp:m:)": "%{lua:"
                            "local file = rpm.expand(\"%{1}\")"
                            "local num = rpm.expand(\"%{2}\")"
                            "if posix.access(file, "r") then"
                            "    local options = rpm.expand(\"%{-q} %{-p:-p%{-p*}} %{-m:-m%{-m*}}\")"
                            "    local scm_apply = rpm.expand(\"%__scm_apply_%{__scm}\")"
                            "    print(rpm.expand(\"%{uncompress:\"..file..\"} | \"..scm_apply.." "..options.."  "..file.." "..num..\"\n\"))"
                            "else"
                            "    print(\"echo 'Cannot read \"..file..\"'; exit 1;\"..\"\n\")"
                            "end}",
    "__ar": "ar",
    "__arch_install_post": "/usr/lib/rpm/check-buildroot",
    "nil": "%{!?nil}",
    "nim_arches": "%{generic_arches}",
    "nodejs_arches": "%{generic_arches}",
    "ocaml_natdynlink": "%{generic_arches}",
    "ocaml_native_compiler": "%{generic_arches}",
    "ocaml_native_profiling": "%{generic_arches}",
    "openEuler": "2",
    "optflags": "%{__global_compiler_flags} -m64 -mtune=generic -fasynchronous-unwind-tables -fstack-clash-protection",
}
