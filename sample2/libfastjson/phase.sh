#!/usr/bash

prep() {
%autosetup -p1


}

build() {
autoreconf -iv
export CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -Wl,-z,relro,-z,now -fstack-protector-strong"
%configure --enable-shared --disable-static

}

install() {
make V=1 DESTDIR=%{buildroot} install
rm -f %{buildroot}/usr/lib64/libfastjson.la

}

check() {
make V=1 check

}

