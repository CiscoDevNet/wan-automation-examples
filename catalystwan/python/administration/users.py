#!/usr/bin/env python3
"""User administration examples."""

from __future__ import annotations

import getpass
from urllib.parse import quote

from utilities.cli import client_from_args, create_parser, run
from utilities.tools import emit

USER_COLUMNS = [("Username", ("userName",)), ("Groups", ("group",))]


def build_parser():
    parser = create_parser("Administer SD-WAN Manager users.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", aliases=["ls"], help="List users")

    add_parser = subparsers.add_parser("add", help="Create a user")
    add_parser.add_argument("username")
    add_parser.add_argument(
        "--group", action="append", dest="groups", default=[], help="Repeat per group"
    )
    add_parser.add_argument("--description")

    delete_parser = subparsers.add_parser("delete", help="Delete a user")
    delete_parser.add_argument("username")
    delete_parser.add_argument("--yes", action="store_true", help="Skip confirmation")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    with client_from_args(args) as client:
        if args.command in {"list", "ls"}:
            payload = client.get("/admin/user")
            emit(payload, args.output, USER_COLUMNS, save=args.save)
            return 0

        escaped_username = quote(args.username, safe="")
        if args.command == "add":
            user_password = getpass.getpass(f"Password for new user {args.username}: ")
            if not user_password:
                raise ValueError("The new user password must not be empty")
            request = {
                "userName": args.username,
                "description": args.description or f"User {args.username} created via API",
                "locale": "en_US",
                "group": args.groups or ["netadmin"],
                "password": user_password,
                "resGroupName": "global",
            }
            payload = client.post("/admin/user", payload=request)
            print(f"User {args.username!r} created.")
        else:
            if not args.yes:
                answer = input(f"Delete user {args.username!r}? [y/N] ").strip().lower()
                if answer not in {"y", "yes"}:
                    print("Cancelled.")
                    return 0
            payload = client.delete(f"/admin/user/{escaped_username}")
            print(f"User {args.username!r} deleted.")

    if payload is not None:
        emit(payload, args.output, save=args.save)
    return 0


if __name__ == "__main__":
    run(main)
