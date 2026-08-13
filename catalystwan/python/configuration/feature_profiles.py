#!/usr/bin/env python3
"""UX 2.0 Feature Profile and parcel examples."""

from __future__ import annotations

from typing import Any

from utilities.cli import client_from_args, create_parser, run
from utilities.manager import ManagerClient
from utilities.tools import emit, extract_rows

PROFILE_TYPES = ("system", "transport", "service", "cli", "policy-object")
PROFILE_COLUMNS = [
    ("Name", ("profileName",)),
    ("ID", ("profileId",)),
    ("Type", ("profileType",)),
    ("Solution", ("solution",)),
    ("Parcels", ("profileParcelCount",)),
    ("Updated by", ("lastUpdatedBy",)),
    ("Description", ("description",)),
]


def list_profiles(client: ManagerClient) -> Any:
    return client.get("/v1/feature-profile/sdwan")


def discover_profile_type(client: ManagerClient, profile_id: str) -> str:
    for profile in extract_rows(list_profiles(client)):
        if profile.get("profileId") == profile_id:
            profile_type = profile.get("profileType")
            if isinstance(profile_type, str) and profile_type:
                return profile_type
    raise ValueError(f"Could not discover the type of profile {profile_id!r}")


def build_parser():
    parser = create_parser("Inspect UX 2.0 Feature Profiles and parcels.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", aliases=["ls"], help="List Feature Profiles")

    get_parser = subparsers.add_parser("get", help="Get Feature Profile details")
    get_parser.add_argument("profile_id")
    get_parser.add_argument("--type", choices=PROFILE_TYPES)

    bfd_parser = subparsers.add_parser("bfd", help="Get a system BFD parcel")
    bfd_parser.add_argument("profile_id")
    bfd_parser.add_argument("parcel_id")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    with client_from_args(args) as client:
        if args.command in {"list", "ls"}:
            payload = list_profiles(client)
            columns = PROFILE_COLUMNS
        elif args.command == "get":
            profile_type = args.type or discover_profile_type(client, args.profile_id)
            payload = client.get(f"/v1/feature-profile/sdwan/{profile_type}/{args.profile_id}")
            columns = None
        else:
            payload = client.get(
                f"/v1/feature-profile/sdwan/system/{args.profile_id}/bfd/{args.parcel_id}"
            )
            columns = None
    emit(payload, args.output, columns, save=args.save)
    return 0


if __name__ == "__main__":
    run(main)
