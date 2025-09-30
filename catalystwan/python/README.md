# Python Examples

## Setup Python Virtual Environment

Install uv by running the following command in Terminal:

`curl -LsSf https://astral.sh/uv/install.sh | sh`

## Init

Initialize and install dependancies:

```bash
uv sync
```

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

All tests will save API response payloads in `output/payloads` folder to easily check the json content.

## Usage

Run python script using `uv run <script.py>`

Example:

```console
uv run users.py ls
```
