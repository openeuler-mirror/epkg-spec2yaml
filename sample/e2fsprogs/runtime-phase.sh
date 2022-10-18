#!/usr/bash

post_devel() {
if [ -f %{_infodir}/libext2fs.info.gz ]; then
/sbin/install-info %{_infodir}/libext2fs.info.gz %{_infodir}/dir || :
fi
}

preun_devel() {
if [ $1 = 0 -a -f %{_infodir}/libext2fs.info.gz ]; then
/sbin/install-info --delete %{_infodir}/libext2fs.info.gz %{_infodir}/dir || :
fi
exit 0
}

