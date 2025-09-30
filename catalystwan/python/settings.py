#! /usr/bin/env python3
# =========================================================================
# Cisco Catalyst SD-WAN Manager APIs
# =========================================================================
#
# Managing settings on SD-WAN Manager
#
# Description:
#   List organization name and vBond IP or name
#
# =========================================================================


import json
import logging
import os

import click
import requests

# Import the new unified Manager class and the credentials function
from manager import Manager, get_manager_credentials_from_env


# -----------------------------------------------------------------------------
@click.group()
def cli():
    """Command line tool for to collect application names)."""
    pass


# -----------------------------------------------------------------------------
def save_json(
    payload: dict, filename: str = "payload", directory: str = "./output/payloads/"
):
    """Save json response payload to a file

    Args:
        payload: JSON response payload
        filename: filename for saved files (default: "payload")
    """

    filename = "".join([directory, f"{filename}.json"])

    if not os.path.exists(directory):
        print(f"Creating folder {directory}")
        os.makedirs(directory)  # Create the directory if it doesn't exist

    # Dump entire payload to file
    with open(filename, "w") as file:
        json.dump(payload, file, indent=4)


# -----------------------------------------------------------------------------
@click.command()
def get_org():
    """
    Get SD_WAN Manager organization
    """

    api_path = "/settings/configuration/organization"

    # Fetch API endpoint for org name
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_json(payload, "org_header_data", "output/payloads/settings/")
        save_json(data, "org_data", "output/payloads/settings/")
        for item in data:
            org = item["org"]
        click.echo(f"Organization: {org}")

    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
@click.command()
def get_validator():
    """
    Get vBond IP or name
    """

    api_path = "/settings/configuration/device"

    # Fetch API endpoint for org name
    try:
        vbond = ""
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_json(payload, "validator_header_all", "output/payloads/settings/")
        save_json(data, "validator_data", "output/payloads/settings/")
        for item in data:
            vbond = item["domainIp"]
        click.echo(f"validator: {vbond}")

    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    log_file_path = "sdwan_api.log"

    logging.basicConfig(
        filename=log_file_path,  # <--- Add this line to specify the log file
        filemode="a",  # <--- Optional: 'a' for append (default), 'w' for overwrite
        format="%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d [%(filename)s])",
        datefmt="%d/%m/%Y %I:%M:%S %p",
        level=logging.INFO,
    )

    # Create session with Cisco Catalyst SD-WAN Manager
    print("\n--- Authenticating to SD-WAN Manager ---")
    host, port, user, password = get_manager_credentials_from_env()
    manager = Manager(host, port, user, password)

    # Run commands
    cli.add_command(get_validator)
    cli.add_command(get_org)
    cli()
