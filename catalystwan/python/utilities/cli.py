"""Shared command-line configuration for the Python examples."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Callable
from pathlib import Path

from .manager import ManagerAPIError, ManagerClient


def load_env_file(path: Path) -> None:
    """Load basic KEY=VALUE entries without replacing exported variables."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def load_environment() -> None:
    python_dir = Path(__file__).resolve().parents[1]
    load_env_file(python_dir / ".env")
    if Path.cwd() != python_dir:
        load_env_file(Path.cwd() / ".env")


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def create_parser(description: str, *, output: bool = True) -> argparse.ArgumentParser:
    """Create a parser with consistent Manager connection arguments."""
    load_environment()
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--vmanage", default=os.getenv("vmanage"))
    parser.add_argument(
        "--port",
        type=positive_int,
        default=os.getenv("port") or "443",
    )
    parser.add_argument("--timeout", type=positive_float, default=30.0)
    tls = parser.add_mutually_exclusive_group()
    tls.add_argument("--insecure", action="store_true", help="Disable TLS verification")
    tls.add_argument("--ca-bundle", help="CA bundle used to verify Manager TLS")
    if output:
        parser.add_argument("--output", choices=("table", "json"), default="table")
        parser.add_argument("--save", type=Path, help="Also save the full JSON response")
    return parser


def client_from_args(args: argparse.Namespace) -> ManagerClient:
    if not args.vmanage:
        raise ValueError("Set vmanage in .env/the environment or pass --vmanage")
    api_key = os.getenv("apikey")
    if not api_key:
        raise ValueError("Set apikey in .env or the environment")
    verify: bool | str = False if args.insecure else (args.ca_bundle or True)
    return ManagerClient(
        args.vmanage,
        api_key,
        port=args.port,
        verify=verify,
        timeout=args.timeout,
    )


def run(main: Callable[[], int | None]) -> None:
    """Run a CLI function with consistent user-facing error handling."""
    try:
        result = main()
    except (ManagerAPIError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130) from None
    raise SystemExit(result or 0)
