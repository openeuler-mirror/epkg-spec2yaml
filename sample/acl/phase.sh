#!/usr/bin/env bash

prep() {
    %autosetup -n %{name}-%{version} -p1
}

build() {
    configure
    %make_build
}

configure() {
    %configure
}

install() {
    %make_install
    %delete_la_and_a
    rm -rf $RPM_BUILD_ROOT%{_docdir}/%{name}*
    
    %find_lang %{name}
}

check() {
    # permissions.test needs 'daemon' users to be in the 'bin' group. If not, stop this test.
    if test 0 = "$(id -u)"; then
    sed -e 's|test/root/permissions.test||' -i test/Makemodule.am Makefile.in Makefile
    fi
    # setfacl.test needs 'bin' users to have the access to build dir. If not, stop this test.
    if ! runuser -u bin -- "${PWD}/setfacl" --version; then
    sed -e 's|test/root/setfacl.test||' -i test/Makemodule.am Makefile.in Makefile
    fi
    
    %make_build check
}

