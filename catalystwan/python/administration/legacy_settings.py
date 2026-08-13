#!/usr/bin/env python3
"""Legacy organization and validator settings examples.

These routes are retained from the original scripts, but are not described in
the checked-in SD-WAN Manager 20.18 or 26.1 OpenAPI specifications.
"""

from __future__ import annotations

from utilities.cli import client_from_args, create_parser, run
from utilities.tools import emit


def build_parser():
    parser = create_parser("Inspect legacy, undocumented SD-WAN Manager settings.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("organization", help="Get the organization name")
    subparsers.add_parser("validator", help="Get the validator address")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    with client_from_args(args) as client:
        if args.command == "organization":
            payload = client.get("/settings/configuration/organization")
            columns = [("Organization", ("org",))]
        else:
            payload = client.get("/settings/configuration/device")
            columns = [("Validator", ("domainIp",))]
    emit(payload, args.output, columns, save=args.save)
    return 0


if __name__ == "__main__":
    run(main)
