#!/usr/bin/env bash

prep() {
    %setup -q
    
    # Common patches
    %patch10 -p1 -b .PIE
    %patch16 -p1 -b .redhat_doc
    %patch72 -p1 -b .64bit
    %patch106 -p1 -b .rh490837
    %patch112 -p1 -b .rh645544
    %patch130 -p1 -b .libdb
    %patch157 -p1 -b .fips-tests
    %patch164 -p1 -b .rh1666814
    
    %patch6000 -p1
    %patch6001 -p1
    %patch9000 -p1
    
    %if %{with PKCS11}
    %patch135 -p1 -b .config-pkcs11
    cp -r bin/named{,-pkcs11}
    cp -r bin/dnssec{,-pkcs11}
    cp -r lib/dns{,-pkcs11}
    cp -r lib/ns{,-pkcs11}
    %patch136 -p1 -b .dist_pkcs11
    %patch149 -p1 -b .kyua-pkcs11
    %endif
    
    # Sparc and s390 arches need to use -fPIE
    %ifarch sparcv9 sparc64 s390 s390x
    for i in bin/named/{,unix}/Makefile.in; do
    sed -i 's|fpie|fPIE|g' $i
    done
    %endif
    
    sed -e 's|"$TOP/config.guess"|"$TOP_SRCDIR/config.guess"|' -i bin/tests/system/ifconfig.sh
    :;
}

build() {
    ## We use out of tree configure/build for export libs
    %define _configure "../configure"
    
    # normal and pkcs11 unit tests
    %define unit_prepare_build() \
      cp -uv Kyuafile "%{1}/" \
      find lib -name 'K*.key' -exec cp -uv '{}' "%{1}/{}" ';' \
      find lib -name 'Kyuafile' -exec cp -uv '{}' "%{1}/{}" ';' \
      find lib -name 'testdata' -type d -exec cp -Tav '{}' "%{1}/{}" ';' \
      find lib -name 'testkeys' -type d -exec cp -Tav '{}' "%{1}/{}" ';' \
    
    %define systemtest_prepare_build() \
      cp -Tuav bin/tests "%{1}/bin/tests/" \
      cp -uv version "%{1}" \
    
    CFLAGS="$CFLAGS $RPM_OPT_FLAGS"
    %if %{with TSAN}
    CFLAGS+=" -O1 -fsanitize=thread -fPIE -pie"
    %endif
    export CFLAGS
    export STD_CDEFINES="$CPPFLAGS"
    
    
    #sed -i -e \
    #'s/RELEASEVER=\(.*\)/RELEASEVER=\\1-RH/' \
    #version
    
    libtoolize -c -f; aclocal -I libtool.m4 --force; autoconf -f
    
    mkdir build
    
    %if %{with DLZ}
    # DLZ modules do not support oot builds. Copy files into build
    mkdir -p build/contrib/dlz
    cp -frp contrib/dlz/modules build/contrib/dlz/modules
    %endif
    
    pushd build
    LIBDIR_SUFFIX=
    export LIBDIR_SUFFIX
    configure_build
    %if %{with DNSTAP}
    pushd lib
    SRCLIB="../../../lib"
    (cd dns && ln -s ${SRCLIB}/dns/dnstap.proto)
    %if %{with PKCS11}
    (cd dns-pkcs11 && ln -s ${SRCLIB}/dns-pkcs11/dnstap.proto)
    %endif
    popd
    %endif
    
    %if %{with DOCPDF}
    # avoid using home for pdf latex files
    export TEXMFVAR="`pwd`"
    export TEXMFCONFIG="`pwd`"
    fmtutil-user --listcfg || :
    fmtutil-user --missing || :
    %endif
    
    %make_build
    
    # Regenerate dig.1 manpage
    pushd bin/dig
    make man
    popd
    pushd bin/python
    make man
    popd
    
    %if %{with DOC}
    make doc
    %endif
    
    %if %{with DLZ}
    pushd contrib/dlz/modules
    for DIR in mysql mysqldyn; do
    sed -e 's/@DLZ_DRIVER_MYSQL_INCLUDES@/$(shell mysql_config --cflags)/' \
            -e 's/@DLZ_DRIVER_MYSQL_LIBS@/$(shell mysql_config --libs)/' \
            $DIR/Makefile.in > $DIR/Makefile
    done
    for DIR in filesystem ldap mysql mysqldyn sqlite3; do
    make -C $DIR CFLAGS="-fPIC -I../include $CFLAGS $LDFLAGS"
    done
    popd
    %endif
    popd # build
    
    %unit_prepare_build build
    %systemtest_prepare_build build
}

