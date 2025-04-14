## references
```
wfg /c/eulermaker/fedora_specs% git grep -ho '%bcond_with.*'|sed -E 's/\s+/ /'|sc
   1093 %bcond_without check
    397 %bcond_without tests
    245 %bcond_with tests
    242 %bcond_without python2
    212 %bcond_with python2
    204 %bcond_without python3
    157 %bcond_with python3
    148 %bcond_with check
    109 %bcond_with bootstrap
     35 %bcond_without openmpi
     30 %bcond_with network
     29 %bcond_without flexiblas
     27 %bcond_without docs
     25 %bcond_without mpich
     22 %bcond_without doc
     21 %bcond_with doc
     18 %bcond_without libnm_glib
     18 %bcond_with libnm_glib
     18 %bcond_with docs
     17 %bcond_with gtk4
     16 %bcond_with suggests
     16 %bcond_without gtk4
     15 %bcond_with debug
     14 %bcond_with test
     13 %bcond_without python
     13 %bcond_with openmpi
     10 %bcond_without test
     10 %bcond_without bootstrap

wfg /c/eulermaker/fedora_specs% git grep -ho '%bcond .*'|sed -E 's/\s+/ /g'|sc
     29 %bcond bootstrap 0
     16 %bcond tests 1
     10 %bcond doc_pdf 1
      6 %bcond autoreconf 1
      4 %bcond manual 1}
      3 %bcond openmpi 1
      3 %bcond mpich 1
      2 %bcond xvfb_tests 1
      2 %bcond wayland 1
      2 %bcond vulkan 0
      2 %bcond usd 1
      2 %bcond usd 0
      2 %bcond testsuite 0
```

