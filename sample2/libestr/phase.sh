#!/usr/bash

prep() {
%autosetup -n %{name}-%{version} -p1

}

build() {
%configure --disable-static --with-pic

%make_build

}

install() {
%make_install
rm -f %{buildroot}/%{_libdir}/*.{a,la}

}

