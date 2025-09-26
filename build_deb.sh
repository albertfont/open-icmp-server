#!/usr/bin/env bash
set -e


# compilar el binari C
gcc -O2 -Wall -o open_icmp_server_c open_icmp_server.c


# assegurar l'arbre necessari per dh_install
mkdir -p debian/open-icmp-server/usr/local/bin
cp open_icmp_server_c debian/open-icmp-server/usr/local/bin/


# construir el paquet
dpkg-buildpackage -us -uc -b
