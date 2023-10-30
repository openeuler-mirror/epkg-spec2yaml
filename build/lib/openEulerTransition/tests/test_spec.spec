Name:       acl
Version:    2.2.53
Release:
Summary:    Utilities for managing POSIX Access Control Lists
License:    LGPLv2.1+ & GPLv2+
URL:        http://savannah.nongnu.org/projects/acl/
Source0:    https://download.savannah.gnu.org/releases/acl/%{name}-%{version}.tar.gz


Patch0:     0001-tests-do-not-hardcode-the-build-path-into-a-helper-l.patch
Patch1:     0001-test-patch-out-failing-bits.patch


BuildRequires: attr

%description
"ACL allows you to provide different levels of access to files \
and folders for different users."


%package lib%{name}
Summary:    lib%{name}


%description lib%{name}
%{summary}.
%package lib%{name}-devel
Summary:    Files necessary to develop applications with libacl


License:    LGPLv2+
Requires: libacl = %{version}-%{release}
Requires: libattr-devel


Obsoletes:  acl-devel < %{version}-%{release}


%description lib%{name}-devel
This package contains header files for the POSIX ACL library.


%build
source /root/rpmbuild/BUILD/env.conf
cd %{_builddir}/%{name}-%{version}
if [ -e "%{_builddir}/%{name}-%{version}/configure" ]; then
  autoreconf
else
  autoscan
  if [ -e "%{_builddir}/%{name}-%{version}/configure.scan" ]; then
      echo "success to make configure.scan"
      cat %{_builddir}/%{name}-%{version}/configure.scan
      sed -i "s/FULL-PACKAGE-NAME/%{name}/g" %{_builddir}/%{name}-%{version}/configure.scan
      sed -i "s/VERSION/%{version}/g" %{_builddir}/%{name}-%{version}/configure.scan
      sed -i "s/BUG-REPORT-ADDRESS/acl-devel@nongnu.org/g" %{_builddir}/%{name}-%{version}/configure.scan
      cp %{_builddir}/%{name}-%{version}/configure.scan %{_builddir}/%{name}-%{version}/configure.ac
  else
      echo "fail to make configure.scan"
      return
  fi
  aclocal
  autoconf
  if [ -e "%{_builddir}/%{name}-%{version}/configure" ]; then
      echo "autoconf success"
  else
      echo "autoconf fail"
      return
  fi
  autoheader
  if [ -e "%{_builddir}/%{name}-%{version}/Makefile.am" ]; then
      echo "autoheader success"
  else
      echo "autoheader fail"
      return
  fi
fi
automake
./configure --build=${BUILD_SYS} --host=${HOST_SYS} --target=${TARGET_SYS} --disable-silent-rules
make


%install
mkdir -p /root/rpmbuild/BUILDROOT/acl-2.2.53-1.x86_64/usr/lib64/pkgconfig
mkdir -p /root/rpmbuild/BUILDROOT/acl-2.2.53-1.x86_64/usr/include/acl
mkdir -p /root/rpmbuild/BUILDROOT/acl-2.2.53-1.x86_64/usr/include/sys
cp %{_builddir}/%{name}-%{version}/.libs/libacl.so* /root/rpmbuild/BUILDROOT/acl-2.2.53-1.x86_64/usr/lib64/
cp %{_builddir}/%{name}-%{version}/libacl.pc /root/rpmbuild/BUILDROOT/acl-2.2.53-1.x86_64/usr/lib64/pkgconfig/
cp %{_builddir}/%{name}-%{version}/include/libacl.h /root/rpmbuild/BUILDROOT/acl-2.2.53-1.x86_64/usr/include/acl
cp %{_builddir}/%{name}-%{version}/include/acl.h /root/rpmbuild/BUILDROOT/acl-2.2.53-1.x86_64/usr/include/sys
make install


%files lib%{name}
"/usr/lib64/lib*.so*"

%files lib%{name}-devel
%{_includedir}/acl/libacl.h
%{_includedir}/sys/acl.h
%{_libdir}/libacl.so*
%{_libdir}/pkgconfig/libacl.pc