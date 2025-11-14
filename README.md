# CASA_SCAN v1

CASA_SCAN is a small, home-focused network scanner designed for **your own home network only**.

Version 1 features:

- ARP sweep to discover devices on your LAN.
- Optional ICMP ping to check liveness and round-trip time.
- Automatic subnet detection (if you don't specify one).
- JSON output with per-device info (IP, MAC, hostname, vendor).
- Simple star-style PNG topology diagram using Graphviz.

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

1. Download & install Npcap (with WinPcap compatibility mode enabled):  
   https://nmap.org/npcap/

2. Install Graphviz:  
   https://graphviz.org/download/

3. Install Python deps:

```powershell
pip install -r requirements.txt
```

4. Run the scanner (Admin recommended):

```powershell
python -m casa_scan.cli
```

> Windows ICMP and ARP behavior varies by driver. Npcap must be installed.

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
- Output:
  - `devices.json`
  - `topology.png`

---

### 3. Specify subnet explicitly

```bash
python -m casa_scan.cli --subnet 192.168.1.0/24
```

---

### 4. Disable ping (ARP only)

```bash
python -m casa_scan.cli --no-ping
```

---

### 5. Custom output paths

```bash
python -m casa_scan.cli --json-output my_devices.json --graph-output my_topology.png
```

---

## JSON Output Format

`devices.json` looks like:

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

---

## Topology PNG

`topology.png` is a simple star or radial graph:

- The default gateway is shown as a **double-circle**.
- Each discovered device appears as a **box node**.
- Labels show:
  - IP address
  - Hostname (if found)
  - Vendor (if known)

This gives you a quick visual snapshot of your home network at scan time.

---

## Future Versions Might Include

- Port/service detection  
- Switch/AP awareness  
- Historical tracking  
- Alerts (offline devices, new devices added)  
- Web dashboard  

CASA_SCAN v1 is intentionally simple so you can extend it easily.

---

## User Agreement & Credits

- CASA_SCAN was created by **Raul Y. Martinez** as a personal/home lab tool.
- CASA_SCAN is provided **“as is,” without warranty of any kind**. You are responsible for how you use it.
- You may use, modify, and extend CASA_SCAN for **personal, non-commercial purposes**, unless you explicitly choose a different license for your own fork or distribution.

**Authorized Use Only**

By using CASA_SCAN, you agree that:

- You will **only** scan networks that you own, administer, or are explicitly authorized to test (for example, your own home network or a lab environment you control).
- You will **not** use CASA_SCAN against third-party networks, neighbors’ Wi-Fi, workplaces, schools, or ISP infrastructure without clear written permission.
- You are responsible for complying with all applicable laws, regulations, and the terms of service of your ISP or network provider.

**Credits**

CASA_SCAN builds on the work of the open-source community and tools such as:

- **Python**
- **Scapy**
- **netifaces**
- **Graphviz**

Please support these projects and respect their licenses.