```
wfg /c/eulermaker/fedora_specs/srcspecs% git grep -h %if|sc
   1636 %if %{with ghc_prof}
   1519 %if %{with check}
   1067 %if %{with haddock}
    973 %if %{with tests}
    532 %if %{defined ghc_version}
    520 %if 0%{?fedora}
    430 %if %{with python2}
    406 %if %{with python3}
    269 %if 0%{?with_python2}
    268 %if %{without bootstrap}
    266 %if 0%{?with_python3}
    265 %if 0%{?rhel}
    225 %if %{with_zts}
    202 %if %{defined perl_bootstrap}
    199 %if %{with_tests}
    173 %if %{revision} >= 50
    170 %if %{dual_life} || %{rebuild_from_scratch}
    152 %if 0%{?with_doc}
    151 %if %{with docs}
    146 %if 0%{?fedora} || 0%{?rhel} > 7
    138 %ifarch %{ocaml_native_compiler}
    136 %ifarch x86_64
    119 %if 0%{?rhel} && 0%{?rhel} <= 7
    119 %if 0%{?el7}
    117 %if 0%{?sources_gpg} == 1
    116 %if %{with_range_dependencies}
    115 %if 0%{?rhel} == 7
    109 %if %{with openmpi}
    108 %if 0%{?tests}
    108 %if 0%{?fedora} || 0%{?rhel} >= 8
    102 %if ! (0%{?rhel})
    101 %if %{with doc}
    101 %if %{use_systemd}
    101 %if !%{defined perl_bootstrap}
     99 %if %{with mpich}
     91 %ifarch %{ix86}
     91 %if 0%{?with_python3_other}
     88 %if 0%{?rhel} && 0%{?rhel} < 8
     73 %if 0
     71 %if 0%{?commit:1}
     70 %ifarch s390x
     69 %if 0%{?_licensedir:1}
     66 %if %{undefined __pythondist_requires}
     65 %ifnarch %{ocaml_native_compiler}
     65 %ifarch %{java_arches}
     65 %ifarch %{ix86} x86_64
     65 %if !0%{?rhel}
     60 %if %{with_suggests}
     59 %if %{with bootstrap}
     56 %if %{buildall}
     56 %if (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30)
     55 %if 0%{?use_gitbare}
     54 %if %{with python}
     54 %ifarch %{arm}
     53 %if 0%{?fedora} >= 27 || 0%{?rhel} >= 8
     52 %if 0%{?fedora} || 0%{?rhel} >= 7
     52 %if !0%{?bootstrap}
     50 %if 0%{?suse_version}
     49 %if ! 0%{?rhel}
     47 %ifarch aarch64
     47 %if 0%{?fedora} >= 33
     44 %ifarch ppc64le
     42 %if ! 0%{?bootstrap}
     41 %ifnarch s390 s390x
     40 %if %{without flatpackage}
     40 %if %{include_normal_build}
     40 %if %{bootstrap}
     40 %if 0%{?with_tests}
     39 %ifnarch s390x
     39 %if %is_system_jdk
     38 %if %{include_fastdebug_build}
     38 %if %{include_debug_build}
     38 %if %{defined ghclibdir}
     37 %if %{with test}
     37 %if 0%{?with_docs}
     37 %if 0%{?flatpak}
     37 %if 0%{?fedora} >= 33 || 0%{?rhel} >= 9
     36 %if %{with java}
     36 %if 0%{?el6}
     35 %if %{?rhel}%{!?rhel:0} == 7
     35 %if 0%{?rhel} == 6
     34 %if %{with doc_pdf}
     34 %if 0%{?rhel} == 8
     34 %if 0%{?__isa_bits} == 64
     33 %if 0%{?fedora} >= 40
     32 %if %{with network}
     32 %if 0%{?fedora} >= 30
     31 %if %{with suggests}
     31 %if %{use_x11_tests}
     30 %if %{with debug}
     30 %if %{include_staticlibs}
     30 %if 0%{?with_selinux}
     30 %if 0%{?docs}
     29 %if !%{disable_python3}
     29 %if 0%{?rhel} >= 8
     29 %if 0%{?fedora} && 0%{?fedora} < 19
     28 %if %{with systemd}
     28 %if %{with main_python}
     28 %if "%{_lib}" == "lib64"
     28 %ifarch s390 s390x
     28 %if 0%{?wine_staging}
     28 %if 0%{?rhel} >= 7
     27 %if 0%{?with_devel}
     27 %if 0%{?rhel} >= 7 || 0%{?fedora}
     26 %if 0%{?with_openmpi}
     26 %if 0%{?with_check}
     26 %if 0%{?gitdate}
     25 %if %{with flexiblas}
     25 %ifarch sparcv9 ppc
     25 %ifarch armv7hl
     24 %if 0%{?rhel} >= 9
     24 %if 0%{?fedora} || 0%{?rhel} >= 9
     24 %if 0%{?enable_tests}
     23 %if 0%{?rhel} && 0%{?rhel} < 7
     23 %if 0%{?rhel} && 0%{?rhel} <= 6
     23 %if 0%{?fedora} || 0%{?rhel} > 6
     22 %if %{with_extras}
     22 %ifnarch %{ix86}
     22 %if 0%{?with_mpich}
     22 %if 0%{?use_release}
     21 %if %{with python3_other}
     21 %if %{with gdbm}
     21 %if %{with_animated}
     21 %if 0%{?rhel} && 0%{?rhel} < 9
     21 %if !0%{?rhel} || 0%{?rhel} >= 8
     21 %if 0%{?qt5}
     21 %if 0%{?py2}
     21 %if 0%{?bootstrap}
     20 %if %{with qt6}
     20 %if %{with qt5}
     20 %if %{with_python3}
     20 %if %{with bundled_ipython}
     20 %if 0%{?rhel} == 0
     20 %if 0%{?fedora} >= 19
     19 %if %{with_systemd}
     19 %if %{with rpmwheels}
     19 %if %{with libwbclient}
     19 %ifnarch %{ix86} x86_64
     19 %ifarch %{multilib_64_archs}
     19 %if 0%{?_with_systemd}
     19 %if 0%{!?perl_bootstrap:1}
     19 %if 0%{?fedora} < 36
     19 %if 0%{?fedora} >= 21
     19 %if 0%{?apidocs}
     18 %if %{with_systemtap}
     18 %if %{with debug_build}
     18 %ifarch ppc64
     18 %if 0%{?with_unit_test} && 0%{?with_devel}
     18 %if 0%{?webkit}
     18 %if 0%{?el8}
     18 %if 0%{?complex}
     17 %if %{with server}
     17 %if %with gtk4
     17 %if %{py3default}
     17 %if %opt
     17 %ifnarch %{ix86} %{arm}
     17 %if %{build_libquadmath}
     17 %if %{build_libasan}
     17 %if %{build_go}
     17 %ifarch %{qt5_qtwebengine_arches}
     16 %if %{with zts}
     16 %if %{with_python2}
     16 %if %{with perl}
     16 %if %{with manual}
     16 %if %{with hadrian}
     16 %if %{with_doc}
     16 %ifnarch %{arm}
     16 %if !%{disable_python2} || !%{disable_python3}
     16 %if %{build_libitm}
     16 %ifarch x86_64 aarch64
     16 %ifarch ppc
     16 %if 0%{?with_asl}
     16 %if 0%{?usesnapshot}
     16 %if 0%{?rhel} && 0%{?rhel} == 7
     16 %if 0%{?qt4}
     16 %if 0%{?fedora} >= 32
     15 %if %{with testsuite}
     15 %if %{WITH_SELINUX}
     15 %if %with libnm_glib
     15 %if %{oldrhel}
     15 %ifnarch x86_64
     15 %ifnarch sparcv9 sparc64 ppc ppc64 ppc64p7
     15 %ifarch sparc64 ppc64 ppc64p7
     15 %if ! 0%{?with_bundled}
     15 %if 0%{?fedora} > 27
     14 %if %{with_mpi}
     14 %if %{with_java}
     14 %if %{build_libubsan}
     14 %if %{build_libatomic}
     14 %if %{build_d}
     14 %ifarch %{valgrind_arches}
     14 %ifarch %{power64}
     14 %ifarch i686
     14 %ifarch %{arm} aarch64
     14 %if 0%{?with_octave}
     14 %if 0%{?qtchooser}
     14 %if 0%{?fedora} < 30
     14 %if 0%{?fedora} >= 21 || 0%{?rhel} >= 8
     13 %if %{with_mpich}
     13 %if %{with autoreconf}
     13 %if %systemd
     13 %ifnarch armv7hl aarch64
     13 %if %{is_release_build -- %{?1}}
     13 %ifarch riscv64
     13 %if 0%{?with_systemd}
     13 %if 0%{?with_fortran}
     13 %if 0%{?rhel} > 7
     13 %if 0%{?_qt5_examplesdir:1}
     13 %if 0%{?fedora} >= 39
     13 %if 0%{?fedora} >= 24
     13 %if 0%{?arch64}
     12 %if %{with pthread}
     12 %if %{with man_page}
     12 %if %{with_loop}
     12 %if %{with html}
     12 %if %{with_docs}
     12 %if %{with dc} || %{with testsuite}
     12 %if %build64
     12 %ifarch %java_arches
     12 %if 0%{?with_python}
     12 %if 0%{verify_tarball_signature}
     12 %if 0%{?need_bootstrap_set} < 1
     12 %if 0%{?__isa_bits} == 32
     12 %if 0%{?fedora} >= 32 || 0%{?rhel} >= 9
     12 %if 0%{?fedora} > 23
     12 %if 0%{?fedora} >= 18 || 0%{?rhel} >= 7
     11 %if %{with tcl}
     11 %if %{with_qemu}
     11 %if %{with_lxc}
     11 %if %{with gui}
     11 %if %{with galera}
     11 %if %{with console}
     11 %if %{modular_conf}
     11 %if %{JAVA}
     11 %if !%{disable_systemd}
     11 %if ! %{defined perl_bootstrap}
     11 %if %{build_objc}
     11 %ifarch sparc64
     11 %ifarch %{arm} %{ix86}
     11 %if 0%{?usegit} >= 1
     11 %if 0%{?fedora} >= 38
     11 %if 0%{?fedora} < 28 && 0%{?rhel} < 8
     11 %if ! 0%{?eln}
     10 %if %{with wx}
     10 %if %{with_static}
     10 %if %{with serial}
     10 %if %{with quota_enables_rpc}
     10 %if %{with_py2}
     10 %if %{with_openmpi}
     10 %if %{with mono}
     10 %if %{with mingw}
     10 %if %{with gtk4}
     10 %if %{with_asl}
     10 %if %{?rhel}%{!?rhel:0} == 8
     10 %if %{build_ada}
     10 %if 0%{?rhel} < 8
     10 %if 0%{?rhel} > 6 || 0%{?fedora}
     10 %if 0%{?rhel} == 5
     10 %if ! 0%{?flatpak}
     10 %if 0%{?fedora} >= 36
     10 %if 0%{?fedora} >= 31
     10 %if 0%{?fedora} >= 25
     10 %if 0%{?fedora} < 19
     10 %if 0%{?fedora} >= 18
     10 %if 0%{?el5}
```