configure_build() {
    %configure \
      --with-python=%{__python3} \
      --with-libtool \
      --localstatedir=%{_var} \
      --with-pic \
      --disable-static \
      --includedir=%{_includedir}/bind9 \
      --with-tuning=large \
      --with-libidn2 \
    %if %{with GEOIP2}
    --with-maxminddb \
    %endif
    %if %{with PKCS11}
    --enable-native-pkcs11 \
      --with-pkcs11=%{_libdir}/pkcs11/libsofthsm2.so \
    %endif
    --with-dlopen=yes \
    %if %{with GSSTSIG}
    --with-gssapi=yes \
    %endif
    %if %{with LMDB}
    --with-lmdb=yes \
    %else
    --with-lmdb=no \
    %endif
    %if %{with JSON}
    --without-libjson --with-json-c \
    %endif
    %if %{with DNSTAP}
    --enable-dnstap \
    %endif
    %if %{with UNITTEST}
    --with-cmocka \
    %endif
    --enable-fixed-rrset \
      --enable-full-report \
    ;
}

check() {
    %if %{with PKCS11} && (%{with UNITTEST} || %{with SYSTEMTEST})
    # Tests require initialization of pkcs11 token
    eval "$(bash %{SOURCE48} -A "`pwd`/softhsm-tokens")"
    %endif
    
    %if %{with TSAN}
    export TSAN_OPTIONS="log_exe_name=true log_path=ThreadSanitizer exitcode=0"
    %endif
    
    %if %{with UNITTEST}
    pushd build
    CPUS=$(lscpu -p=cpu,core | grep -v '^#' | wc -l)
    if [ "$CPUS" -gt 16 ]; then
    ORIGFILES=$(ulimit -n)
    ulimit -n 4096 || : # Requires on some machines with many cores
    fi
    export ISC_TASK_WORKERS=8
    make unit
    e=$?
    if [ "$e" -ne 0 ]; then
    echo "ERROR: this build of BIND failed 'make unit'. Aborting."
    exit $e;
    fi;
    
    [ "$CPUS" -gt 16 ] && ulimit -n $ORIGFILES || :
    popd
    ## End of UNITTEST
    %endif
    
    %if %{with SYSTEMTEST}
    # Runs system test if ip addresses are already configured
    # or it is able to configure them
    if perl bin/tests/system/testsock.pl
    then
    CONFIGURED=already
    else
    CONFIGURED=
    sh bin/tests/system/ifconfig.sh up
    perl bin/tests/system/testsock.pl && CONFIGURED=build
    fi
    if [ -n "$CONFIGURED" ]
    then
    set -e
    pushd build/bin/tests
    chown -R ${USER} . # Can be unknown user
    %make_build test 2>&1 | tee test.log
    e=$?
    popd
    [ "$CONFIGURED" = build ] && sh bin/tests/system/ifconfig.sh down
    if [ "$e" -ne 0 ]; then
    echo "ERROR: this build of BIND failed 'make test'. Aborting."
    exit $e;
    fi;
    else
    echo 'SKIPPED: tests require root, CAP_NET_ADMIN or already configured test addresses.'
    fi
    %endif
    :
}

