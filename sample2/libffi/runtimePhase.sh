#!/usr/bash

post:help() {
/sbin/install-info --info-dir=%{_infodir} %{_infodir}/libffi.info.gz || :
}

preun:help() {
if [ $1 = 0 ] ;then
/sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/libffi.info.gz || :
fi
}

