#!/usr/bash

post_lockd() {
%systemd_post lvmlockd.service lvmlocks.service
}

preun_lockd() {
%systemd_preun lvmlockd.service lvmlocks.service
}

postun_lockd() {
%systemd_postun lvmlockd.service lvmlocks.service
}

post_cluster() {
if [ -e /run/clvmd.pid ]; then
/usr/sbin/clvmd -S || echo "Failed to start clvmd."
fi
%systemd_post lvm2-clvmd.service lvm2-cluster-activation.service
}

preun_cluster() {
if [ "$1" = "0" ]; then
/sbin/lvmconf --disable-cluster
fi
%systemd_preun lvm2-clvmd.service lvm2-cluster-activation.service
}

postun_cluster() {
%systemd_postun lvm2-clvmd.service lvm2-cluster-activation.service
}

post_cmirror() {
%systemd_post lvm2-cmirrord.service
}

preun_cmirror() {
%systemd_preun lvm2-cmirrord.service
}

postun_cmirror() {
%systemd_postun lvm2-cmirrord.service
}

post_dbusd() {
%systemd_post lvm2-lvmdbusd.service
}

preun_dbusd() {
%systemd_preun lvm2-lvmdbusd.service
}

postun_dbusd() {
%systemd_postun lvm2-lvmdbusd.service
}

post_device-mapper-event() {
/sbin/ldconfig
%systemd_post dm-event.socket
systemctl enable dm-event.socket
systemctl start dm-event.socket >/dev/null 2>&1 || :
if [ -e %{_default_pid_dir}/dmeventd.pid ]; then
%{_sbindir}/dmeventd -R || echo "Failed to start dmeventd."
fi
}

preun_device-mapper-event() {
%systemd_preun dm-event.service dm-event.socket
}

postun_device-mapper-event() {
/sbin/ldconfig
}

post() {
/sbin/ldconfig
%systemd_post blk-availability.service lvm2-monitor.service
if [ "$1" = "1" ] ; then
systemctl enable lvm2-monitor.service
systemctl start lvm2-monitor.service >/dev/null 2>&1 || :
fi

%systemd_post lvm2-lvmpolld.socket
systemctl enable lvm2-lvmpolld.socket
systemctl start lvm2-lvmpolld.socket >/dev/null 2>&1 || :

}

preun() {
%systemd_preun blk-availability.service lvm2-monitor.service
%systemd_preun lvm2-lvmpolld.service lvm2-lvmpolld.socket

}

postun() {
%systemd_postun lvm2-monitor.service
%systemd_postun_with_restart lvm2-lvmpolld.service
/sbin/ldconfig

}

