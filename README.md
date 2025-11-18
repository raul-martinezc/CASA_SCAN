# CASA_SCAN v1.2

CASA_SCAN is a small, home-focused network scanner designed for **your own home network only**.

Version 1.2 features:

- ARP sweep to discover devices on your LAN.
- Optional ICMP ping to check liveness and round-trip time.
- Automatic subnet detection (if you don't specify one).
- JSON output with per-device info (IP, MAC, hostname, vendor).
- Simple star-style PNG topology diagram using Graphviz.
- Local-first hostname resolution using **mDNS (Bonjour-style)**, with optional traditional reverse DNS lookups.

> **Important:** CASA_SCAN is intended **only** for scanning networks you own or are explicitly authorized to scan (e.g., your own home network).

---

## Requirements

- Python 3.9+
- **Python virtual environments are strongly encouraged** to keep dependencies isolated.
- System dependencies:
  - `libpcap` / raw socket support (Linux/macOS).
  - `npcap` (Windows) — required for Scapy.
  - `graphviz` installed system-wide so the `dot` command is available.
- Python packages (see `requirements.txt`):
  - `scapy`
  - `netifaces`
  - `graphviz`
  - `dnspython`  (used for local mDNS and optional reverse-DNS lookups)

---

## Platform Setup Instructions

### macOS

```bash
brew install graphviz
pip install -r requirements.txt
```

Scapy uses raw sockets, so scanning may require:

```bash
sudo python -m casa_scan.cli
```

---

### Linux (Debian/Ubuntu example)

```bash
sudo apt-get install graphviz
pip install -r requirements.txt
```

Run with:

```bash
sudo python -m casa_scan.cli
```

---

### Windows 10/11

Scapy requires **Npcap** on Windows.

Download & install Npcap (with WinPcap compatibility mode enabled):  
https://nmap.org/npcap/

Install Graphviz:  
https://graphviz.org/download/

Install Python deps:

```powershell
pip install -r requirements.txt
```

Run the scanner (Admin recommended):

```powershell
python -m casa_scan.cli
```

Windows ICMP and ARP behavior varies by driver. Npcap must be installed.

---

## Installation (All Platforms)

Unzip the archive, then:

```bash
cd casa_scan_project_full
pip install -r requirements.txt
```

---

## Creating a Python Virtual Environment (Recommended)

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Deactivate anytime:

```bash
deactivate
```

---

## Usage

### 1. Activate your Python environment (recommended)

macOS/Linux:

```bash
source venv/bin/activate
```

Windows:

```powershell
venv\Scripts\activate
```

---

### 2. Autodetect your home subnet

```bash
python -m casa_scan.cli
```

This will:

- Detect your primary IPv4 subnet from the default gateway.
- Run an ARP sweep (and ICMP ping by default).
- Use local mDNS to resolve hostnames where possible.
- Output:
  - `devices.json`
  - `topology.png`

---

### 3. Specify subnet explicitly

```bash
python -m casa_scan.cli --subnet 192.168.1.0/24
```

---

### 4. Control hostname resolution (mDNS vs rDNS)

By default, CASA_SCAN:

- Tries mDNS first (224.0.0.251:5353, Bonjour-style, local-only).
- Does **not** query your ISP DNS unless `--rdns` is provided.

You can adjust behavior:

Disable mDNS (no local multicast lookups):

```bash
python -m casa_scan.cli --no-mdns
```

Enable reverse DNS (may hit ISP resolvers):

```bash
python -m casa_scan.cli --rdns
```

Combine both:

```bash
python -m casa_scan.cli --rdns --no-mdns      # rDNS only
python -m casa_scan.cli --rdns                # mDNS, then rDNS fallback
```

---

### 5. Disable ping (ARP only)

```bash
python -m casa_scan.cli --no-ping
```

---

### 6. Custom output paths

```bash
python -m casa_scan.cli --json-output my_devices.json --graph-output my_topology.png
```

---

## JSON Output Format

```json
{
  "subnet": "192.168.1.0/24",
  "gateway_ip": "192.168.1.1",
  "started_at": "...",
  "finished_at": "...",
  "devices": [
    {
      "ip": "192.168.1.42",
      "mac": "AA:BB:CC:DD:EE:FF",
      "vendor": "Apple, Inc.",
      "hostname": "ExampleHostname",
      "is_gateway": false,
      "alive": true,
      "rtt_ms": 12.3,
      "first_seen": "...",
      "last_seen": "..."
    }
  ]
}
```

Notes:

- `vendor` is derived from a local `oui_db.csv` file.
- `hostname` is from mDNS by default, or reverse DNS when `--rdns` is used.

---

## Topology PNG

- Gateway = double-circle node
- Devices = rectangular nodes
- Labels include IP, hostname, vendor

---

## Future Versions Might Include

- Port scanning
- Switch/AP awareness
- Historical tracking
- Alerts for device changes
- Web dashboard

---

## User Agreement & Credits

CASA_SCAN was created by **Raul Y. Martinez**.

CASA_SCAN is provided *as-is*, without warranty. You are responsible for how you use it.

### Authorized Use Only

You agree to:

- Only scan networks you own or have explicit permission to test.
- Not use CASA_SCAN on third-party networks, workplaces, schools, or ISP infrastructure.
- Follow local laws, regulations, and ISP terms.

### Credits

CASA_SCAN relies on:

- Python
- Scapy
- netifaces
- Graphviz
- dnspython

Respect the licenses of these projects.
