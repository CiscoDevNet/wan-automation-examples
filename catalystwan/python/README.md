# Cisco Catalyst SD-WAN Manager Python Examples

These examples use API-key authentication exclusively. They do not create a
username/password session or a JWT session.

## Structure

```text
python/
├── monitoring/                    Monitoring and statistics APIs
│   ├── cases.py                   Reusable queries and use-case registry
│   ├── run_cases.py               CLI for registered monitoring use cases
│   └── approute.py                Application and AppRoute examples
├── configuration/                 Configuration APIs
│   ├── config_groups.py           UX 2.0 Configuration Group examples
│   └── feature_profiles.py        UX 2.0 Feature Profile examples
├── administration/                Administration APIs
│   ├── users.py                   User administration examples
│   └── legacy_settings.py         Undocumented legacy settings examples
├── inventory/                     Device inventory APIs
│   └── devices.py                 Inventory and running configuration
└── utilities/                     Shared implementation
    ├── manager.py                 API-key authentication and HTTP transport
    ├── cli.py                     Environment and command-line configuration
    └── tools.py                   JSON, table, file, and timestamp helpers
```

## Setup

The project is pinned to Python 3.12 through `.python-version`. Run commands
from this `python/` directory and let uv install the interpreter and create the
virtual environment:

```shell
uv python install
uv sync
```

Copy the environment template and provide the same API-key values used by the
Bruno collection:

```shell
cp .env.example .env
```

```dotenv
vmanage=192.168.1.10
port=443
apikey=replace-with-your-api-key
system_ip=10.0.0.20
```

The client sends the API key to `GET /dataservice/client/token`, stores the
returned XSRF token in memory, and includes both values in subsequent request
headers. The API key is accepted only through `.env` or the environment so it
does not leak through shell history or process listings. Secrets are never
written to logs or output files.

The project has one third-party dependency, `requests`. `uv run` installs it
from `pyproject.toml` automatically.

## Common monitoring use cases

List the registered cases:

```shell
uv run -m monitoring.run_cases --help
```

Run historical application utilization. If 24 hours is empty, widen the window
carefully:

```shell
uv run -m monitoring.run_cases applications --hours 24
uv run -m monitoring.run_cases applications --hours 1000
```

Run a targeted real-time query using `system_ip` from `.env`:

```shell
uv run -m monitoring.run_cases system-status
```

Run every case once:

```shell
uv run -m monitoring.run_cases all --hours 24
```

Global options must precede the subcommand:

```shell
uv run -m monitoring.run_cases --output json sites --hours 24
uv run -m monitoring.run_cases --save output/sites.json sites --hours 24
```

To add a monitoring use case, add one `MonitoringCase` entry to `CASES` in
`monitoring/cases.py`. Authentication, CLI connection options, error handling,
JSON output, and table rendering require no changes.

## Other examples

```shell
uv run -m inventory.devices list
uv run -m inventory.devices get 10.0.0.20
uv run -m configuration.feature_profiles list
uv run -m configuration.config_groups list
uv run -m administration.legacy_settings organization
uv run -m monitoring.approute statistics 10.0.0.20 10.0.0.21 --hours 6
uv run -m administration.users list
```

Use `--help` on any script or subcommand for its complete arguments.

`administration/legacy_settings.py` retains two routes used by the original examples:
`/settings/configuration/organization` and `/settings/configuration/device`.
They now use the shared API-key client, but neither route appears in the
checked-in 20.18 or 26.1 OpenAPI specifications. Treat them as
version-dependent, undocumented compatibility examples rather than supported
26.1 APIs.

## TLS and production use

TLS certificate verification is enabled by default. Prefer a trusted
certificate or `--ca-bundle PATH`. Use `--insecure` only for an isolated lab.

All requests have a bounded timeout and return concise errors without exposing
the API key or XSRF token. Real-time monitoring commands remain intended for
targeted troubleshooting, not continuous polling.
