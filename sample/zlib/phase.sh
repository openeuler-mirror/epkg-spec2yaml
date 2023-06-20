#!/usr/bin/env bash

prep() {
    %setup -n %{name}-%{version}
    %patch0 -p1
    %ifarch aarch64
    %patch1 -p1
    %patch2 -p1
    %patch3 -p1
    %patch4 -p1
    %patch5 -p1
    %patch6 -p1
    %endif
    %patch6000 -p1
    %patch6001 -p1
    %patch6002 -p1
    %patch6003 -p1
    %patch6004 -p1
}

build() {
    export CFLAGS="$RPM_OPT_FLAGS"
    %ifarch aarch64
    CFLAGS+=" -DARM_NEON -O3"
    CFLAGS+=" -march=armv8-a+crc"
    %endif
    
    configure
    %make_build LDFLAGS="$LDFLAGS -Wl,-z,relro -Wl,-z,now"
    
    cd contrib/minizip
    autoreconf --install
    configure_1
    %make_build
}

configure() {
    %{?add_configure_flags} \
    ./configure --libdir=%{_libdir} --includedir=%{_includedir} --prefix=%{_prefix}
}

configure_1() {
    %configure --enable-static=no
}

install() {
    %make_install
    
    %make_install -C contrib/minizip
    rm -f $RPM_BUILD_ROOT%_includedir/minizip/crypt.h
    
    find $RPM_BUILD_ROOT -name '*.la' | xargs rm -f
}

check() {
    make test
}

