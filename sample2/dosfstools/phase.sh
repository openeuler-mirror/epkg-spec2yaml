#!/usr/bash

prep() {
%autosetup -n %{name}-%{version} -p1

}

build() {
%configure --enable-compat-symlinks
%make_build CFLAGS="%{optflags} -D_LARGEFILE_SOURCE -D_FILE_OFFSET_BITS=64 -fno-strict-aliasing"

}

check() {
make check

}

install() {
%make_install

}

