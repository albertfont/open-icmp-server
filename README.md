# open-icmp-server

### Project purpose

`open-icmp-server` is a tiny, focused daemon that listens for ICMP Echo Requests ("ping") and responds with proper ICMP Echo Replies.

### Features

* Minimal Python 3 daemon (single file)
* Installs as a systemd service
* Graceful start/stop
* Minimal logging to syslog (via `systemd` stdout/stderr capture)
* Notes about required capabilities and security

### Requirements

* Linux with Python 3.8+
* Root privileges to open raw sockets (or run via `CAP_NET_RAW` capability)

### Installation (example)

```bash
# on the target machine (as root)
chmod +x install.sh
./install.sh
# then start
systemctl enable --now open-icmp-server.service
```

### Usage

* The daemon runs in the foreground under systemd and writes to journal. Use `journalctl -u open-icmp-server.service -f` to follow activity.

### Security & Notes

* The daemon opens a raw socket and crafts ICMP replies. Running as root is required unless you grant `CAP_NET_RAW` to the binary with `setcap`.
* This program is intentionally simple and not hardened. Do not expose on production networks where security/isolation matters.

### Uninstall

```bash
systemctl stop open-icmp-server.service
systemctl disable open-icmp-server.service
rm /usr/local/bin/open_icmp_server.py
rm /etc/systemd/system/open-icmp-server.service
systemctl daemon-reload
```

## Final notes

This draft is intentionally polished: concise README, clean single-file daemon, systemd unit, and install script. Use it as a template for a lighthearted prank. Always make sure to have permission before deploying on someone else's machine or a production environment.
