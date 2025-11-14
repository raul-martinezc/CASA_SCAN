# casa_scan/oui_db.py
"""
Simple OUI (MAC prefix) → vendor lookup.

- Uses the first 3 bytes of the MAC address (e.g. D8:EC:5E).
- Data is loaded from oui_db.csv in the same package directory.
- If the DB file is missing or a prefix isn't found, returns None.

This is intentionally small and local. You can update or expand
oui_db.csv over time as you like.
"""

from __future__ import annotations

import csv
import os
from functools import lru_cache
from typing import Dict, Optional


def _normalize_mac_prefix(prefix: str) -> str:
    """
    Normalize an OUI prefix to the form 'AA:BB:CC' (uppercase).
    Accepts things like 'AA-BB-CC', 'aabbcc', 'AA:BB:CC', etc.
    """
    p = prefix.strip().upper().replace("-", ":")
    # If the prefix is 6 hex chars with no separators, add colons
    if ":" not in p and len(p) == 6:
        p = f"{p[0:2]}:{p[2:4]}:{p[4:6]}"
    # Trim to first 8 chars in case extra stuff is present
    return p[0:8]


def mac_to_oui(mac: str) -> Optional[str]:
    """
    Convert a full MAC address like 'd8:ec:5e:f2:44:39' into an
    OUI prefix 'D8:EC:5E'. Returns None if the MAC is malformed.
    """
    if not mac:
        return None
    m = mac.strip().upper().replace("-", ":")
    parts = m.split(":")
    if len(parts) < 3:
        return None
    return ":".join(parts[0:3])


@lru_cache()
def load_oui_db() -> Dict[str, str]:
    """
    Load oui_db.csv from the package directory.

    Expected CSV format (WITH header):

        prefix,vendor
        D8:EC:5E,Linksys / Belkin
        28:CF:E9,Apple, Inc.
        ...

    Lines starting with '#' are treated as comments and ignored.
    """
    mapping: Dict[str, str] = {}

    here = os.path.dirname(__file__)
    path = os.path.join(here, "oui_db.csv")

    if not os.path.exists(path):
        # No DB shipped or user removed it; that's fine.
        return mapping

    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                first = row[0].strip()
                if not first:
                    continue
                # Skip comments
                if first.startswith("#"):
                    continue
                # Skip header row like "prefix,vendor"
                if first.lower() == "prefix":
                    continue
                if len(row) < 2:
                    continue
                prefix = _normalize_mac_prefix(first)
                vendor = row[1].strip()
                if prefix and vendor:
                    mapping[prefix] = vendor
    except Exception:
        # If parsing explodes, just return whatever we got.
        pass

    return mapping


def lookup_vendor(mac: Optional[str]) -> Optional[str]:
    """
    Look up a vendor string for a full MAC address using the OUI DB.

    Returns vendor string or None if not found or MAC is missing.
    """
    if not mac:
        return None
    oui = mac_to_oui(mac)
    if not oui:
        return None
    db = load_oui_db()
    return db.get(oui)