```
wfg /c/eulermaker/fedora_specs/2yamls% git grep -h '0%{[^}]\+}'
    355 release: 10%{?dist}
    281     %if 0%{?fedora}
    232 release: 20%{?dist}
    180     %if 0%{?with_python3}
    166     %if 0%{?rhel}
    148     %if 0%{?with_python2}
    137 release: 30%{?dist}
    101     %if ! (0%{?rhel})
     92 buildRequires rpmWhen 0%{?fedora}:
     86     %if 0%{?fedora} || 0%{?rhel} > 7
     69     %if 0%{?_licensedir:1}
     66     %if 0%{?rhel} == 7
     65     %if 0%{?el7}
     64     %if 0%{?with_doc}
     57     %if 0%{?tests}
     56 release: 40%{?dist}
     50     %if 0%{?with_python3_other}
     50     %if 0%{?fedora} || 0%{?rhel} >= 8
     49     %if 0%{?rhel} && 0%{?rhel} <= 7
     47 buildRequires rpmWhen 0%{?tests}:
     46     %if !0%{?bootstrap}
     45     with_tests: "0%{!?_without_tests:1}"
     45     %if 0%{?use_gitbare}
     45     %if 0%{?commit:1}
     42     group rpmWhen (0%{?rhel} > 0 && 0%{?rhel} <= 8) || (0%{?fedora} >= 0 && 0%{?fedora} < 30): Development/Languages
     40     %if 0%{?rhel} && 0%{?rhel} < 8
     39 source rpmWhen 0%{?sources_gpg} == 1:
     39     %if 0%{?sources_gpg} == 1
     39 buildRequires rpmWhen 0%{?sources_gpg} == 1:
     37     %if 0%{?flatpak}
     36 buildRequires rpmWhen ! 0%{?rhel}:
     35     %if 0%{?suse_version}
     34     %if 0%{?fedora} || 0%{?rhel} >= 7
     32     %if 0%{?fedora} >= 33
     31     %if 0%{?fedora} >= 33 || 0%{?rhel} >= 9
     29     %if 0%{?fedora} && 0%{?fedora} < 19
     28     %if 0%{?__isa_bits} == 64
     27     %if !0%{?rhel}
     27 buildRequires rpmWhen 0%{?rhel}:
     26     with_zts: "0%{?__ztsphp:1}"
     26 source rpmWhen 0%{?commit:1}:
     25 buildRequires rpmWhen 0%{?with_python3}:
     23     %if 0%{?fedora} >= 40
     22     %if 0%{?rhel} >= 9
     22 buildRequires rpmWhen 0%{?fedora} || 0%{?rhel} >= 8:
     22 buildRequires rpmWhen 0%{?el7}:
     21     %if 0%{?with_docs}
     21     %if 0%{?rhel} == 6
     21 buildRequires rpmWhen 0%{?with_python2}:
     21 buildRequires rpmWhen 0%{?rhel} == 7:
     21 buildRequires rpmWhen ! 0%{?bootstrap}:
     20     requires rpmWhen 0%{?fedora}:
     20 requires rpmWhen 0%{?fedora}:
     20     %if 0%{?rhel} >= 8
     20     %if 0%{?rhel} >= 7 || 0%{?fedora}
     20     %if 0%{?rhel} && 0%{?rhel} <= 6
     19     %if 0%{?el6}
     19     %global with_tests   0%{?_with_tests:1}
     19     %global with_tests   0%{!?_without_tests:1}
     19 buildRequires rpmWhen ! 0%{?fedora} || 0%{?rhel} >= 8:
     19 buildRequires rpmWhen 0%{?fedora} || 0%{?rhel} > 7:
     18     %if 0%{?with_mpich}
     18     %if 0%{?bootstrap}
     17 release: 50%{?dist}
     17     %if 0%{?wine_staging}
     17     %if 0%{?rhel} >= 7
     17     %if 0%{?fedora} >= 21
     16     with_zts: "0%{!?_without_zts:%{?__ztsphp:1}}"
     16 subpackage.python2-%{srcname} rpmWhen 0%{?with_python2}:
     16 subpackage.python2-%{srcname}.files rpmWhen 0%{?with_python2}: |
     16 requires rpmWhen 0%{?rhel} && 0%{?rhel} <= 7:
     16 requires rpmWhen ! 0%{?fedora} >= 27 || 0%{?rhel} >= 8:
     16 recommends rpmWhen 0%{?fedora}:
     16     %if 0%{?with_openmpi}
     16     %if 0%{?fedora} >= 30
     16     %if 0%{?fedora} || 0%{?rhel} > 6
     16 buildRequires rpmWhen 0%{?with_tests}:
     15     %if 0%{?_with_systemd}
     15     %if 0%{?rhel} > 7
     15     %if ! 0%{?rhel}
     15     %if 0%{?fedora} >= 32 || 0%{?rhel} >= 9
     15     %if 0%{?fedora} >= 27 || 0%{?rhel} >= 8
     15     %if 0%{?fedora} || 0%{?rhel} >= 9
     15     %if 0%{?docs}
     14 subpackage.python%{python3_pkgversion}-%{srcname} rpmWhen 0%{?with_python3}:
     14 subpackage.python%{python3_pkgversion}-%{srcname}.files rpmWhen 0%{?with_python3}: |
     14 requires rpmWhen 0%{?fedora} >= 27 || 0%{?rhel} >= 8:
     14 recommends rpmWhen 0%{?fedora} || 0%{?rhel} >= 8:
     14     %if 0%{?with_selinux}
     14     %if 0%{?with_devel}
     14     %if 0%{?use_release}
     14 buildRequires rpmWhen ! 0%{?fedora}:
     13 subpackage.${{pkg.name}}-examples.files rpmWhen 0%{?_qt5_examplesdir:1}: |
     13 postun rpmWhen 0%{?rhel} && 0%{?rhel} <= 7() {
     13     %if 0%{?rhel} && 0%{?rhel} == 7
     13     %if (0%{?fedora} && 0%{?fedora} < 19) || (0%{?rhel} && 0%{?rhel} < 7)
     13     %if ! 0%{?bootstrap}
     13 buildRequires rpmWhen 0%{?rhel} != 7:
     13 buildRequires rpmWhen 0%{!?perl_bootstrap:1}:
     12     %if 0%{?with_unit_test} && 0%{?with_devel}
     12     %if 0%{?with_tests}
     12     %if 0%{?with_asl}
     12     %if 0%{?rhel} == 8
     12     %if 0%{?rhel} && 0%{?rhel} < 9
     12     %if 0%{?__isa_bits} == 32
     12     %if 0%{?complex}
     11     requires rpmWhen 0%{?rhel}:
     11 post rpmWhen 0%{?rhel} && 0%{?rhel} <= 7() {
     11     %if 0%{?rhel} && 0%{?rhel} < 7
     11     %if 0%{?qt5}
     11     %if 0%{?el8}
     11 buildRequires rpmWhen ! 0%{?fedora} || 0%{?rhel} > 7:
     11     buildRequires rpmWhen 0%{?fedora}:
     10 source rpmWhen 0%{?gitdate}:
     10 requires rpmWhen ! 0%{?fedora} || 0%{?rhel} > 7:
     10 posttrans rpmWhen 0%{?rhel} && 0%{?rhel} <= 7() {
     10     %if ! 0%{?with_bundled}
     10     %if 0%{?qtchooser}
     10     %if 0%{?fedora} >= 32
     10     %if 0%{?fedora} < 30
     10     %if 0%{?fedora} < 28 && 0%{?rhel} < 8
     10     %if 0%{?fedora} < 19
     10     %if 0%{?apidocs}
     10 buildRequires rpmWhen 0%{?with_python3_other}:
     10 buildRequires rpmWhen 0%{?rhel} && 0%{?rhel} < 8:
     10 buildRequires rpmWhen 0%{?fedora} >= 30:
     10 buildRequires rpmWhen 0%{?fedora} || 0%{?rhel} >= 7:
```

