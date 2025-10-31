# Cisco Catalyst SD-WAN Manager APIs - Python Examples

This folder provides Python examples for interacting with Cisco Catalyst SD-WAN Manager APIs.
Explore practical demonstrations for automating network configurations, monitoring, and integrations.

Please note these examples are for demonstration purposes only and not production-ready.

## Setup local environment variables to provide manager instance details

You need to define the SD-WAN Manager parameters to authenticate.

Copy `.env.example` to `.env` and update the values with your Manager information.

Example:

```.env
manager_host=192.168.1.10
manager_port=443
manager_username=admin
manager_password=admin
```

## Usage

Run python scripts using `uv run <script.py>`

Example:

```shell
uv run users.py ls
```

All tests will save API response payloads in `output/` folder to easily check the json content.
