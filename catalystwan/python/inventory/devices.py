#!/usr/bin/env python3
"""Device inventory and configuration examples."""

from __future__ import annotations

from utilities.cli import client_from_args, create_parser, run
from utilities.tools import emit, save_json

DEVICE_COLUMNS = [
    ("UUID", ("uuid",)),
    ("Model", ("deviceModel",)),
    ("Certificate", ("vedgeCertificateState",)),
    ("Hostname", ("host-name",)),
    ("System IP", ("configuredSystemIP", "deviceIP")),
    ("Site ID", ("siteId",)),
    ("Managed by", ("managed-by",)),
]


def build_parser():
    parser = create_parser("Inspect SD-WAN devices and running configurations.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", aliases=["ls"], help="List WAN Edge devices")
    get_parser = subparsers.add_parser("get", help="Get a device by system IP")
    get_parser.add_argument("system_ip")
    config_parser = subparsers.add_parser("config", help="Get running configuration")
    config_parser.add_argument("uuid")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    with client_from_args(args) as client:
        if args.command in {"list", "ls"}:
            payload = client.get("/system/device/vedges")
            columns = DEVICE_COLUMNS
        elif args.command == "get":
            payload = client.get("/system/device/vedges", params={"deviceIP": args.system_ip})
            columns = DEVICE_COLUMNS
        else:
            payload = client.get(f"/template/config/running/{args.uuid}")
            columns = None

    if args.command == "config" and args.output == "table":
        config = payload.get("config", "") if isinstance(payload, dict) else payload
        print(config or "No running configuration returned.")
        if args.save:
            save_json(payload, args.save)
    else:
        emit(payload, args.output, columns, save=args.save)
    return 0


if __name__ == "__main__":
    run(main)
