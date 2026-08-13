"""Output and file helpers shared by the Python examples."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

Column = tuple[str, tuple[str, ...]]


def extract_rows(payload: Any) -> list[dict[str, Any]]:
    """Normalize common Manager list response shapes."""
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return [item for item in payload["data"] if isinstance(item, dict)]
    return [payload] if isinstance(payload, dict) else []


def value_for(row: dict[str, Any], keys: tuple[str, ...]) -> str:
    value = next((row[key] for key in keys if key in row), "")
    if isinstance(value, (dict, list)):
        value = json.dumps(value, separators=(",", ":"))
    text = str(value)
    return text if len(text) <= 48 else f"{text[:45]}..."


def print_table(rows: list[dict[str, Any]], columns: list[Column]) -> None:
    """Render a compact ASCII table without a third-party dependency."""
    if not rows:
        print("No matching records returned.")
        return
    values = [[value_for(row, keys) for _, keys in columns] for row in rows]
    widths = [
        max(len(label), *(len(row[index]) for row in values))
        for index, (label, _) in enumerate(columns)
    ]
    line = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    print(line)
    print(
        "|"
        + "|".join(f" {label:<{width}} " for (label, _), width in zip(columns, widths, strict=True))
        + "|"
    )
    print(line)
    for row in values:
        print(
            "|"
            + "|".join(f" {value:<{width}} " for value, width in zip(row, widths, strict=True))
            + "|"
        )
    print(line)


def save_json(payload: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(payload, indent=2, sort_keys=True)}\n", encoding="utf-8")


def emit(
    payload: Any,
    output: str,
    columns: list[Column] | None = None,
    *,
    save: Path | None = None,
) -> None:
    """Print a full JSON response or selected table fields and optionally save it."""
    if output == "json" or not columns:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_table(extract_rows(payload), columns)
    if save:
        save_json(payload, save)


def convert_timestamp(timestamp_ms: int | float | None) -> str:
    if timestamp_ms is None:
        return "N/A"
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
