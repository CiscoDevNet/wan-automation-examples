#!/usr/bin/env python3
"""CLI for the reusable SD-WAN Manager monitoring use cases."""

from __future__ import annotations

import os

from utilities.cli import client_from_args, create_parser, positive_int, run
from utilities.tools import emit

from .cases import CASES, MonitoringOptions, is_empty, run_cases


def build_parser():
    parser = create_parser("Run reusable SD-WAN Manager monitoring use cases.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    default_device = os.getenv("system_ip")

    for case in CASES.values():
        subparser = subparsers.add_parser(case.key, help=case.description)
        if case.requires_device:
            subparser.add_argument("--device-id", default=default_device)
        if case.uses_hours:
            subparser.add_argument("--hours", type=positive_int, default=24)
        if case.key == "bfd-state":
            subparser.add_argument("--count", type=positive_int, default=1000)

    all_cases = subparsers.add_parser("all", help="Run every use case once")
    all_cases.add_argument("--device-id", default=default_device)
    all_cases.add_argument("--hours", type=positive_int, default=24)
    all_cases.add_argument("--count", type=positive_int, default=1000)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    options = MonitoringOptions(
        device_id=getattr(args, "device_id", None),
        hours=getattr(args, "hours", 24),
        count=getattr(args, "count", 1000),
    )
    keys = list(CASES) if args.command == "all" else [args.command]
    with client_from_args(args) as client:
        results = run_cases(client, keys, options)

    for case, payload in results:
        print(f"\n{case.title}\n{'=' * len(case.title)}")
        save_path = args.save
        if save_path and len(results) > 1:
            save_path = save_path / f"{case.key}.json"
        emit(payload, args.output, list(case.columns), save=save_path)
        if case.empty_hint and is_empty(payload):
            print(case.empty_hint)
    return 0


if __name__ == "__main__":
    run(main)
