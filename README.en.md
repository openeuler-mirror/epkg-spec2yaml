# adapter-transition

#### Description
Conversion tool used to store unified builds

#### Software Architecture
Software architecture description

#### Installation

1.  pip install openEulerTransition-0.0.1-py3-none-any.whl

#### Instructions

1.  python3 openEulerTransitionMain.py -p ***.spec
2.  openEulerTransition -p ***.spec

#### Contribution

1.  Fork the repository
2.  Create Feat_xxx branch
3.  Commit your code
4.  Create Pull Request


#### Gitee Feature

1.  You can use Readme\_XXX.md to support different languages, such as Readme\_en.md, Readme\_zh.md
2.  Gitee blog [blog.gitee.com](https://blog.gitee.com)
3.  Explore open source project [https://gitee.com/explore](https://gitee.com/explore)
4.  The most valuable open source project [GVP](https://gitee.com/gvp)
5.  The manual of Gitee [https://gitee.com/help](https://gitee.com/help)
6.  The most popular members  [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)


#### Change Keywords

1. Summary => meta.summary
2. URL  =>  meta.homepage         
3. %description =>  meta.description
4. Name => name
5. Version => version
6. Release => release
7. Licence => licence
8. Requires => requires
9. BuildRequires => buildRequires
10. Provides => provides
11. Obsoletes => obsoletes
12. Recommends => recommends
13. %global => rpmGlobal
14. %define => rpmGlobal
15. %undefine => rpmMacros
16. %bcond_with => useFlags +
17. %bcond_without => useFlags -
18. %prep => phase.sh: prep
19. %build => phase.sh: build+configure
20. %install => phase.sh: install
21. %check => phase.sh: check
22. %clean => phase.sh: clean
23. %post => runtimePhase.sh: post
24. %postun => runtimePhase.sh: postun
25. %posttrans => runtimePhase.sh: posttrans
26. %pre => runtimePhase.sh: pre
27. %preun => runtimePhase.sh: preun
28. %pretrans => runtimePhase.sh: pretrans
29. %triggerprein => runtimePhase.sh: triggerprein
30. %triggerin => runtimePhase.sh: triggerin
31. %triggerun => runtimePhase.sh: triggerun
32. %triggerpostun => runtimePhase.sh: triggerpostun
33. %filetriggerin => runtimePhase.sh: filetriggerin
34. %filetriggerun => runtimePhase.sh: filetriggerun
35. %filetriggerpostun => runtimePhase.sh: filetriggerpostun
36. %transfiletriggerin => runtimePhase.sh: transfiletriggerin
37. %transfiletriggerun => runtimePhase.sh: transfiletriggerun
38. %transfiletriggerpostun => runtimePhase.sh: transfiletriggerpostun
39. %files => files.yaml: files
40. %package => subpackage
41. %include => includeSource
42. Source* => source
43. Patch* => patchset
44. Conflict => conflict
45. %post -p <lua> => runtimePhase.lua: post
46. %changelog => changelog.md
47. Requires(pre) => requiresPre
48. Requires(preun) => requiresPreun
49. Requires(pretrans) => requiresPretrans
50. Requires(post) => requiresPost
51. Requires(postun) => requiresPostun
52. Requires(posttrans) => requiresPosttrans

#### change grammar
****
Condition field expression
* before: 

        %if %{with ***}
        BuildRequires: gcc
        %endif
* after:

        buildRequires when +***:
            gcc
****
"meta" expression
* before:

        Summary: %{summary}
        URL: https://***
        %description
        .....
* after:

        meta:
            summary: %{summary}
            homepage: https://***
            description: |
            ....
***
Version Values with Quotation Marks
* before:

        Version: 1.0
* after:

        version: "1.0"
****
Source expression
* before:

        Source0: ***.tar.gz
        Source1: ***.tar.gz.sig
* after:

        source:
            0: ***.tar.gz
            1: ***.tar.gz.sig
****
Patch expression
* before:

        Patch9001: ***.patch
        Patch9006: ***.patch
* after:

        patchset:
            9001: ***.patch
            9002: ***.patch
****
defineFlags expression
* before:

        %bcond_with openEuler
        %ifarch %{valgrind_arches} 
        %bcond_without valgrind 
        %else 
        %bcond_with valgrind 
        %endif
* after:

        defineFlags:
            -openEuler:
        defineFlags when arch in %%%{rpmGlobal.valgrind_arches}:
            +valgrind:
        defineFlags when arch not in %%%{rpmGlobal.valgrind_arches}:
            -valgrind:

****
rpmMacros expression
* before:

        %ifarch %{arm} 
        %define target %{_target_cpu}-%{_vendor}-linuxeabi 
        %endif
        %undefine with_docs
* after:

        rpmMacros: |
            %ifarch %{arm} 
            %define target %{_target_cpu}-%{_vendor}-linuxeabi 
            %endif
            %undefine with_docs
****
rpmGlobal expression
* before:

        %define GCC gcc 
        %define GXX g++
        %global x86_arches %{ix86} x86_64
* after:

        rpmGlobal:
        GCC: gcc
        GXX: g++
        x86_arches: "%{ix86} x86_64"
****
provides,obsoletes,requires and conflict expression
* before:

        Obsoletes: nss_db <= 2.28, nss_hesiod <= 2.28
        Provides: nss_db = %{version}-%{release}
        Requires: audit-libs >= 1.1.3
* after:

        obsoletes:
            - nss_db <= 2.28
            - nss_hesiod <= 2.28
        provides:
            - nss_db = %{version}-%{release}
        requires:
            - audit-libs >= 1.1.3
*****
Subpackage expression,subpackages are named to the full name.
* before:

        %package nss-devel
        Summary: ...
        Requires: ...
        %package -n nscd
        Summary:  Name caching service daemon. 
        Requires: %{name} = %{version}-%{release}
* after:

        subPackage.glibc-nss-devel:
            meta:
                summary: ...
            requires:
                - ...
        subPackage.nscd:
            meta:
                summary: Name caching service daemon. 
            requires:
                - "%{name} = %{version}-%{release}"
****
The prep, build, install, check, and clean commands are converted into functions in the phase.sh script.
The configure command in the build function is an independent function,If the configure command is in the
./configure format, "%{?add_configure_flags}\" is added to the previous line by default.
* before：

        %prep
        ...
        %build
        ...
        %configure ...\
        ...\
        %{nul}
        make
        %install
        ...
        %check
        ...
        %clean
        ...
* after:
  + phase.sh:(its exist as a function in the shell scripts)

        prep() {
            ...
        }
        configure() {
            %configure ...\
            ...\
            %{nil}
        }
        build() {
            ...
            configure
            ...
        }
        install() {
            ...
        }
        check() {
            ...
        }
        clean() {
            ...
        }
****
The contents of shell scripts such as pre, post, and triggerin are converted into functions in the runtimePhase.sh file.
If parameter input is involved, the contents start with #:rpm_macro_param and are written in the first line of the
function content.
* before:

        %pre
        ...
        %post -n nscd
        ...
        %postun -p /sbin/ldconfig devel
    ...
* after:
  + runtimePhase.sh:

        pre() {
            ...
        }
        subPackage.nscd.post() {
            ...
        }
        postun() {
            #:rpm_macro_param: -p /sbin/ldconfig
            ...
        }
****
The content of the lua script is written in runtimePhase.lua. The parameter input is written in the first line of the
function content in lua comment mode.
* before:

        %pre -p <lua>
        -- Check that the running kernel is new enough
        ...
        if rpm.vercmp(rel, required) < 0 then
          error("FATAL: kernel too old", 0)
        end
* after:
  + runtimePhase.lua:

        function pre() {
          --:rpm_macro_param: -p <lua>
          -- Check that the running kernel is new enough
          ...
          if rpm.vercmp(rel, required) < 0 then
             error("FATAL: kernel too old", 0)
          end
        }
***
Files and files of subpackages are expressed in multi-line character strings in file.yaml.
If parameter input is involved, write them in the first line starting with #:rpm_macro_param.
* before:

        %files -f glibc.filelist 
        %dir %{_prefix}/%{_lib}/audit
        %files -f common.filelist common 
        %dir %{_prefix}/lib/locale
* after:
    + files.yaml:

            files:rpm_macro_param: -f glibc.filelist
            files:
                %dir %{_prefix}/%{_lib}/audit
            subPackage.glibc-common.files:rpm_macro_param: -f glibc.filelist
            subPackage.glibc-common.files:
                %dir %{_prefix}/lib/locale
***
The macros of the subpackage are written in the rpmMacros of the subpackage.
* before:

        %package all-langpacks
        ...
        %{lua:
        ...
        end
        }
* after:

       subpackage.glibc-all-langpacks:
            ...
            rpmMacros:|
              %{lua:
              ...
              end
              }
***
The shell script uses this expression to express the path of the bash.
* before:

        %build
        ...
* after:

        #!/usr/bin/env bash
        build() {
          ...
        }
***
Expression converted from "%if" to "when". Multiple conditions can be concatenated with and, &&, or, | |, not, and!.
* before:

        %if %{with abc}
        %if %{without xyz}
* after:

        when +abc && -xyz
        或者
        when +abc and -xyz
***
"%%" represent macros of Layered-Customization.
* before:

        %if 0%{?abc}
* after:

        rpmWhen 0%{?abc}或者when %%{rpmGlobal.abc}
***
"%if x%{?abc} != x" equal to "0%{?abc}" equal to "0%{?abc} != 0"
* before:

        %if x%{?abc} != x
* after:

        when %%{abc}
***
"else" is changed to "when not" expression.
* before:

        %ifarch x86_64
        Requires: ...
        else
        Requires: ...
* after:

        requires when arch in x86_64: ...
        requires when arch not in x86_64: ...
***
* before:

        %ifnarch x86_64
* after:

        when arch not in x86_64
***
Macro defined in rpmGlobal, represented by %%{rpmGlobal.***}
* before:

        %if %{valgrind}
* after:

        when %%{rpmGlobal.valgrind}
***
Macro defined by the rpm system, represented by %%%{rpmGlobal.***}
* before:

        %if %{openEuler}
* after:

        when %%%{rpmGlobal.openEuler}
***
* before:

        %if ! 0%{?openEuler}
        Requires: ...
        %endif
        %if ! 0%{?_conf}
        Requires: ...
        %endif
* after:

        Requires when not %%%{rpmGlobal.openEuler}: ...
        Requires rpmWhen ! 0%{?_conf}: ...
***
For multi-condition judgment, the statement after "%if" is regarded as a whole, and "%if" is converted into when or rpmWhen.
* before:

        %if 0%{?openEuler} || 0%{?fedora} || 0%{?rhel}
* after:

        when 0%{?openEuler} || 0%{?fedora} || 0%{?rhel}
***
* before:

        "%{name}-common = %{version}-%{release}"
* after:

        "%%{name}-common = %%{version}-%%{release}"
***