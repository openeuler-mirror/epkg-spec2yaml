#!/usr/bash

post:libs() {
-p /sbin/ldconfig
}

postun:libs() {
-p /sbin/ldconfig
}

