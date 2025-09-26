#!/usr/bin/env python3
"""
open_icmp_server.py — Minimal ICMP Echo Responder daemon

Run as root (or with CAP_NET_RAW). Listens for ICMP Echo Requests and replies with Echo Replies
preserving identifier, sequence, and payload. Intended for demonstration / harmless pranks only.
"""

import socket
import struct
import select
import signal
import sys
import time

RUNNING = True


def checksum(data: bytes) -> int:
    """Compute the Internet Checksum of the supplied data."""
    if len(data) % 2:
        data += b"\x00"
    s = 0
    for i in range(0, len(data), 2):
        w = data[i] << 8 | data[i + 1]
        s += w
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    return ~s & 0xffff


def build_icmp_echo_reply(icmp_packet: bytes) -> bytes:
    # ICMP header: type (1), code (1), checksum (2), id (2), seq (2)
    if len(icmp_packet) < 8:
        return b""
    icmp_type, code, chksum, ident, seq = struct.unpack('!BBHHH', icmp_packet[:8])
    payload = icmp_packet[8:]
    # only handle Echo Request (type 8)
    if icmp_type != 8:
        return b""
    # build reply header: type=0 (Echo Reply), code=0
    new_type = 0
    new_code = 0
    header = struct.pack('!BBHHH', new_type, new_code, 0, ident, seq)
    packet = header + payload
    cs = checksum(packet)
    # insert checksum
    header = struct.pack('!BBHHH', new_type, new_code, cs, ident, seq)
    return header + payload


def main():
    global RUNNING

    def _signal_handler(signum, frame):
        nonlocal RUNNING
        RUNNING = False

    signal.signal(signal.SIGINT, lambda s, f: _signal_handler(s, f))
    signal.signal(signal.SIGTERM, lambda s, f: _signal_handler(s, f))

    try:
        # raw socket for ICMP. Requires root or CAP_NET_RAW
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        sock.setblocking(False)
    except PermissionError:
        print("Permission denied: this program needs root or CAP_NET_RAW.", file=sys.stderr)
        sys.exit(1)

    print("open-icmp-server: started (listening for ICMP Echo Requests)")

    while RUNNING:
        # wait for activity with a small timeout so we can handle signals
        r, _, _ = select.select([sock], [], [], 1.0)
        if not r:
            continue
        try:
            data, addr = sock.recvfrom(65535)
        except BlockingIOError:
            continue

        # On most Linuxes when using SOCK_RAW with IPPROTO_ICMP we receive the ICMP packet only
        icmp = data
        if len(icmp) < 8:
            continue
        # Only respond to Echo Requests
        if icmp[0] == 8:
            reply = build_icmp_echo_reply(icmp)
            if reply:
                try:
                    sock.sendto(reply, (addr[0], 0))
                    print(f"Replied to {addr[0]} (len={len(reply)})")
                except Exception as e:
                    print(f"Failed to send reply to {addr[0]}: {e}")

    print("open-icmp-server: stopping")


if __name__ == '__main__':
    main()
