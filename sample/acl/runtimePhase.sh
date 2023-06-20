#!/usr/bin/env bash

post:libacl() {
    #:rpm_macro_param: -p /sbin/ldconfig
}

postun:libacl() {
    #:rpm_macro_param: -p /sbin/ldconfig
}

