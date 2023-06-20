#!/usr/bin/env bash

transfiletriggerin() {
    #:rpm_macro_param:  -- %{_libdir}/gio/modules
    gio-querymodules-%{__isa_bits} %{_libdir}/gio/modules &> /dev/null || :
    
    glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :
}

transfiletriggerpostun() {
    #:rpm_macro_param:  -- %{_libdir}/gio/modules
    gio-querymodules-%{__isa_bits} %{_libdir}/gio/modules &> /dev/null || :
    
    glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :
}