install() {
    # Build directory hierarchy
    mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d
    mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/{bind,named}
    mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/named/{slaves,data,dynamic}
    mkdir -p ${RPM_BUILD_ROOT}%{_mandir}/{man1,man5,man8}
    mkdir -p ${RPM_BUILD_ROOT}/run/named
    mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/log
    
    #chroot
    for D in %{chroot_create_directories}
    do
    mkdir -p ${RPM_BUILD_ROOT}/%{chroot_prefix}${D}
    done
    
    # create symlink as it is on real filesystem
    pushd ${RPM_BUILD_ROOT}/%{chroot_prefix}/var
    ln -s ../run run
    popd
    
    # these are required to prevent them being erased during upgrade of previous
    touch ${RPM_BUILD_ROOT}/%{chroot_prefix}%{_sysconfdir}/named.conf
    #end chroot
    
    pushd build
    %make_install
    popd
    rpm -E %{_unitdir}
    
    # Remove unwanted files
    rm -f ${RPM_BUILD_ROOT}/etc/bind.keys
    
    # Systemd unit files
    mkdir -p ${RPM_BUILD_ROOT}%{_unitdir}
    install -m 644 %{SOURCE37} ${RPM_BUILD_ROOT}%{_unitdir}
    install -m 644 %{SOURCE38} ${RPM_BUILD_ROOT}%{_unitdir}
    install -m 644 %{SOURCE44} ${RPM_BUILD_ROOT}%{_unitdir}
    install -m 644 %{SOURCE46} ${RPM_BUILD_ROOT}%{_unitdir}
    
    %if %{with PKCS11}
    install -m 644 %{SOURCE47} ${RPM_BUILD_ROOT}%{_unitdir}
    %else
    # Not packaged without PKCS11
    find ${RPM_BUILD_ROOT}%{_includedir}/bind9/pk11 ${RPM_BUILD_ROOT}%{_includedir}/bind9/pkcs11 \
      -name '*.h' \! -name site.h -delete
    
    %endif
    
    mkdir -p ${RPM_BUILD_ROOT}%{_libexecdir}
    install -m 755 %{SOURCE41} ${RPM_BUILD_ROOT}%{_libexecdir}/setup-named-chroot.sh
    install -m 755 %{SOURCE42} ${RPM_BUILD_ROOT}%{_libexecdir}/generate-rndc-key.sh
    
    %if %{with PKCS11}
    install -m 755 %{SOURCE48} ${RPM_BUILD_ROOT}%{_libexecdir}/setup-named-softhsm.sh
    %endif
    
    install -m 644 %SOURCE3 ${RPM_BUILD_ROOT}/etc/logrotate.d/named
    mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig
    install -m 644 %{SOURCE1} ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig/named
    install -m 644 %{SOURCE49} ${RPM_BUILD_ROOT}%{_sysconfdir}/named-chroot.files
    
    %if %{with DLZ}
    pushd build
    pushd contrib/dlz/modules
    for DIR in filesystem ldap mysql mysqldyn sqlite3; do
    %make_install -C $DIR libdir=%{_libdir}/named
    done
    pushd ${RPM_BUILD_ROOT}/%{_libdir}/bind
    cp -s ../named/dlz_*.so .
    popd
    mkdir -p doc/{mysql,mysqldyn}
    cp -p mysqldyn/testing/README doc/mysqldyn/README.testing
    cp -p mysqldyn/testing/* doc/mysqldyn
    cp -p mysql/testing/* doc/mysql
    popd
    popd
    %endif
    
    # Install isc/errno2result.h header
    install -m 644 lib/isc/unix/errno2result.h ${RPM_BUILD_ROOT}%{_includedir}/bind9/isc
    
    # Remove libtool .la files:
    find ${RPM_BUILD_ROOT}/%{_libdir} -name '*.la' -exec '/bin/rm' '-f' '{}' ';';
    
    # PKCS11 versions manpages
    %if %{with PKCS11}
    pushd ${RPM_BUILD_ROOT}%{_mandir}/man8
    ln -s named.8.gz named-pkcs11.8.gz
    ln -s dnssec-checkds.8.gz dnssec-checkds-pkcs11.8.gz
    ln -s dnssec-dsfromkey.8.gz dnssec-dsfromkey-pkcs11.8.gz
    ln -s dnssec-importkey.8.gz dnssec-importkey-pkcs11.8.gz
    ln -s dnssec-keyfromlabel.8.gz dnssec-keyfromlabel-pkcs11.8.gz
    ln -s dnssec-keygen.8.gz dnssec-keygen-pkcs11.8.gz
    ln -s dnssec-revoke.8.gz dnssec-revoke-pkcs11.8.gz
    ln -s dnssec-settime.8.gz dnssec-settime-pkcs11.8.gz
    ln -s dnssec-signzone.8.gz dnssec-signzone-pkcs11.8.gz
    ln -s dnssec-verify.8.gz dnssec-verify-pkcs11.8.gz
    popd
    %endif
    
    # 9.16.4 installs even manual pages for tools not generated
    %if %{without DNSTAP}
    rm -f ${RPM_BUILD_ROOT}%{_mandir}/man1/dnstap-read.1* || true
    %endif
    %if %{without LMDB}
    rm -f ${RPM_BUILD_ROOT}%{_mandir}/man8/named-nzd2nzf.8* || true
    %endif
    
    pushd ${RPM_BUILD_ROOT}%{_mandir}/man8
    ln -s ddns-confgen.8.gz tsig-keygen.8.gz
    ln -s named-checkzone.8.gz named-compilezone.8.gz
    popd
    
    %if %{with DOC}
    mkdir -p ${RPM_BUILD_ROOT}%{_pkgdocdir}
    cp -a build/doc/arm/_build/html ${RPM_BUILD_ROOT}%{_pkgdocdir}
    rm -rf ${RPM_BUILD_ROOT}%{_pkgdocdir}/html/.{buildinfo,doctrees}
    # Backward compatible link to 9.11 documentation
    (cd ${RPM_BUILD_ROOT}%{_pkgdocdir} && ln -s html/index.html Bv9ARM.html)
    # Share static data from original sphinx package
    for DIR in %{python3_sitelib}/sphinx_rtd_theme/static/*
    do
    BASE=$(basename -- "$DIR")
    BINDTHEMEDIR="${RPM_BUILD_ROOT}%{_pkgdocdir}/html/_static/$BASE"
    if [ -d "$BINDTHEMEDIR" ]; then
    rm -rf "$BINDTHEMEDIR"
    ln -s "$DIR" "$BINDTHEMEDIR"
    fi
    done
    %endif
    %if %{with DOCPDF}
    cp -a build/doc/arm/Bv9ARM.pdf ${RPM_BUILD_ROOT}%{_pkgdocdir}
    %endif
    
    # Ghost config files:
    touch ${RPM_BUILD_ROOT}%{_localstatedir}/log/named.log
    
    # configuration files:
    install -m 640 %{SOURCE16} ${RPM_BUILD_ROOT}%{_sysconfdir}/named.conf
    touch ${RPM_BUILD_ROOT}%{_sysconfdir}/rndc.{key,conf}
    install -m 644 %{SOURCE27} ${RPM_BUILD_ROOT}%{_sysconfdir}/named.root.key
    install -m 644 %{SOURCE36} ${RPM_BUILD_ROOT}%{_sysconfdir}/trusted-key.key
    mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/named
    
    # data files:
    mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/named
    install -m 640 %{SOURCE17} ${RPM_BUILD_ROOT}%{_localstatedir}/named/named.ca
    install -m 640 %{SOURCE18} ${RPM_BUILD_ROOT}%{_localstatedir}/named/named.localhost
    install -m 640 %{SOURCE19} ${RPM_BUILD_ROOT}%{_localstatedir}/named/named.loopback
    install -m 640 %{SOURCE20} ${RPM_BUILD_ROOT}%{_localstatedir}/named/named.empty
    install -m 640 %{SOURCE23} ${RPM_BUILD_ROOT}%{_sysconfdir}/named.rfc1912.zones
    
    # sample bind configuration files for \%\%doc:
    mkdir -p sample/etc sample/var/named/{data,slaves}
    install -m 644 %{SOURCE25} sample/etc/named.conf
    # Copy default configuration to \%\%doc to make it usable from system-config-bind
    install -m 644 %{SOURCE16} named.conf.default
    install -m 644 %{SOURCE23} sample/etc/named.rfc1912.zones
    install -m 644 %{SOURCE18} %{SOURCE19} %{SOURCE20}  sample/var/named
    install -m 644 %{SOURCE17} sample/var/named/named.ca
    for f in my.internal.zone.db slaves/my.slave.internal.zone.db slaves/my.ddns.internal.zone.db my.external.zone.db; do
    echo '@ in soa localhost. root 1 3H 15M 1W 1D
    ns localhost.' > sample/var/named/$f;
    done
    :;
    
    mkdir -p ${RPM_BUILD_ROOT}%{_tmpfilesdir}
    install -m 644 %{SOURCE35} ${RPM_BUILD_ROOT}%{_tmpfilesdir}/named.conf
    
    mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/rwtab.d
    install -m 644 %{SOURCE43} ${RPM_BUILD_ROOT}%{_sysconfdir}/rwtab.d/named
}

