#!/usr/bash

post_libfdisk() {
-p /sbin/ldconfig
}

postun_libfdisk() {
-p /sbin/ldconfig
}

post_libsmartcols() {
-p /sbin/ldconfig
}

postun_libsmartcols() {
-p /sbin/ldconfig
}

post_libmount() {
-p /sbin/ldconfig
}

postun_libmount() {
-p /sbin/ldconfig
}

post_libblkid() {
/sbin/ldconfig

[ -d /run/blkid ] || mkdir -p /run/blkid
for i in /etc/blkid.tab /etc/blkid.tab.old \
  /etc/blkid/blkid.tab /etc/blkid/blkid.tab.old
do
if [ -f "${i}" ]
then
mv "${i}" /run/blkid/ || :
fi
done
}

postun_libblkid() {
-p /sbin/ldconfig
}

pre_uuidd() {
getent group uuidd >/dev/null || groupadd -r uuidd
getent passwd uuidd >/dev/null || \
useradd -r -g uuidd -d /var/lib/libuuid -s /sbin/nologin \
    -c "UUID generator helper daemon" uuidd
exit 0
}

post_uuidd() {
%systemd_post uuidd
if [ $1 -eq 1 ]
then
/bin/systemctl start uuidd > /dev/null 2>&1 || :
fi
}

preun_uuidd() {
%systemd_preun uuidd
}

postun_uuidd() {
/sbin/ldconfig
%systemd_postun_with_restart uuidd
}

post_libuuid() {
-p /sbin/ldconfig
}

postun_libuuid() {
-p /sbin/ldconfig
}

post() {
[ -d /var/log ] || mkdir -p /var/log

touch /var/log/lastlog
chown root:root /var/log/lastlog
chmod 0644 /var/log/lastlog

if [ -x /usr/sbin/selinuxenabled ] && /usr/sbin/selinuxenabled
then
SECXT=`/usr/sbin/matchpathcon -n /var/log/lastlog 2> /dev/null`
if [ -n "$SECXT" ]
then
/usr/bin/chcon "$SECXT"  /var/log/lastlog >/dev/null 2>&1 || :
fi
fi
if [ ! -L /etc/mtab ]
then
ln -sf ../proc/self/mounts /etc/mtab || :
fi

}

