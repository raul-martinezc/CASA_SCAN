from __future__ import annotations

import ipaddress
import socket
import time
from datetime import datetime
from typing import Dict, Optional, Tuple, List

import netifaces
from scapy.all import ARP, Ether, srp, IP, ICMP, conf  # type: ignore

# mDNS / DNS
import dns.message
import dns.query
import dns.rdatatype
import dns.reversename

from .models import Device, ScanResult
from .oui_db import lookup_vendor as oui_lookup_vendor


def autodetect_subnet() -> Tuple[ipaddress.IPv4Network, Optional[str]]:
    """
    Use netifaces to find the default IPv4 gateway and the corresponding
    interface, then derive the IPv4 network (subnet) from that interface
    address + netmask.
    """
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
    """
    Parse a user-provided subnet string like '192.168.1.0/24'.
    """
    return ipaddress.IPv4Network(subnet_str, strict=False)


def arp_sweep(
    subnet: ipaddress.IPv4Network,
    iface: Optional[str] = None,
    timeout: float = 2.0,
    inter: float = 0.02,
) -> Dict[str, str]:
    """
    Perform an ARP sweep over the given subnet, returning a mapping
    ip -> mac for all hosts that respond.
    """
    conf.verb = 0
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp = ARP(pdst=str(subnet))
    ans, _ = srp(broadcast / arp, timeout=timeout, inter=inter, iface=iface)
    results: Dict[str, str] = {}
    for _, rcv in ans:
        results[rcv.psrc] = rcv.hwsrc
    return results


def icmp_ping(
    ips: List[str],
    iface: Optional[str] = None,
    timeout: float = 1.0,
    delay_between: float = 0.03,
) -> Dict[str, float]:
    """
    Send a single ICMP echo request to each IP and return a mapping
    ip -> round-trip-time in milliseconds for hosts that respond.
    """
    from scapy.all import sr1  # type: ignore

    conf.verb = 0
    rtts: Dict[str, float] = {}

    for ip in ips:
        pkt = IP(dst=ip) / ICMP()
        start = time.time()
        reply = sr1(pkt, timeout=timeout, iface=iface)
        end = time.time()
        if reply is not None:
            rtts[ip] = (end - start) * 1000.0
        time.sleep(delay_between)

    return rtts


def mdns_reverse_lookup(ip: str, timeout: float = 0.7) -> Optional[str]:
    """
    Try to resolve an IP to a hostname using mDNS only (224.0.0.251:5353).

    This stays on the local link and does NOT go through the ISP resolver.
    Returns the hostname (like 'iphone.local') or None if not found.
    """
    try:
        # e.g. "192.168.1.30" -> "30.1.168.192.in-addr.arpa."
        ptr_name = dns.reversename.from_address(ip)

        query = dns.message.make_query(ptr_name, dns.rdatatype.PTR)

        # Send to the mDNS multicast group on UDP/5353
        response = dns.query.udp(
            query,
            "224.0.0.251",
            port=5353,
            timeout=timeout,
            ignore_unexpected=True,
        )

        for answer in response.answer:
            for item in answer.items:
                # item.target is like "iphone.local."
                return str(item.target).rstrip(".")
    except Exception:
        return None


def resolve_hostname(
    ip: str,
    use_mdns: bool = True,
    use_rdns: bool = False,
) -> Optional[str]:
    """
    Resolve an IP to a hostname.

    - First tries mDNS (local, 224.0.0.251:5353) if use_mdns is True.
    - Then optionally tries traditional reverse DNS (via system resolver)
      if use_rdns is True.

    Default behavior: use_mdns=True, use_rdns=False → stays local.
    """
    # 1) Try mDNS (local, Bonjour-style)
    if use_mdns:
        name = mdns_reverse_lookup(ip)
        if name:
            return name

    # 2) Optionally fall back to reverse DNS via system resolver (may hit ISP)
    if use_rdns:
        try:
            host, _, _ = socket.gethostbyaddr(ip)
            return host
        except Exception:
            pass

    return None


def scan(
    subnet_str: Optional[str] = None,
    iface: Optional[str] = None,
    enable_ping: bool = True,
    use_mdns: bool = True,
    use_rdns: bool = False,
) -> ScanResult:
    """
    Main scan function.

    - If subnet_str is provided, scan that subnet.
    - Otherwise, autodetect the default gateway + subnet.
    - Uses ARP to find live hosts and MAC addresses.
    - Optionally pings hosts to get RTT and 'alive' flag.
    - Looks up MAC OUI vendor using oui_db.py.
    - Hostname resolution:
        * mDNS first (local, default enabled)
        * optional reverse DNS via ISP if use_rdns=True
    """
    started_at = datetime.utcnow().isoformat() + "Z"

    if subnet_str:
        network = parse_subnet(subnet_str)
        gateway_ip: Optional[str] = None
    else:
        network, gateway_ip = autodetect_subnet()

    # 1) ARP sweep to discover IP -> MAC
    arp_results = arp_sweep(network, iface=iface)

    # Sort IPs numerically so output is stable and human-friendly
    ips = sorted(arp_results.keys(), key=lambda ip: tuple(int(p) for p in ip.split(".")))

    # 2) Optional ICMP ping to measure RTT & confirm reachability
    rtts: Dict[str, float] = {}
    if enable_ping and ips:
        rtts = icmp_ping(ips, iface=iface)

    # 3) Build Device objects
    devices: List[Device] = []
    for ip in ips:
        mac = arp_results.get(ip)
        vendor = oui_lookup_vendor(mac) if mac else None
        hostname = resolve_hostname(ip, use_mdns=use_mdns, use_rdns=use_rdns)
        rtt_ms = rtts.get(ip)
        alive = ip in rtts if enable_ping else None
        is_gateway = (ip == gateway_ip) if gateway_ip else False

        dev = Device(
            ip=ip,
            mac=mac,
            vendor=vendor,
            hostname=hostname,
            is_gateway=is_gateway,
            alive=alive,
            rtt_ms=rtt_ms,
            first_seen=started_at,
            last_seen=started_at,
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
