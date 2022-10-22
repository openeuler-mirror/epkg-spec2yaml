#!/usr/bash

post() {
%__rm -f %{_bindir}/ld
%{_sbindir}/alternatives --install %{_bindir}/ld ld \
  %{_bindir}/ld.bfd %{ld_bfd_priority}

%if %{with gold}
%{_sbindir}/alternatives --install %{_bindir}/ld ld \
  %{_bindir}/ld.gold %{ld_gold_priority}
%endif

if [ $1 = 0 ]; then
%{_sbindir}/alternatives --auto ld
fi

/sbin/ldconfig

}

preun() {
if [ $1 = 0 ]; then
%{_sbindir}/alternatives --remove ld %{_bindir}/ld.bfd

%if %{with gold}
%{_sbindir}/alternatives --remove ld %{_bindir}/ld.gold
%endif
fi

}

postun() {
/sbin/ldconfig

}

