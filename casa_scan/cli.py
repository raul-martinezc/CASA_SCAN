from __future__ import annotations

import argparse
import os
import sys

from .scanner import scan
from .exporters import save_json, export_topology_png
from . import __version__


def build_parser():
    p = argparse.ArgumentParser(
        description="CASA_SCAN v1.1 - ARP+ICMP scanner with local mDNS and optional rDNS"
    )
    p.add_argument("--subnet", "-s", help="Subnet to scan (e.g. 192.168.1.0/24). If omitted, autodetect.")
    p.add_argument("--iface", "-i", help="Network interface to use (e.g. en0, eth0).")
    p.add_argument(
        "--no-ping",
        action="store_true",
        help="Disable ICMP ping (skip RTT / alive checks).",
    )
    p.add_argument(
        "--no-mdns",
        action="store_true",
        help="Disable local mDNS hostname resolution.",
    )
    p.add_argument(
        "--rdns",
        action="store_true",
        help="Enable traditional reverse DNS lookups (may contact ISP resolvers).",
    )
    p.add_argument(
        "--json-output",
        "-j",
        default="devices.json",
        help="Path to write JSON output (default: devices.json).",
    )
    p.add_argument(
        "--graph-output",
        "-g",
        default="topology.png",
        help="Path to write Graphviz topology PNG (default: topology.png).",
    )
    p.add_argument(
        "--version",
        action="store_true",
        help="Show CASA_SCAN version and exit.",
    )
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.version:
        print(f"CASA_SCAN v{__version__}")
        return 0

    enable_ping = not args.no_ping

    try:
        result = scan(subnet_str=args.subnet, iface=args.iface, enable_ping=enable_ping)
    except Exception as e:
        print(f"[!] Scan failed: {e}", file=sys.stderr)
        return 1

    print(f"[+] Scan complete. Found {len(result.devices)} devices.")

    # --- Summary stats ---
    total = len(result.devices)
    responded = sum(1 for d in result.devices if d.alive)
    mdns_named = sum(1 for d in result.devices if d.hostname)
    known_vendor = sum(1 for d in result.devices if d.vendor)

    print(f"[=] Summary:")
    print(f"    • Total devices:          {total}")
    print(f"    • Responded to ping:      {responded}")
    print(f"    • mDNS hostnames found:   {mdns_named}")
    print(f"    • Known vendors:          {known_vendor}")

    save_json(result, args.json_output)
    print(f"[+] JSON saved: {os.path.abspath(args.json_output)}")
    export_topology_png(result, args.graph_output)
    print(f"[+] Topology PNG saved: {os.path.abspath(args.graph_output)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
