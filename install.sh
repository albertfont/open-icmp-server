#!/usr/bin/env bash
set -e


DEST=/usr/local/bin/open_icmp_server.py
UNIT=/etc/systemd/system/open-icmp-server.service


if [ "$(id -u)" -ne 0 ]; then
echo "must be run as root"
exit 1
fi


cp open_icmp_server.py "$DEST"
chmod +x "$DEST"
cp open-icmp-server.service "$UNIT"
systemctl daemon-reload
systemctl enable --now open-icmp-server.service


echo "installed and started open-icmp-server"
