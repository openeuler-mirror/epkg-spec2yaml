#!/usr/bash

post:%{name}(){
  -p /sbin/ldconfig
}

postun:%{name}(){
  -p /sbin/ldconfig
}

