
from __future__ import annotations

import ipaddress
import socket
import time
from datetime import datetime
from typing import Dict, Optional, Tuple, List

import netifaces
from scapy.all import ARP, Ether, srp, IP, ICMP, conf  # type: ignore

from .models import Device, ScanResult


OUI_VENDOR_MAP = {
    "F0:18:98": "Apple, Inc.",
    "3C:5A:B4": "Google, Inc.",
    "BC:30:D9": "Samsung Electronics",
    "00:1A:2B": "Example Vendor",
}

def normalize_mac(mac: str) -> str:
    return mac.upper().replace("-", ":").strip()

def lookup_vendor(mac: Optional[str]) -> Optional[str]:
    if not mac:
        return None
    mac = normalize_mac(mac)
    prefix = ":".join(mac.split(":")[:3])
    return OUI_VENDOR_MAP.get(prefix, None)

def autodetect_subnet() -> Tuple[ipaddress.IPv4Network, Optional[str]]:
    gws = netifaces.gateways()
    default = gws.get("default", {})
    v4_default = default.get(netifaces.AF_INET)
    if not v4_default:
        raise RuntimeError("Could not determine default IPv4 gateway")
    gateway_ip, iface = v4_default[0], v4_default[1]

    addrs = netifaces.ifaddresses(iface)
    inet_info = addrs.get(netifaces.AF_INET)
    if not inet_info:
        raise RuntimeError(f"No IPv4 address found on interface {iface}")

    addr = inet_info[0]["addr"]
    netmask = inet_info[0].get("netmask", "255.255.255.0")

    network = ipaddress.IPv4Network(f"{addr}/{netmask}", strict=False)
    return network, gateway_ip

def parse_subnet(subnet_str: str) -> ipaddress.IPv4Network:
    return ipaddress.IPv4Network(subnet_str, strict=False)

def arp_sweep(subnet, iface=None, timeout=2.0, inter=0.02) -> Dict[str, str]:
    conf.verb = 0
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp = ARP(pdst=str(subnet))
    ans, _ = srp(broadcast / arp, timeout=timeout, inter=inter, iface=iface)
    results = {}
    for snd, rcv in ans:
        results[rcv.psrc] = rcv.hwsrc
    return results

def icmp_ping(ips: List[str], iface=None, timeout=1.0, delay_between=0.03) -> Dict[str, float]:
    from scapy.all import sr1
    conf.verb = 0
    rtts = {}
    for ip in ips:
        pkt = IP(dst=ip) / ICMP()
        start = time.time()
        reply = sr1(pkt, timeout=timeout, iface=iface)
        end = time.time()
        if reply is not None:
            rtts[ip] = (end - start) * 1000.0
        time.sleep(delay_between)
    return rtts

def resolve_hostname(ip: str) -> Optional[str]:
    try:
        host, _, _ = socket.gethostbyaddr(ip)
        return host
    except:
        return None

def scan(subnet_str=None, iface=None, enable_ping=True) -> ScanResult:
    started_at = datetime.utcnow().isoformat() + "Z"

    if subnet_str:
        network = parse_subnet(subnet_str)
        gateway_ip = None
    else:
        network, gateway_ip = autodetect_subnet()

    arp_results = arp_sweep(network, iface=iface)

    ips = sorted(arp_results.keys(), key=lambda ip: tuple(int(p) for p in ip.split(".")))

    rtts = {}
    if enable_ping and ips:
        rtts = icmp_ping(ips, iface=iface)

    devices = []
    for ip in ips:
        mac = arp_results.get(ip)
        vendor = lookup_vendor(mac)
        hostname = resolve_hostname(ip)
        rtt_ms = rtts.get(ip)
        alive = ip in rtts if enable_ping else None
        is_gateway = (ip == gateway_ip) if gateway_ip else False

        dev = Device(
            ip=ip, mac=mac, vendor=vendor,
            hostname=hostname, is_gateway=is_gateway,
            alive=alive, rtt_ms=rtt_ms,
            first_seen=started_at, last_seen=started_at
        )
        devices.append(dev)

    finished_at = datetime.utcnow().isoformat() + "Z"

    return ScanResult(
        subnet=str(network),
        gateway_ip=gateway_ip,
        devices=devices,
        started_at=started_at,
        finished_at=finished_at,
    )
