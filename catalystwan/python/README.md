# Cisco Catalyst SD-WAN Manager APIs - Python Examples

This folder provides Python examples for interacting with Cisco Catalyst SD-WAN Manager APIs. Explore practical demonstrations for automating network configurations, monitoring, and integrations.

Please note these examples are for demonstration purposes only and not production-ready.

## Setup local environment variables to provide manager instance details

You need to define the SD-WAN Manager parameters to authenticate.

Example for MacOSX:

```bash
export manager_host=10.0.0.100
export manager_port=443
export manager_username=sdwan
export manager_password=mysuperpassword
```

Example for Windows

```shell
set manager_host=10.0.0.100
set manager_port=443
set manager_username=sdwan
set manager_password=mysuperpassword
```

The easiest way to run the tool is to provide all the lab variables in a init file and source that file.
The example file below contains all the variables required to run all the tasks.

```shell
% cat init.sh
export manager_host=10.0.0.100
export manager_port=443
export manager_username=sdwan
export manager_password=mysuperpassword
% source init.sh
```

All tests will save API response payloads in `output/` folder to easily check the json content.

## Usage

Run python scripts using `uv run <script.py>`

Example:

```shell
uv run users.py ls
```
