#!/usr/bin/env bash

post:bind-pkcs11() {
    # Initial installation
    %systemd_post named-pkcs11.service
}

preun:bind-pkcs11() {
    # Package removal, not upgrade
    %systemd_preun named-pkcs11.service
}

postun:bind-pkcs11() {
    # Package upgrade, not uninstall
    %systemd_postun_with_restart named-pkcs11.service
    
    # Fix permissions on existing device files on upgrade
}

post:bind-chroot() {
    %systemd_post named-chroot.service
    %chroot_fix_devices %{chroot_prefix}
    :;
}

posttrans:bind-chroot() {
    if [ -x /usr/sbin/selinuxenabled ] && /usr/sbin/selinuxenabled; then
    [ -x /sbin/restorecon ] && /sbin/restorecon %{chroot_prefix}/dev/* > /dev/null 2>&1;
    fi;
}

preun:bind-chroot() {
    # wait for stop of both named-chroot and named-chroot-setup services
    # on uninstall
    %systemd_preun named-chroot.service named-chroot-setup.service
    :;
}

postun:bind-chroot() {
    # Package upgrade, not uninstall
    %systemd_postun_with_restart named-chroot.service
}

pre() {
    if [ "$1" -eq 1 ]; then
    /usr/sbin/groupadd -g %{bind_gid} -f -r named >/dev/null 2>&1 || :;
    /usr/sbin/useradd  -u %{bind_uid} -r -N -M -g named -s /sbin/nologin -d /var/named -c Named named >/dev/null 2>&1 || :;
    fi;
    :;
}

post when +PKCS11() {
    %?ldconfig
    if [ -e "%{_sysconfdir}/selinux/config" ]; then
    %selinux_set_booleans -s targeted %{selinuxbooleans}
    %selinux_set_booleans -s mls %{selinuxbooleans}
    fi
    if [ "$1" -eq 1 ]; then
    # Initial installation
    [ -x /sbin/restorecon ] && /sbin/restorecon /etc/rndc.* /etc/named.* >/dev/null 2>&1 ;
    # rndc.key has to have correct perms and ownership, CVE-2007-6283
    [ -e /etc/rndc.key ] && chown root:named /etc/rndc.key
    [ -e /etc/rndc.key ] && chmod 0640 /etc/rndc.key
    else
    # Upgrade, use invalid shell
    if getent passwd named | grep ':/bin/false$' >/dev/null; then
    /sbin/usermod -s /sbin/nologin named
    fi
    # Checkconf will parse out comments
    if /usr/sbin/named-checkconf -p /etc/named.conf 2>/dev/null | grep -q named.iscdlv.key
    then
    echo "Replacing obsolete named.iscdlv.key with named.root.key..."
    if cp -Rf --preserve=all --remove-destination /etc/named.conf /etc/named.conf.rpmbackup; then
    sed -e 's/named\.iscdlv\.key/named.root.key/' \
            /etc/named.conf.rpmbackup > /etc/named.conf || \
          mv /etc/named.conf.rpmbackup /etc/named.conf
    fi
    fi
    fi
    %systemd_post named.service
    :;
}

preun when +PKCS11() {
    # Package removal, not upgrade
    %systemd_preun named.service
}

postun when +PKCS11() {
    %?ldconfig
    # Package upgrade, not uninstall
    %systemd_postun_with_restart named.service
    if [ -e "%{_sysconfdir}/selinux/config" ]; then
    %selinux_unset_booleans -s targeted %{selinuxbooleans}
    %selinux_unset_booleans -s mls %{selinuxbooleans}
    fi
}

triggerun() {
    #:rpm_macro_param:  -- bind < 32:9.9.0-0.6.rc1
    /sbin/chkconfig --del named >/dev/null 2>&1 || :
    /bin/systemctl try-restart named.service >/dev/null 2>&1 || :
    
    %ldconfig_scriptlets libs
    
    %if %{with PKCS11}
    %ldconfig_scriptlets pkcs11-libs
    %endif
}

