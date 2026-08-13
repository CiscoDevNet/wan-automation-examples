#!/usr/bin/env python3
"""Configuration Group examples."""

from __future__ import annotations

from utilities.cli import client_from_args, create_parser, run
from utilities.tools import emit

CONFIG_GROUP_COLUMNS = [
    ("Name", ("name",)),
    ("ID", ("id",)),
    ("Description", ("description",)),
    ("Devices", ("numberOfDevices",)),
    ("Up to date", ("numberOfDevicesUpToDate",)),
    ("Updated by", ("lastUpdatedBy",)),
]


def build_parser():
    parser = create_parser("Inspect UX 2.0 Configuration Groups.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", aliases=["ls"], help="List Configuration Groups")
    get_parser = subparsers.add_parser("get", help="Get one Configuration Group")
    get_parser.add_argument("group_id")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    with client_from_args(args) as client:
        if args.command in {"list", "ls"}:
            payload = client.get("/v1/config-group", params={"solution": "sdwan"})
        else:
            payload = client.get(f"/v1/config-group/{args.group_id}")
    emit(payload, args.output, CONFIG_GROUP_COLUMNS, save=args.save)
    return 0


if __name__ == "__main__":
    run(main)
