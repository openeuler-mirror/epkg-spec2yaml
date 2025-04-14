
## convert to build.configure.flags

## references
```
wfg /c/eulermaker/fedora_specs/2yamls% gg -A3 'configure()'
4ti2/phase.sh:46:configure() {
4ti2/phase.sh-47-    %configure --enable-shared --disable-static
4ti2/phase.sh-48-
4ti2/phase.sh-49-}
--
AtomicParsley/phase.sh:14:configure() {
AtomicParsley/phase.sh-15-    %configure --prefix=%{_prefix}
AtomicParsley/phase.sh-16-
AtomicParsley/phase.sh-17-}
--
BibTool/phase.sh:19:configure() {
BibTool/phase.sh-20-    %configure --libdir=%{_datadir}
BibTool/phase.sh-21-
BibTool/phase.sh-22-}
--
BitchX/phase.sh:20:configure() {
BitchX/phase.sh-21-    %configure --with-plugins --with-ssl --enable-ipv6
BitchX/phase.sh-22-
BitchX/phase.sh-23-}
--
CCfits/phase.sh:12:configure() {
CCfits/phase.sh-13-    %configure --disable-static --with-cfitsio=%{_prefix} --with-cfitsio-include=%{_includedir}/cfitsio
CCfits/phase.sh-14-
CCfits/phase.sh-15-}
--
ClanLib/phase.sh:18:configure() {
ClanLib/phase.sh-19-    %configure --disable-dependency-tracking --disable-static --disable-docs
ClanLib/phase.sh-20-
ClanLib/phase.sh-21-}
--
ClanLib06/phase.sh:28:configure() {
ClanLib06/phase.sh-29-    %configure --disable-debug --enable-dyn --disable-directfb $ARCH_CONFIG_FLAGS
ClanLib06/phase.sh-30-
ClanLib06/phase.sh-31-}
--
Coin2/phase.sh:46:configure() {
Coin2/phase.sh-47-    %configure \
Coin2/phase.sh-48-      --includedir=%{coin_includedir} \
Coin2/phase.sh-49-      htmldir=%{coin_htmldir}/Coin \
--
Coin3/phase.sh:56:configure() {
Coin3/phase.sh-57-    %configure \
Coin3/phase.sh-58-      --includedir=%{coin_includedir} \
Coin3/phase.sh-59-      htmldir=%{coin_htmldir}/Coin \
--
ColPack/phase.sh:17:configure() {
ColPack/phase.sh-18-    %configure
ColPack/phase.sh-19-
ColPack/phase.sh-20-}
--
CriticalMass/phase.sh:15:configure() {
CriticalMass/phase.sh-16-    %configure
CriticalMass/phase.sh-17-
CriticalMass/phase.sh-18-}
--
EMBOSS/phase.sh:64:configure() {
EMBOSS/phase.sh-65-    %configure \
EMBOSS/phase.sh-66-      --includedir=%{_includedir}/EMBOSS
EMBOSS/phase.sh-67-
--
ETL/phase.sh:12:configure() {
ETL/phase.sh-13-    %configure
ETL/phase.sh-14-
ETL/phase.sh-15-}
--
FlightGear-Atlas/phase.sh:14:configure() {
FlightGear-Atlas/phase.sh-15-    %configure CXXFLAGS="$RPM_OPT_FLAGS -fPIC" \
FlightGear-Atlas/phase.sh-16-      --datadir=%{_datadir}/flightgear
FlightGear-Atlas/phase.sh-17-
--
afpfs-ng/phase.sh:21:configure() {
afpfs-ng/phase.sh-22-    %configure %{?!with_fuse:--disable-fuse} --disable-static
afpfs-ng/phase.sh-23-
afpfs-ng/phase.sh-24-}
--
ams/phase.sh:12:configure() {
ams/phase.sh-13-    %configure --with-ladspa-path=%{_libdir}/ladspa
ams/phase.sh-14-
ams/phase.sh-15-}
--
anjuta/phase.sh:24:configure() {
anjuta/phase.sh-25-    %configure
anjuta/phase.sh-26-
anjuta/phase.sh-27-}
--
anthy-unicode/phase.sh:15:configure() {
anthy-unicode/phase.sh-16-    %configure --disable-static
anthy-unicode/phase.sh-17-
anthy-unicode/phase.sh-18-}
--
anyremote/phase.sh:12:configure() {
anyremote/phase.sh-13-    %configure
anyremote/phase.sh-14-
anyremote/phase.sh-15-}
--
apcupsd/phase.sh:15:configure() {
apcupsd/phase.sh-16-    %configure \
apcupsd/phase.sh-17-      --sysconfdir="/etc/apcupsd" \
apcupsd/phase.sh-18-      --sbindir=/sbin \
--
apricots/phase.sh:16:configure() {
apricots/phase.sh-17-    ./configure --prefix=%{_prefix}
--
apron/phase.sh:65:configure() {
apron/phase.sh-66-    ./configure -prefix %{_prefix} -pplite-prefix %{_prefix} -no-strip -java-prefix %{_jvmdir}/java
apron/phase.sh-67-
apron/phase.sh-68-}
--
ast/phase.sh:18:configure() {
ast/phase.sh-19-    %configure CPPFLAGS="-I%{_includedir}/star" --disable-static --libdir=%{_libdir}/%{name} --with-external_cminpack --with-external_pal
ast/phase.sh-20-
ast/phase.sh-21-}
--
asunder/phase.sh:12:configure() {
asunder/phase.sh-13-    %configure
asunder/phase.sh-14-
asunder/phase.sh-15-}
--
atari++/phase.sh:25:configure() {
atari++/phase.sh-26-    %configure
atari++/phase.sh-27-
atari++/phase.sh-28-}
--
aterm/phase.sh:16:configure() {
aterm/phase.sh-17-    %configure --enable-fading --enable-background-image \
aterm/phase.sh-18-      --x-includes=%{_includedir} \
aterm/phase.sh-19-      --x-libraries=%{_libdir}
--
avr-libc/phase.sh:52:configure() {
avr-libc/phase.sh-53-    ./configure --prefix=%{_prefix} --host=avr --build=`./config.guess` #--enable-doc
bes/phase.sh:39:configure() {
bes/phase.sh-40-    %configure --disable-dependency-tracking \
bes/phase.sh-41-      CPPFLAGS="-I%{_includedir}/cfitsio -I%{_includedir}/tirpc -Wno-vla" LDFLAGS=-L%{_libdir}/libdap LIBS=-ltirpc
bes/phase.sh-42-
--
bfast/phase.sh:21:configure() {
bfast/phase.sh-22-    %configure "CFLAGS=${CFLAGS} -fgnu89-inline"
bfast/phase.sh-23-
bfast/phase.sh-24-}
--
bgpq4/phase.sh:13:configure() {
bgpq4/phase.sh-14-    %configure --docdir=%{_pkgdocdir}
bgpq4/phase.sh-15-
bgpq4/phase.sh-16-}
--
bibutils/phase.sh:14:configure() {
bibutils/phase.sh-15-    ./configure \
bibutils/phase.sh-16-      --install-dir %{buildroot}%{_bindir} \
bibutils/phase.sh-17-      --install-lib %{buildroot}%{_libdir} \
--
bigloo/phase.sh:73:configure() {
bigloo/phase.sh-74-    ./configure \
bigloo/phase.sh-75-      --bindir=%{_bindir} \
bigloo/phase.sh-76-      --libdir=%{_libdir} \
--
biloba/phase.sh:17:configure() {
biloba/phase.sh-18-    %configure --prefix=%{_prefix}
biloba/phase.sh-19-
biloba/phase.sh-20-}
--
bindfs/phase.sh:12:configure() {
bindfs/phase.sh-13-    %configure
bindfs/phase.sh-14-
bindfs/phase.sh-15-}
--
bio2jack/phase.sh:20:configure() {
bio2jack/phase.sh-21-    %configure --enable-static=no --enable-shared=yes
--
boinc-client/phase.sh:51:configure() {
boinc-client/phase.sh-52-    %configure %{?confflags} \
boinc-client/phase.sh-53-      STRIP=: \
boinc-client/phase.sh-54-      DOCBOOK2X_MAN=/usr/bin/db2x_docbook2man \
--
boinc-tui/phase.sh:13:configure() {
boinc-tui/phase.sh-14-    %configure --without-gnutls
boinc-tui/phase.sh-15-
boinc-tui/phase.sh-16-}
--
bonnie++/phase.sh:12:configure() {
bonnie++/phase.sh-13-    %configure --disable-stripping
bonnie++/phase.sh-14-
bonnie++/phase.sh-15-}
--
bristol/phase.sh:31:configure() {
bristol/phase.sh-32-    ./configure --prefix=%{_prefix} --libdir=%{_libdir} --enable-static=no --disable-version-check
bristol/phase.sh-33-
bristol/phase.sh-34-}
--
gsequencer/phase.sh:21:configure() {
gsequencer/phase.sh-22-    %configure FO_XSL="/usr/share/sgml/docbook/xsl-stylesheets/fo/docbook.xsl" HTMLHELP_XSL="/usr/share/sgml/docbook/xs
l-stylesheets/htmlhelp/htmlhelp.xsl" --disable-upstream-gtk-doc --enable-introspection --disable-oss --enable-gtk-doc --enable-gtk-doc-html
gsequencer/phase.sh-23-
gsequencer/phase.sh-24-}
--
ipv6calc/phase.sh:14:configure() {
ipv6calc/phase.sh-15-    %configure \
ipv6calc/phase.sh-16-           %{?enable_ip2location:--enable-ip2location} \
ipv6calc/phase.sh-17-           %{?enable_ip2location:--with-ip2location-dynamic} \
--
irc-otr/phase.sh:13:configure() {
irc-otr/phase.sh-14-    %configure --with-irssi-module-dir=%{_libdir}/irssi/modules
irc-otr/phase.sh-15-
irc-otr/phase.sh-16-}

```
