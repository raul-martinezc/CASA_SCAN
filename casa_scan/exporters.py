from __future__ import annotations

import json
import os
from graphviz import Digraph

from .models import ScanResult


def save_json(scan_result: ScanResult, path: str) -> None:
    """Save the scan result to a JSON file."""
    data = scan_result.to_dict()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def export_topology_png(
    scan_result: ScanResult,
    path: str,
    title: str = "CASA_SCAN Topology",
) -> None:
    """
    Export a simple radial topology as a PNG using Graphviz.

    - Uses a radial layout engine ("twopi") so the gateway is central
      and devices are arranged around it.
    - Tries to keep the output in a 16:9-ish aspect ratio with readable labels.
    """
    # Graphviz expects a filename without extension when using render()
    base, _ = os.path.splitext(path)
    if not base:
        base = "topology"

    # Use a radial layout engine instead of the default "dot"
    dot = Digraph(comment=title, format="png", engine="twopi")

    # Global graph look & aspect ratio (Graphviz units are in inches)
    dot.graph_attr.update(
        size="16,9!",    # 16:9 aspect; "!" forces exact size
        ratio="fill",    # fill that rectangle
        dpi="150",       # decent DPI for readability
        overlap="false",
        splines="true",
    )

    dot.attr(fontsize="10")

    gateway_ip = scan_result.gateway_ip or "gateway"
    gateway_node_id = f"gw_{gateway_ip}"

    # Default gateway node (may be relabeled if we have a Device marked as is_gateway)
    dot.node(
        gateway_node_id,
        f"Gateway\n{gateway_ip}",
        shape="doublecircle",
        style="filled",
        fillcolor="lightgray",
    )

    # First pass: if there is a device marked as gateway, use its extra info to relabel
    for dev in scan_result.devices:
        if dev.is_gateway:
            label_lines = [dev.ip]
            if dev.hostname:
                label_lines.append(dev.hostname)
            if dev.vendor:
                label_lines.append(dev.vendor)
            label = "\n".join(label_lines)
            dot.node(
                gateway_node_id,
                label,
                shape="doublecircle",
                style="filled",
                fillcolor="lightgray",
            )
            break  # only one gateway expected

    # Second pass: add all non-gateway devices around the center
    for dev in scan_result.devices:
        if dev.is_gateway:
            continue

        label_lines = [dev.ip]
        if dev.hostname:
            label_lines.append(dev.hostname)
        if dev.vendor:
            label_lines.append(dev.vendor)
        label = "\n".join(label_lines)

        node_id = f"dev_{dev.ip}"
        dot.node(node_id, label, shape="box")

        # Connect each device to the gateway node
        dot.edge(gateway_node_id, node_id)

    dot.render(filename=base, cleanup=True)
