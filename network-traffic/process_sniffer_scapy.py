"""
process_sniffer_scapy.py

Same idea as process_sniffer.py (attribute captured traffic to the owning
process via psutil, track bytes sent/received, timestamp everything, log
to CSV) but captures packets with Scapy + Npcap instead of raw sockets.

This avoids the NIC receive-offloading issue that causes raw sockets on
Windows to undercount/miss inbound traffic -- Scapy/Npcap taps in at the
NDIS layer, below where offloading distorts things, the same way Wireshark
does.

Requirements:
    1. Install Npcap:  https://npcap.com/#download
       (Use the default install options; "WinPcap API-compatible mode" is fine.)
    2. pip install scapy psutil

Must be run as Administrator on Windows (packet capture requires elevation).

Usage:
    python process_sniffer_scapy.py                      # show all processes seen
    python process_sniffer_scapy.py --name chrome.exe     # only chrome.exe
    python process_sniffer_scapy.py --pid 12345            # only a specific PID
    python process_sniffer_scapy.py --quiet                # summary table only
    python process_sniffer_scapy.py --summary-interval 10  # summary every 10s (default 5)
    python process_sniffer_scapy.py --csv capture.csv      # log every packet to CSV
    python process_sniffer_scapy.py --iface "Wi-Fi"        # capture on a specific interface
"""

import argparse
import csv
import os
import socket
import time
from datetime import datetime

import psutil
from scapy.all import sniff, IP, TCP, UDP, conf


def build_port_pid_map():
    """
    Returns two dicts:
      port_to_pid:   {local_port: pid}
      pid_to_name:   {pid: process_name}
    Built from the current connection table. Call this periodically since
    connections open/close over time.
    """
    port_to_pid = {}
    pid_to_name = {}

    for c in psutil.net_connections(kind="inet"):
        if c.laddr and c.pid:
            port_to_pid[c.laddr.port] = c.pid
            if c.pid not in pid_to_name:
                try:
                    pid_to_name[c.pid] = psutil.Process(c.pid).name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pid_to_name[c.pid] = "unknown"

    return port_to_pid, pid_to_name


def format_bytes(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def print_summary(stats, pid_to_name):
    if not stats:
        return
    print("\n" + "=" * 70)
    print(f"[{timestamp()}] SUMMARY")
    print(f"{'PROCESS':<20}{'PID':<8}{'SENT':<12}{'RECEIVED':<12}")
    print("-" * 70)
    for pid, (sent, received) in sorted(stats.items(), key=lambda kv: -(kv[1][0] + kv[1][1])):
        name = pid_to_name.get(pid, "unknown")
        print(f"{name:<20}{pid:<8}{format_bytes(sent):<12}{format_bytes(received):<12}")
    print("=" * 70 + "\n")


def open_csv_writer(path):
    file_is_new = not os.path.exists(path) or os.path.getsize(path) == 0
    f = open(path, "a", newline="", encoding="utf-8")
    writer = csv.writer(f)
    if file_is_new:
        writer.writerow([
            "timestamp", "process", "pid", "protocol", "direction",
            "src_ip", "src_port", "dst_ip", "dst_port", "bytes"
        ])
        f.flush()
    return f, writer


class State:
    """Small mutable bag so the Scapy callback can update shared state."""
    def __init__(self, host, args):
        self.host = host
        self.args = args
        self.port_to_pid, self.pid_to_name = build_port_pid_map()
        self.last_map_refresh = time.time()
        self.last_summary = time.time()
        self.stats = {}  # pid -> (sent, received)
        self.csv_file = None
        self.csv_writer = None
        if args.csv:
            self.csv_file, self.csv_writer = open_csv_writer(args.csv)


def handle_packet(packet, state):
    if IP not in packet:
        return
    if TCP in packet:
        proto_name, layer = "TCP", packet[TCP]
    elif UDP in packet:
        proto_name, layer = "UDP", packet[UDP]
    else:
        return  # only care about TCP/UDP for process attribution

    src_ip = packet[IP].src
    dst_ip = packet[IP].dst
    src_port = layer.sport
    dst_port = layer.dport
    packet_len = len(packet)

    # Refresh the port->pid map periodically since connections churn
    if time.time() - state.last_map_refresh > 2.0:
        state.port_to_pid, state.pid_to_name = build_port_pid_map()
        state.last_map_refresh = time.time()

    pid = state.port_to_pid.get(src_port) or state.port_to_pid.get(dst_port)
    if pid is None:
        return  # can't attribute this packet to a known local process

    proc_name = state.pid_to_name.get(pid, "unknown")

    if state.args.pid and pid != state.args.pid:
        return
    if state.args.name and state.args.name.lower() not in proc_name.lower():
        return

    direction = "sent" if src_ip == state.host else "received"
    sent, received = state.stats.get(pid, (0, 0))
    if direction == "sent":
        sent += packet_len
    else:
        received += packet_len
    state.stats[pid] = (sent, received)

    now = timestamp()

    if not state.args.quiet:
        print(f"[{now}] [{proc_name} pid={pid}] {proto_name} "
              f"{src_ip}:{src_port} -> {dst_ip}:{dst_port}  "
              f"({format_bytes(packet_len)}, {direction})")

    if state.csv_writer:
        state.csv_writer.writerow([
            now, proc_name, pid, proto_name, direction,
            src_ip, src_port, dst_ip, dst_port, packet_len
        ])
        state.csv_file.flush()

    if time.time() - state.last_summary > state.args.summary_interval:
        print_summary(state.stats, state.pid_to_name)
        state.last_summary = time.time()


def main():
    parser = argparse.ArgumentParser(description="Sniff traffic (Scapy/Npcap) filtered by owning process")
    parser.add_argument("--name", help="Only show traffic for this process name (e.g. chrome.exe)")
    parser.add_argument("--pid", type=int, help="Only show traffic for this PID")
    parser.add_argument("--host", help="Local IP to treat as 'this machine' (defaults to auto-detected)")
    parser.add_argument("--iface", help="Interface name to capture on (defaults to Scapy's default interface)")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-packet lines, show summary table only")
    parser.add_argument("--summary-interval", type=float, default=5.0,
                         help="Seconds between summary table prints (default 5)")
    parser.add_argument("--csv", help="Path to a CSV file to log every captured packet to (appends if it exists)")
    args = parser.parse_args()

    host = args.host or socket.gethostbyname(socket.gethostname())
    iface = args.iface or conf.iface

    print(f"[*] Treating {host} as this machine's IP")
    print(f"[*] Capturing on interface: {iface}")
    print("[*] Run as Administrator, and make sure Npcap is installed (https://npcap.com).")
    if args.csv:
        print(f"[*] Logging every packet to {args.csv}")

    state = State(host, args)

    try:
        sniff(iface=iface, filter="ip", prn=lambda pkt: handle_packet(pkt, state), store=False)
    except KeyboardInterrupt:
        pass
    finally:
        print_summary(state.stats, state.pid_to_name)
        if state.csv_file:
            state.csv_file.close()


if __name__ == "__main__":
    main()
