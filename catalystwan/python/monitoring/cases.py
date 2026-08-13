"""Reusable monitoring use cases independent of CLI presentation."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any

from utilities.manager import ManagerClient
from utilities.tools import Column, extract_rows


@dataclass(frozen=True, slots=True)
class MonitoringOptions:
    device_id: str | None = None
    hours: int = 24
    count: int = 1000


@dataclass(frozen=True, slots=True)
class MonitoringCase:
    key: str
    title: str
    description: str
    request: Callable[[ManagerClient, MonitoringOptions], Any]
    columns: tuple[Column, ...]
    requires_device: bool = False
    uses_hours: bool = False
    empty_hint: str | None = None


def time_query(hours: int, data_type: str | None = None) -> dict[str, Any]:
    rules: list[dict[str, Any]] = [
        {
            "value": [str(hours)],
            "field": "entry_time",
            "type": "date",
            "operator": "last_n_hours",
        }
    ]
    if data_type:
        rules.append({"value": [data_type], "field": "type", "type": "string", "operator": "in"})
    return {"condition": "AND", "rules": rules}


def application_query(hours: int) -> dict[str, Any]:
    return {
        "query": time_query(hours),
        "aggregation": {
            "field": [{"property": "family", "size": 200, "sequence": 1}],
            "metrics": [{"property": "octets", "type": "sum", "order": "desc"}],
        },
    }


def availability_query(hours: int, data_type: str) -> dict[str, Any]:
    fields = (
        [{"property": "site_id", "sequence": 1, "size": 100}]
        if data_type == "site"
        else [
            {"property": "system_ip", "sequence": 1, "size": 100},
            {"property": "color", "sequence": 2, "size": 100},
        ]
    )
    return {
        "query": time_query(hours, data_type),
        "aggregation": {
            "field": fields,
            "metrics": [{"property": "down_time", "type": "sum", "order": "desc"}],
        },
    }


def _device_params(options: MonitoringOptions) -> dict[str, str]:
    if not options.device_id:
        raise ValueError("This use case requires --device-id or system_ip in .env")
    return {"deviceId": options.device_id}


CASES: dict[str, MonitoringCase] = {
    case.key: case
    for case in (
        MonitoringCase(
            "system-status",
            "Real-time system status",
            "Get current CPU, uptime, and system status from one device.",
            lambda client, options: client.get(
                "/device/system/status", params=_device_params(options)
            ),
            (
                ("Host", ("vdevice-host-name",)),
                ("CPU user", ("cpu_user",)),
                ("CPU system", ("cpu_system",)),
                ("CPU idle", ("cpu_idle",)),
                ("Uptime", ("uptime",)),
                ("Last updated", ("lastupdated",)),
            ),
            requires_device=True,
        ),
        MonitoringCase(
            "interfaces",
            "Real-time interface status and counters",
            "Get current interface state, traffic, and errors from one device.",
            lambda client, options: client.get("/device/interface", params=_device_params(options)),
            (
                ("Host", ("vdevice-host-name",)),
                ("Interface", ("ifname", "interface")),
                ("Admin", ("if-admin-status",)),
                ("Oper", ("if-oper-status",)),
                ("Mbps", ("speed-mbps",)),
                ("RX octets", ("rx-octets", "rx_octets")),
                ("TX octets", ("tx-octets", "tx_octets")),
                ("RX errors", ("rx-errors", "rx_errors")),
                ("TX errors", ("tx-errors", "tx_errors")),
            ),
            requires_device=True,
        ),
        MonitoringCase(
            "bfd-state",
            "Bulk BFD session state",
            "Get one bounded batch of BFD state across the fabric.",
            lambda client, options: client.get(
                "/data/device/state/BFDSessions", params={"count": options.count}
            ),
            (
                ("Host", ("vdevice-host-name", "host_name")),
                ("System IP", ("system-ip", "system_ip", "vdevice-name")),
                ("State", ("state",)),
                ("Local color", ("local-color", "local_color")),
                ("Remote color", ("remote-color", "remote_color")),
            ),
        ),
        MonitoringCase(
            "tunnel-traffic",
            "Real-time tunnel traffic",
            "Get current tunnel counters from one device.",
            lambda client, options: client.get(
                "/device/tunnel/statistics", params=_device_params(options)
            ),
            (
                ("Host", ("vdevice-host-name",)),
                ("Peer", ("system-ip",)),
                ("Local color", ("local-color",)),
                ("Remote color", ("remote-color",)),
                ("RX octets", ("rx_octets", "rx-octets")),
                ("TX octets", ("tx_octets", "tx-octets")),
            ),
            requires_device=True,
        ),
        MonitoringCase(
            "applications",
            "Applications by traffic utilization",
            "Aggregate DPI traffic by application family.",
            lambda client, options: client.post(
                "/statistics/dpi/aggregation", payload=application_query(options.hours)
            ),
            (
                ("Family", ("family", "application")),
                ("Octets", ("octets",)),
                ("Count", ("count",)),
            ),
            uses_hours=True,
            empty_hint="No DPI records matched. Try a wider --hours value.",
        ),
        MonitoringCase(
            "sites",
            "Sites by availability",
            "Aggregate Network Availability records by site.",
            lambda client, options: client.post(
                "/statistics/nwa/details",
                payload=availability_query(options.hours, "site"),
            ),
            (
                ("Site ID", ("site_id", "siteid")),
                ("Site", ("sitename", "site_name")),
                ("Availability", ("availability",)),
                ("Downtime", ("down_time",)),
                ("Health", ("health",)),
            ),
            uses_hours=True,
        ),
        MonitoringCase(
            "circuits",
            "Circuits by availability",
            "Aggregate Network Availability link records by system IP and color.",
            lambda client, options: client.post(
                "/statistics/nwa/details",
                payload=availability_query(options.hours, "link"),
            ),
            (
                ("System IP", ("system_ip", "system-ip")),
                ("Color", ("color",)),
                ("Availability", ("availability",)),
                ("Downtime", ("down_time",)),
                ("Health", ("health",)),
            ),
            uses_hours=True,
        ),
    )
}


def run_case(
    client: ManagerClient, key: str, options: MonitoringOptions
) -> tuple[MonitoringCase, Any]:
    try:
        case = CASES[key]
    except KeyError:
        raise ValueError(f"Unknown monitoring use case: {key}") from None
    return case, case.request(client, options)


def run_cases(
    client: ManagerClient, keys: Iterable[str], options: MonitoringOptions
) -> list[tuple[MonitoringCase, Any]]:
    return [run_case(client, key, options) for key in keys]


def is_empty(payload: Any) -> bool:
    return not extract_rows(payload)
