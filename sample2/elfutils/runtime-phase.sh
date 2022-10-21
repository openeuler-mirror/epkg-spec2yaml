#!/usr/bash

post_libs() {
-p /sbin/ldconfig
}

postun_libs() {
-p /sbin/ldconfig
}

post_libelf() {
-p /sbin/ldconfig
}

postun_libelf() {
-p /sbin/ldconfig
}

post_default-yama-scope() {
if [ -x /usr/lib/systemd/systemd-sysctl ] ; then
%sysctl_apply 10-default-yama-scope.conf
fi
}

post_debuginfod-client() {
-p /sbin/ldconfig
}

postun_debuginfod-client() {
-p /sbin/ldconfig
}

pre_debuginfod() {
getent group debuginfod >/dev/null || groupadd -r debuginfod
getent passwd debuginfod >/dev/null || \
  useradd -r -g debuginfod -d /var/cache/debuginfod -s /sbin/nologin \
          -c "elfutils debuginfo server" debuginfod
exit 0
}

post_debuginfod() {
%systemd_post debuginfod.service
}

postun_debuginfod() {
%systemd_postun_with_restart debuginfod.service
}

