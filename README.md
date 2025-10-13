# WAN Automation Examples

## Introduction

[Cisco Catalyst SD-WAN API Official documentation](https://developer.cisco.com/docs/sdwan/)

This repository provides Python and Terraform examples for interacting with Cisco Catalyst SD-WAN Manager and the Meraki Dashboard APIs. Explore practical demonstrations for automating network configurations, monitoring, and integrations.

Please note these examples are for demonstration purposes only and not production-ready.

## Install and Setup

Clone the code to local machine.

```shell
git clone https://github.com/CiscoDevNet/wan-automation-examples.git
```

## File Structure

```example
wan-automation-examples/
├── bruno/
├── docs/
├── catalystwan/
    ├── python/
    ├── terraform/    
├── meraki/
    ├── python/
    ├── terraform/    
├── README.md
```

bruno:

- Similar to postman collections
- A few examples of APIs
- Check [README](bruno/README.md)

catalystwan:

- python example. Check [README](catalystwan/python/README.md)
- terraform examples, check [README](catalystwan/terraform/README.md)

meraki:

- python and terraform examples - TBD

docs:

- [Getting Started](docs/01-Getting-Started.md)
- [Authentication](docs/02-Authentication.md)
- And a few more docs

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

Initialize and install dependancies:

```shell
uv sync
```

## Notes

The `CODE_OF_CONDUCT.md` reflects our standards for interaction.

The `CONTRIBUTING.md` file instructs new contributors on how to communicate with the project maintainers, report issues, provide pull requests, reviewing contributions, and how to version control releases.

The `LICENSE` file should contain the license you intend for the source code in the repo.

The `SECURITY.md` file describes security policies and procedures including reporting a security-related bug and the policy on disclosure. 

The `AGENTS.md` file contains a template for guiding AI agents that work with your repository.
