# models.py
# 
# This file defines the object data structures that represent: a single device on the network and the full scan itself
#   -The scanner creates device objects
#   -Those get collected into a scan result
#   -Exporters use ScanResult.to_dict() to write JSON.
#   -The topology (exporter.py) generator uses ScanResult.devices.
#   -The CLI summary counts properties of devices in ScanResult.devices.
# Without these models, everything else would be messy and error-prone.
#
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

@dataclass
class Device:
    ip: str
    mac: Optional[str] = None
    vendor: Optional[str] = None
    hostname: Optional[str] = None
    is_gateway: bool = False
    alive: Optional[bool] = None
    rtt_ms: Optional[float] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ScanResult:
    subnet: str
    gateway_ip: Optional[str]
    devices: List[Device]
    started_at: str
    finished_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subnet": self.subnet,
            "gateway_ip": self.gateway_ip,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "devices": [d.to_dict() for d in self.devices],
        }
