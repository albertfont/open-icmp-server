#!/usr/bin/env bash
set -e


# build C binary
gcc -O2 -Wall -o open_icmp_server_c open_icmp_server.c


# ensure debhelper is installed
type dpkg-buildpackage >/dev/null 2>&1 || { echo "dpkg-dev/debhelper required"; exit 1; }


# build package
dpkg-buildpackage -us -uc -b
