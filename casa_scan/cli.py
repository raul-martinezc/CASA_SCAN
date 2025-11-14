
from __future__ import annotations
import argparse, os, sys
from .scanner import scan
from .exporters import save_json, export_topology_png
from . import __version__

def build_parser():
    p = argparse.ArgumentParser(description="CASA_SCAN v1 - ARP+ICMP scanner")
    p.add_argument("--subnet", "-s")
    p.add_argument("--iface", "-i")
    p.add_argument("--no-ping", action="store_true")
    p.add_argument("--json-output", "-j", default="devices.json")
    p.add_argument("--graph-output", "-g", default="topology.png")
    p.add_argument("--version", action="store_true")
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
    save_json(result, args.json_output)
    print(f"[+] JSON saved: {os.path.abspath(args.json_output)}")
    export_topology_png(result, args.graph_output)
    print(f"[+] Topology PNG saved: {os.path.abspath(args.graph_output)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
