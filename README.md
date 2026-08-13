# WAN Automation Examples

## Introduction

This repository provides Python and Terraform examples for interacting
with Cisco Catalyst SD-WAN Manager and the Meraki Dashboard APIs.
Explore practical demonstrations for automating network configurations, monitoring, and integrations.

Please note these examples are for demonstration purposes only and not production-ready.

For guided Cisco Catalyst SD-WAN lessons, API concepts, configuration and
monitoring workflows, and hands-on lab material, visit the
[Catalyst SD-WAN API Learning Hub](https://jbarozet.github.io/catalyst-sdwan-api-hub/).
For the product API reference, see the
[official Cisco Catalyst SD-WAN API documentation](https://developer.cisco.com/docs/sdwan/).

## Install and Setup

Clone the code to local machine.

```shell
git clone https://github.com/CiscoDevNet/wan-automation-examples.git
```

## File Structure

```example
wan-automation-examples/
├── catalystwan/
│   ├── bruno/
│   ├── lab/
│   ├── mcp-sdwan/
│   ├── python/
│   └── terraform/
├── meraki/
│   ├── bruno/
│   ├── python/
│   └── terraform/
├── scripts/
└── README.md
```

catalystwan:

- Bruno API collection. Visit [README](catalystwan/bruno/README.md)
- python examples. Visit [README](catalystwan/python/README.md)
- terraform examples. Visit [README](catalystwan/terraform/README.md)
- archived scripts retained for older Cisco API documentation. Visit
  [README](catalystwan/lab/README.md)

meraki:

- Bruno API collection. Visit [README](meraki/bruno/README.md)
- python examples
- terraform examples

The Bruno collections are stored beside the Python and Terraform examples for
their respective platforms. [Bruno](https://www.usebruno.com/) is a local-first
API client that keeps collections in Git-friendly text files.

## Setup Python Environment

Install [uv](https://github.com/astral-sh/uv) with standalone installers:

```shell
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```shell
# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Initialize and install dependencies:

```shell
uv sync
```

This initializes your environment by adding packages specified in the pyproject.toml file, ensuring all dependencies are installed as defined for your project.

## Notes

The `CODE_OF_CONDUCT.md` reflects our standards for interaction.

The `CONTRIBUTING.md` file instructs new contributors on how to communicate with the project maintainers, report issues, provide pull requests, reviewing contributions, and how to version control releases.

The `LICENSE` file should contain the license you intend for the source code in the repo.

The `SECURITY.md` file describes security policies and procedures including reporting a security-related bug and the policy on disclosure.

The `AGENTS.md` file contains repository-specific guidance for coding agents.
