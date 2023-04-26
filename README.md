# adapter-transition

#### Description
用来放统一构建的转换工具

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
40. %package => subPackages
41. %include => includeSource
42. Source* => sources
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
条件字段表达式
* before:
  + %if %{with ***}
  + BuildRequires: gcc
  + %endif
* after:
  + buildRequires when +***:
    + gcc
****
meta表达式
* before:
  + Summary: %{summary}
  + URL: https://***
  + %description
  + .....
* after:
  + meta:
    + summary: %{summary}
    + homepage: https://***
    + description: |
      + ....
***
版本值带引号
* before:
  + Version: 1.0
* after:
  + version: "1.0"
****
源文件表达式
* before:
  + Source0: ***.tar.gz
  + Source1: ***.tar.gz.sig
* after:
  + source:
    + 0: ***.tar.gz
    + 1: ***.tar.gz.sig
****
patch表达式
* before:
  + Patch9001: ***.patch
  + Patch9006: ***.patch
* after:
  + patchset:
    + 9001: ***.patch
    + 9002: ***.patch
****
宏定义useFlags
* before:
  + %bcond_with openEuler
  + %ifarch %{valgrind_arches} 
  + %bcond_without valgrind 
  + %else 
  + %bcond_with valgrind 
  + %endif
* after:
  + useFlags:
    + -openEuler
  + useFlags when arch in %{valgrind_arches}
    + +valgrind
  + useFlags when arch not in %{valgrind_arches}
    + -valgrind
****
宏定义rpmMacros
* before:
  + %ifarch %{arm} 
  + %define target %{_target_cpu}-%{_vendor}-linuxeabi 
  + %endif
  + %undefine with_docs
* after:
  + rpmMacros: |
    + %ifarch %{arm} 
    + %define target %{_target_cpu}-%{_vendor}-linuxeabi 
    + %endif
    + %undefine with_docs
****
宏定义rpmGlobal
* before:
  + %define GCC gcc 
  + %define GXX g++
  + %global x86_arches %{ix86} x86_64
* after:
  + rpmGlobal:
    + GCC: gcc
    + GXX: g++
    + x86_arches: "%{ix86} x86_64"
****
provides,obsoletes,requires,conflict表达式
* before:
  + Obsoletes: nss_db <= 2.28, nss_hesiod <= 2.28
  + Provides: nss_db = %{version}-%{release}
  + Requires: audit-libs >= 1.1.3
* after:
  + obsoletes:
    - \- nss_db <= 2.28
    - \- nss_hesiod <= 2.28
  + provides:
    - \- nss_db = %{version}-%{release}
  + requires:
    - \- audit-libs >= 1.1.3
*****
子包表达式，子包统一用全称名
* before:
  + %package nss-devel
  + Summary: ...
  + Requires: ...
  + %package -n nscd
  + Summary:  Name caching service daemon. 
  + Requires: %{name} = %{version}-%{release}
* after:
  + subPackage.glibc-nss-devel:
    + meta:
      + summary: ...
    + requires:
      + \- ...
  + subPackage.nscd:
    + summary: Name caching service daemon. 
    + requires:
      + \- "%{name} = %{version}-%{release}"
****
prep,build,install,check,clean转换到phase.sh脚本中以函数形式表达，build函数中的configure命令单独作为一个函数
* before：
  + %prep
  + ...
  + %build
  + ...
  + %configure ...\
  + ...\
  + %{nul}
  + make
  + %install
  + ...
  + %check
  + ...
  + %clean
  + ...
* after:
  + phase.sh:（shell脚本文件中以函数形式存在）
    + prep() {
      + ...
    + }
    + configure() {
      + %configure ...\
      + ...\
      + %{nil}
    + }
    + build() {
      + ...
      + configure
      + ...
    + }
    + install() {
      + ...
    + }
    + check() {
      + ...
    + }
    + clean() {
      + ...
    + }
****
pre,post,triggerin等shell脚本内容转换到runtimePhase.sh文件中以函数形式存在，如果涉及到参数输入，则以#:rpm_macro_param开头
写在函数内容第一行
* before:
  + %pre
  + ...
  + %post -n nscd
  + ...
  + %postun -p /sbin/ldconfig devel
  + ...
* after:
  + runtimePhase.sh(shell脚本文件中以函数形式存在):
    + pre() {
      + ...
    + }
    + subPackage.nscd.post() {
      + ...
    + }
    + postun() {
      + #:rpm_macro_param: -p /sbin/ldconfig
      + ...
    + }
****
lua脚本的内容写在runtimePhase.lua中，参数输入以lua注释的方式写在函数内容第一行
* before:
  + %pre -p <lua>
  + -- Check that the running kernel is new enough
  + ...
  + if rpm.vercmp(rel, required) < 0 then
  +   error("FATAL: kernel too old", 0)
  + end
* after:
  + runtimePhase.lua:
    + function pre() {
      + --:rpm_macro_param: -p <lua>
      + -- Check that the running kernel is new enough
      + ...
      + if rpm.vercmp(rel, required) < 0 then
      +   error("FATAL: kernel too old", 0)
      + end
    + }
***
* before:
  + %files -f glibc.filelist 
  + %dir %{_prefix}/%{_lib}/audit
  + %files -f common.filelist common 
  + %dir %{_prefix}/lib/locale
* after:
  + files.yaml(files的内容统一在files.yaml文件中表达，参数输入以注释:rpm_macro_param:的形式写在内容第一行):
    + files:
      + \#:rpm_macro_param: -f glibc.filelist
      + %dir %{_prefix}/%{_lib}/audit
    + subPackage.glibc-common.files:
      + \#:rpm_macro_param: -f glibc.filelist
      + %dir %{_prefix}/lib/locale
***
子包的宏写在子包的rpmMacros中
* before:
  + %package all-langpacks
  + ...
  + %{lua:
  + ...
  + end
  + }
* after:
  + subpackage.glibc-all-langpacks:
    + ...
    + rpmMacros:|
      + %{lua:
      + ...
      + end
      + }
***
shell脚本用这种表达式表达bash的路径
* before:
  + %build
  + ...
* after:
  + #!/usr/bin/env bash
  + build() {
    + ...
  + }
***
* before:
  + %if %{with abc}
  + %if %{without xyz}
* after:
  + when -abc when +xyz
***
* before:
  + %if 0%{?abc}
* after:
  + when %%{abc}
***
* before:
  + %if x%{?abc} != x
* after:
  + when %%{abc}
***
* before:
  + %ifarch x86_64
* after:
  + when arch in x86_64
***
* before:
  + %ifnarch x86_64
* after:
  + when arch not in x86_64
***
* before:
  + %if %{valgrind}
* after:
  + when %%{rpmGlobal.valgrind}
***
* before:
  + %if %{openEuler}
* after:
  + when %%%{rpmGlobal.openEuler}
***
* before:
  + %if ! 0%{?openEuler}
* after:
  + when not %%%{rpmGlobal.openEuler}
***
* before:
  + %if 0%{?openEuler} || 0%{?fedora} || 0%{?rhel}
* after:
  + when 0%{?openEuler} || 0%{?fedora} || 0%{?rhel}
***
* before:
  + "%{name}-common = %{version}-%{release}"
* after:
  + "%%{name}-common = %%{version}-%%{release}"
***