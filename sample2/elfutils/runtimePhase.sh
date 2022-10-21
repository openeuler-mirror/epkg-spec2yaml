#!/usr/bash

post:libs() {
-p /sbin/ldconfig
}

postun:libs() {
-p /sbin/ldconfig
}

post:libelf() {
-p /sbin/ldconfig
}

postun:libelf() {
-p /sbin/ldconfig
}

post:default-yama-scope() {
if [ -x /usr/lib/systemd/systemd-sysctl ] ; then
%sysctl_apply 10-default-yama-scope.conf
fi
}

post:debuginfod-client() {
-p /sbin/ldconfig
}

postun:debuginfod-client() {
-p /sbin/ldconfig
}

pre:debuginfod() {
getent group debuginfod >/dev/null || groupadd -r debuginfod
getent passwd debuginfod >/dev/null || \
  useradd -r -g debuginfod -d /var/cache/debuginfod -s /sbin/nologin \
          -c "elfutils debuginfo server" debuginfod
exit 0
}

post:debuginfod() {
%systemd_post debuginfod.service
}

postun:debuginfod() {
%systemd_postun_with_restart debuginfod.service
}

