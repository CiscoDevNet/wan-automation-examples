#!/usr/bin/env python3
"""Application classification and AppRoute monitoring examples."""

from __future__ import annotations

from typing import Any

from utilities.cli import client_from_args, create_parser, positive_int, run
from utilities.tools import emit, extract_rows

APPLICATION_COLUMNS = [
    ("Application", ("name",)),
    ("Family", ("family",)),
    ("ID", ("appId",)),
]
APPROUTE_COLUMNS = [
    ("Direction", ("direction",)),
    ("Tunnel", ("name",)),
    ("vQoE", ("vqoe_score",)),
    ("Latency", ("latency", "mean-latency")),
    ("Loss %", ("loss_percentage", "mean-loss")),
    ("Jitter", ("jitter", "mean-jitter")),
]


def aggregation_query(local_ip: str, remote_ip: str, hours: int) -> dict[str, Any]:
    return {
        "query": {
            "condition": "AND",
            "rules": [
                {
                    "value": [str(hours)],
                    "field": "entry_time",
                    "type": "date",
                    "operator": "last_n_hours",
                },
                {
                    "value": [local_ip],
                    "field": "local_system_ip",
                    "type": "string",
                    "operator": "in",
                },
                {
                    "value": [remote_ip],
                    "field": "remote_system_ip",
                    "type": "string",
                    "operator": "in",
                },
            ],
        },
        "aggregation": {
            "field": [{"property": "name", "sequence": 1, "size": 6000}],
            "metrics": [
                {"property": "loss_percentage", "type": "avg"},
                {"property": "vqoe_score", "type": "avg"},
                {"property": "latency", "type": "avg"},
                {"property": "jitter", "type": "avg"},
            ],
        },
    }


def build_parser():
    parser = create_parser("Inspect applications and AppRoute measurements.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("applications", help="List application mappings")
    subparsers.add_parser("qosmos", help="List Qosmos application mappings")
    subparsers.add_parser("fields", help="List AppRoute statistics fields")

    stats = subparsers.add_parser("statistics", help="Compare two tunnel directions")
    stats.add_argument("router_a")
    stats.add_argument("router_b")
    stats.add_argument("--hours", type=positive_int, default=1)

    realtime = subparsers.add_parser("realtime", help="Get one live AppRoute path")
    realtime.add_argument("--device-id", required=True)
    realtime.add_argument("--remote-system-ip", required=True)
    realtime.add_argument("--local-color", required=True)
    realtime.add_argument("--remote-color")
    return parser


def directional_rows(payload: Any, direction: str) -> list[dict[str, Any]]:
    rows = extract_rows(payload)
    return [{"direction": direction, **row} for row in rows]


def main() -> int:
    args = build_parser().parse_args()
    with client_from_args(args) as client:
        if args.command == "applications":
            payload = client.get("/device/dpi/application-mapping")
            columns = APPLICATION_COLUMNS
        elif args.command == "qosmos":
            payload = client.get("/device/dpi/qosmos-static/applications")
            columns = APPLICATION_COLUMNS
        elif args.command == "fields":
            payload = client.get("/statistics/approute/fields")
            columns = [("Property", ("property",)), ("Type", ("dataType",))]
        elif args.command == "statistics":
            a_to_b = client.post(
                "/statistics/approute/aggregation",
                payload=aggregation_query(args.router_a, args.router_b, args.hours),
            )
            b_to_a = client.post(
                "/statistics/approute/aggregation",
                payload=aggregation_query(args.router_b, args.router_a, args.hours),
            )
            payload = {
                "data": directional_rows(a_to_b, f"{args.router_a} -> {args.router_b}")
                + directional_rows(b_to_a, f"{args.router_b} -> {args.router_a}"),
                "responses": {"a_to_b": a_to_b, "b_to_a": b_to_a},
            }
            columns = APPROUTE_COLUMNS
        else:
            payload = client.get(
                "/device/app-route/statistics",
                params={
                    "deviceId": args.device_id,
                    "remote-system-ip": args.remote_system_ip,
                    "local-color": args.local_color,
                    "remote-color": args.remote_color or args.local_color,
                },
            )
            columns = [
                ("Host", ("vdevice-host-name",)),
                ("Remote", ("remote-system-ip",)),
                ("Index", ("index",)),
                ("Latency", ("mean-latency", "average-latency")),
                ("Jitter", ("mean-jitter", "average-jitter")),
                ("Loss", ("mean-loss", "loss")),
            ]
    emit(payload, args.output, columns, save=args.save)
    return 0


if __name__ == "__main__":
    run(main)
