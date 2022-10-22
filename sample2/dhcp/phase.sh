#!/usr/bash

prep() {
%setup -n %{name}-%{version}
pushd bind
tar -xvf bind.tar.gz
ln -s bind-9* bind
popd
%autopatch -p1

sed -i -e 's|/var/db/|%{_localstatedir}/lib/dhcpd/|g' contrib/dhcp-lease-list.pl

}

build() {
autoreconf --verbose --force --install

CFLAGS="%{optflags} -fno-strict-aliasing" \
%configure --with-srv-lease-file=%{_localstatedir}/lib/dhcpd/dhcpd.leases \
    --with-srv6-lease-file=%{_localstatedir}/lib/dhcpd/dhcpd6.leases \
    --with-cli-lease-file=%{_localstatedir}/lib/dhclient/dhclient.leases \
    --with-cli6-lease-file=%{_localstatedir}/lib/dhclient/dhclient6.leases \
    --with-srv-pid-file=%{_localstatedir}/run/dhcpd.pid \
    --with-srv6-pid-file=%{_localstatedir}/run/dhcpd6.pid \
    --with-cli-pid-file=%{_localstatedir}/run/dhclient.pid \
    --with-cli6-pid-file=%{_localstatedir}/run/dhclient6.pid \
    --with-relay-pid-file=%{_localstatedir}/run/dhcrelay.pid \
    --with-ldap --with-ldapcrypto --with-ldap-gssapi --disable-static  --enable-log-pid --enable-paranoia --enable-early-chroot \
    --enable-binary-leases --with-systemd

make

}

install() {
%make_install

install -D -p -m 0755 %{SOURCE1} $RPM_BUILD_ROOT%{_sbindir}/dhclient-script

install -p -m 0644 %{SOURCE2} .

mkdir -p $RPM_BUILD_ROOT%{dhcpconfdir}/dhclient.d

mkdir -p $RPM_BUILD_ROOT%{nmconfdir}/dispatcher.d
install -p -m 0755 %{SOURCE3} $RPM_BUILD_ROOT%{nmconfdir}/dispatcher.d

install -D -p -m 0755 %{SOURCE4} $RPM_BUILD_ROOT%{_libdir}/pm-utils/sleep.d/56dhclient

mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_unitdir}
install -m 644 %{SOURCE6} $RPM_BUILD_ROOT%{_unitdir}
install -m 644 %{SOURCE7} $RPM_BUILD_ROOT%{_unitdir}

mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/dhcpd/
touch $RPM_BUILD_ROOT%{_localstatedir}/lib/dhcpd/dhcpd.leases
touch $RPM_BUILD_ROOT%{_localstatedir}/lib/dhcpd/dhcpd6.leases
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/dhclient/

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
cat <<EOF > %{buildroot}%{_sysconfdir}/sysconfig/dhcpd



EOF

mkdir -p $RPM_BUILD_ROOT%{dhcpconfdir}
cat << EOF > %{buildroot}%{dhcpconfdir}/dhcpd.conf
EOF
cat << EOF > %{buildroot}%{dhcpconfdir}/dhcpd6.conf
EOF

rm -f $RPM_BUILD_ROOT/usr/lib/debug/usr/sbin/dhcrelay-4.3.6-28.7.aarch64.debug

mkdir -p $RPM_BUILD_ROOT%{_datadir}/doc/dhcp-client
mkdir -p $RPM_BUILD_ROOT%{_datadir}/doc/dhcp-server

mv -f $RPM_BUILD_ROOT%{_sysconfdir}/dhclient.conf.example doc/examples/dhclient-dhcpv4.conf
mv -f $RPM_BUILD_ROOT%{_sysconfdir}/dhcpd.conf.example doc/examples/dhcpd-dhcpv4.conf
install -p -m 0755 doc/examples/dhclient-dhcpv4.conf $RPM_BUILD_ROOT%{_datadir}/doc/dhcp-client/dhclient.conf.example
install -p -m 0755 doc/examples/dhcpd-dhcpv4.conf $RPM_BUILD_ROOT%{_datadir}/doc/dhcp-server/dhcpd.conf.example

install -p -m 0755 doc/examples/dhclient-dhcpv6.conf $RPM_BUILD_ROOT%{_datadir}/doc/dhcp-client/dhclient6.conf.example
install -p -m 0755 doc/examples/dhcpd-dhcpv6.conf $RPM_BUILD_ROOT%{_datadir}/doc/dhcp-server/dhcpd6.conf.example
install -p -m 0755 server/dhcpd.conf.example $RPM_BUILD_ROOT%{_datadir}/doc/dhcp-server/dhcpd.conf.example

install -D -p -m 0644 contrib/ldap/dhcp.schema $RPM_BUILD_ROOT%{_sysconfdir}/openldap/schema/dhcp.schema

find $RPM_BUILD_ROOT -type f -name "*.la" -delete -print

}

check() {
make check

}