```
wfg /c/eulermaker/fedora_specs/2yamls% git grep -h '%{[^}]\+}'
   2319         - "%{name}%{?_isa} = %{version}-%{release}"
   2266     make %{?build_make_flags} %{?_smp_mflags}
   1731     %{_mandir}/man3/*
   1699         summary: "%{summary}"
   1628         - "%{name} = %{version}-%{release}"
   1568     %{perl_vendorlib}/*
   1445 release: 1%{?dist}
   1327     %{_fixperms} $RPM_BUILD_ROOT/*
   1042     0: "%{gosource}"
   1040     homepage: "%{gourl}"
   1010     %{make_build}
   1009     %{make_install}
    955             "%{summary}."
    947 name: "%{goname}"
    922     %{_bindir}/%{name}
    913     %{_fixperms} %{buildroot}/*
    875 release: 2%{?dist}
    842     %{?perl_default_filter}
    783      -f %{name}.lang
    778         %{common_description}
    760 release: 3%{?dist}
    736     %{_bindir}/*
    641 release: 4%{?dist}
    608 release: 5%{?dist}
    600 subpackage.python3-%{pypi_name}:
    595 subpackage.python3-%{pypi_name}.files: |
    588         - "%{name}-devel%{?_isa} = %{version}-%{release}"
    575     make pure_install DESTDIR=%{buildroot}
    559         - "%{name}-static = %{version}-%{release}"
    542     rpmMacros: "%{?python_provide:%python_provide python3-%{pypi_name}}"
    539     debug_package: "%{nil}"
    532     requires rpmWhen %{defined ghc_version}:
    532     %if %{with ghc_prof}
    532         - ghc-compiler = %{ghc_version}
    532     0: https://hackage.haskell.org/package/%{pkgver}/%{pkgver}.tar.gz
    531     pkgver: "%{pkg_name}-${{pkg.version}}"
    528 buildRequires rpmWhen %{with ghc_prof}:
    517 subpackage.python3-%{srcname}:
    515      -f %{name}.files
    513         - "%{name}-static%{?_isa} = %{version}-%{release}"
    511 subpackage.${{pkg.name}}-prof rpmWhen %{with ghc_prof}:
    511     -f %{name}-devel.files
    510 subpackage.python3-%{srcname}.files: |
    510 subpackage.${{pkg.name}}-prof.files:rpm_macro_param rpmWhen %{with ghc_prof}: |
    510 subpackage.${{pkg.name}}-doc rpmWhen %{with haddock}:
    510 subpackage.${{pkg.name}}-doc.files rpmWhen %{with haddock}: |
    510 subpackage.${{pkg.name}}-doc.files:rpm_macro_param rpmWhen %{with haddock}: |
    510         - (%{name}-devel and ghc-prof) 
    510     -f %{name}-prof.files
    510     -f %{name}-doc.files
    504             This package provides the Haskell %{pkg_name} profiling library.
    499     %find_lang %{name}
    490     - 'perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))'
    484     %setup -q -n %{pkgver}
    482             This package provides the Haskell %{pkg_name} library documentation.
    446 release: 6%{?dist}
    446     %autosetup -n %{pypi_name}-${{pkg.version}}
    444     %{gem_spec}
    442 release: 9%{?dist}
    432     %if %{with tests}
    431     mkdir -p %{buildroot}%{gem_dir}
    421     - "%{ix86}"
    416             This package provides the Haskell %{pkg_name} library development files.
    415     %{_fixperms} -c %{buildroot}
    413     %{_mandir}/man1/*
    401     rpmMacros: "%{?python_provide:%python_provide python3-%{srcname}}"
    392     %{_datadir}/applications/%{name}.desktop
    385     rm -rf %{pypi_name}.egg-info
    378     0: "%{pypi_source}"
    363 release: 11%{?dist}
    361     %exclude %{gem_cache}
    359 release: 8%{?dist}
    355 release: 10%{?dist}
    355     %{__perl} Makefile.PL INSTALLDIRS=vendor
    353     test -d %{packname}/src && (cd %{packname}/src; rm -f *.o *.so)
    349         "%{summary}."
    343     pushd .%{gem_instdir}
    340     %{gem_libdir}
    334     %dir %{gem_instdir}
    332 release: 7%{?dist}
    331 release: 12%{?dist}
    331     %doc %{gem_docdir}
    329     %setup -q -c -n %{packname}
    329     0: https://rubygems.org/gems/%{gem_name}-${{pkg.version}}.gem
    328     %{_datadir}/%{name}
    323     cp -a .%{gem_dir}/* \
    322 release: 13%{?dist}
    321     %{_libdir}/*.so
    319         - "%{name} = %{?epoch:%{epoch}:}%{version}-%{release}"
    303     find %{buildroot} -type f -name .packlist -delete
    301     rm -rf %{buildroot}
    301     %autosetup -n %{srcname}-${{pkg.version}}
    299 release: 16%{?dist}
    291         - "%{name}-common = %{version}-%{release}"
    290 release: 14%{?dist}
    289 release: 15%{?dist}
    289     mkdir -p %{buildroot}%{rlibdir}
    288     rm -f %{buildroot}%{rlibdir}/R.css
    288     %{rlibdir}/%{packname}/NAMESPACE
    287     %{rlibdir}/%{packname}/DESCRIPTION
    286     %{rlibdir}/%{packname}/INDEX
    285             %{buildroot}%{gem_dir}/
    284     %{rlibdir}/%{packname}/help
    283     %{rlibdir}/%{packname}/Meta
    283     %doc %{rlibdir}/%{packname}/html
    283     %dir %{rlibdir}/%{packname}
    281     %if 0%{?fedora}
    281     %{_bindir}/R CMD INSTALL -l %{buildroot}%{rlibdir} %{packname}
    279     %{rlibdir}/%{packname}/R
    271     %{_mandir}/man3/*.3*
    262     %{_libexecdir}/%{name}
    257     %if %{with python3}
    255     %{__python3} setup.py test
    244     %{_mandir}/man1/%{name}.1*
    241         - "%{name}-libs%{?_isa} = %{version}-%{release}"
    234 release: 19%{?dist}
    234     mkdir -p %{buildroot}%{_bindir}
    232             with "%{_libexecdir}/${{pkg.name}}/test".
    232 release: 20%{?dist}
    231     %doc %{gem_instdir}/README.md
    229     %{_bindir}/R CMD check %{packname}
    225     %{_libdir}/*.so.*
    225     %if %{with_zts}
    223     %{perl_vendorarch}/auto/*
    221 release: 18%{?dist}
    218      -f %{pyproject_files}
    214     %{!?_licensedir:%global license %%doc}
    214     %{_datadir}/%{name}/
    213     mkdir -p %{buildroot}%{_libexecdir}/%{name}
    211     make install DESTDIR=%{buildroot}
    210     %if %{with python2}
    209     chmod +x %{buildroot}%{_libexecdir}/%{name}/test
    208     cat > %{buildroot}%{_libexecdir}/%{name}/test << 'EOF'
    206     %{_libdir}/pkgconfig/%{name}.pc
    203     %{python3_sitelib}/%{pypi_name}/
    202 release: 17%{?dist}
    202     gem build ../%{gem_name}-%{version}.gemspec
    198     %{_includedir}/*
    197     %global shortcommit %(c=%{commit}; echo ${c:0:7})
    196     install -m 0755 -vd                     %{buildroot}%{_bindir}
    195     %{python3_sitelib}/*
    195     install -m 0755 -vp %{gobuilddir}/bin/* %{buildroot}%{_bindir}/
    193     %{__perl} Makefile.PL INSTALLDIRS=vendor NO_PACKLIST=1
    186     %{?mingw_package_header}
    184     export HARNESS_OPTIONS=j$(perl -e 'if ($ARGV[0] =~ /.*-j([0-9][0-9]*).*/) {print $1} else {print 1}' -- '%{?_smp_mflags}')
    183     cp -a t %{buildroot}%{_libexecdir}/%{name}
    181 release: 25%{?dist}
    180 release: 23%{?dist}
    180     %if 0%{?with_python3}
    179 release: 21%{?dist}
    176     0: https://cran.r-project.org/src/contrib/%{packname}_%{packver}.tar.gz
    173     %if %{revision} >= 50
    173     %global revision %(echo %{version} | cut -d. -f3)
    168         summary: "%{sum}"
    166 release: 22%{?dist}
    166         - "python%{python3_pkgversion}-devel"
    166     %if 0%{?rhel}
    166     %{gem_instdir}/Rakefile
    162             %{?mingw_debug_package}
    160     %{?python_enable_dependency_generator}
    160     %{python3_sitelib}/%{pypi_name}-%{version}-py%{python3_version}.egg-info
    156     %{python3_sitelib}/%{srcname}/
    156         - "%{name} = %{epoch}:%{version}-%{release}"
    154     %doc %{rlibdir}/%{packname}/NEWS.md
    151     cd %{_libexecdir}/%{name} && exec prove -I . -j "$(getconf _NPROCESSORS_ONLN)"
    150     summary: "%{sum}"
    148     %if 0%{?with_python2}
    146     %license %{rlibdir}/%{packname}/LICENSE
    145     rlibdir: "%{_libdir}/R/library"
    144     %setup -q -n %{gem_name}-${{pkg.version}}
    144 release: 29%{?dist}
    144 release: 26%{?dist}
    143     rlibdir: "%{_datadir}/R/library"
    143     %global gh_short     %(c=%{gh_commit}; echo ${c:0:7})
    141     %cmake %{?build_cmake_flags} \
    138 release: 28%{?dist}
    137 release: 30%{?dist}
    137     - "%{name}-libs%{?_isa} = %{version}-%{release}"
    137     %ifarch %{ocaml_native_compiler}
    133     %{_libdir}/pkgconfig/*.pc
    132     mkdir -p %{buildroot}%{_mandir}/man1
    130     %doc %{rlibdir}/%{packname}/doc
    130     %dir %{rlibdir}/%{packname}/libs
    129     %{rlibdir}/%{packname}/libs/%{packname}.so
    129 release: 24%{?dist}
    129     - "python%{python3_pkgversion}-devel"
    129     %{_includedir}/%{name}/
    129     %gobuild -o %{gobuilddir}/bin/$(basename $cmd) %{goipath}/$cmd
    129             "%{desc}"
    128     %setup -q -n %{gh_project}-%{gh_commit}
    128         - "python%{python3_pkgversion}-setuptools"
    128     %{python3_sitelib}/%{pypi_name}
    128     %{_libdir}/lib%{name}.so
    128     %find_lang %{name} --all-name --with-html
    128     %dir %{_pkgdocdir}
    127         - "%{name}-core%{?_isa} = %{version}-%{release}"
    127     %{_datadir}/appdata/%{name}.appdata.xml
    127     1: https://hackage.haskell.org/package/%{pkgver}/%{pkg_name}.cabal#/%{pkgver}.cabal
    125 release: 32%{?dist}
    125     gem build %{gem_name}.gemspec
    122     	%{nil}
    122         "%{desc}"
    121     gem unpack %{SOURCE0}
    121     %autosetup -n %{srcname}-${{pkg.version}} -p1
    119 release: 31%{?dist}
    118 release: 27%{?dist}
    116     %if %{with_tests}
    116     0: "%{url}/archive/v${{pkg.version}}/${{pkg.name}}-${{pkg.version}}.tar.gz"
    113     %{__perl} Build.PL installdirs=vendor
    112     %{gem_instdir}/Gemfile
    112     %{_datadir}/applications/*.desktop
    111     %license %{gem_instdir}/LICENSE
    111     ./Build install --destdir=%{buildroot} --create_packlist=0
    110     %dir %{_datadir}/%{name}
    109     rpmMacros: "%{?python_provide:%python_provide python%{python3_pkgversion}-%{srcname}}"
    109     %autosetup -p1 -n %{srcname}-${{pkg.version}}
    108     %{python3_sitelib}/__pycache__/*
    107 subpackage.python%{python3_pkgversion}-%{srcname}:
    106 subpackage.python%{python3_pkgversion}-%{srcname}.files: |
    106 release: 34%{?dist}
    106     mkdir -p $RPM_BUILD_ROOT%{_bindir}
    106     0: "%{url}/archive/${{pkg.version}}/${{pkg.name}}-${{pkg.version}}.tar.gz"
    105 release: 33%{?dist}
    104 release: 35%{?dist}
    103     mkdir -p $RPM_BUILD_ROOT%{_datadir}/appdata
    102     fontdocsex: "%{fontlicenses}"
    101     %{py3_build}
    101     %{_mandir}/man1/*.1*
    101     %if ! (0%{?rhel})
    101     %ghost %{crate_instdir}/Cargo.toml
```
