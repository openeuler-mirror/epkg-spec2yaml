#!/usr/bash

prep() {
%autosetup -n LVM2.%{version} -p1

}

build() {
%configure --with-default-dm-run-dir=/run --with-default-run-dir=/run/lvm --with-default-pid-dir=/run --with-default-locking-dir=/run/lock/lvm --with-usrlibdir=%{_libdir} --enable-fsadm --enable-write_install --with-user= --with-group= --with-device-uid=0 --with-device-gid=6 --with-device-mode=0660 --enable-pkgconfig --enable-applib --enable-cmdlib --enable-dmeventd --enable-blkid_wiping %{?configure_cluster} %{?configure_cmirror} --with-udevdir=%{_prefix}/lib/udev/rules.d --enable-udev_sync --with-thin=internal --with-thin=internal --enable-lvmpolld %{?configure_lockd_dlm} %{?configure_lockd_sanlock} --enable-dbus-service --enable-notify-dbus --enable-dmfilemapd
make %{?_smp_mflags}

}

check() {
make run-unit-test

}

install() {
make install DESTDIR=%{buildroot}
make install_system_dirs DESTDIR=%{buildroot}
make install_systemd_units DESTDIR=%{buildroot}
make install_systemd_generators DESTDIR=%{buildroot}
make install_tmpfiles_configuration DESTDIR=%{buildroot}
make -C test install DESTDIR=%{buildroot}

}

