#!/usr/bash

post_help() {
/sbin/install-info --info-dir=%{_infodir} %{_infodir}/libffi.info.gz || :
}

preun_help() {
if [ $1 = 0 ] ;then
/sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/libffi.info.gz || :
fi
}

