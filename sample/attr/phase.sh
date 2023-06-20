#!/usr/bin/env bash

prep() {
    %autosetup -n %{name}-%{version} -p1
}

build() {
    configure
    make %{?_smp_mflags}
}

configure() {
    %configure --disable-silent-rules
}

install() {
    %make_install
    # remove rpath
    chrpath -d $RPM_BUILD_ROOT%{_bindir}/attr
    chrpath -d $RPM_BUILD_ROOT%{_bindir}/getfattr
    chrpath -d $RPM_BUILD_ROOT%{_bindir}/setfattr
    
    
    # handle docs on our own
    rm -rf $RPM_BUILD_ROOT%{_docdir}/%{name}*
    
    # temporarily provide attr/xattr.h symlink until users are migrated (#1601482)
    ln -fs ../sys/xattr.h $RPM_BUILD_ROOT%{_includedir}/attr/xattr.h
    
    %find_lang %{name}
}

check() {
    if ./setfattr -n user.name -v value .; then
    make check || exit $?
    else
    echo '*** xattrs are probably not supported by the file system,' \
             'the test-suite will NOT run ***'
    fi
}

