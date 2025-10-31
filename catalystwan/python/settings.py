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


import logging

import click
import requests

# Import Manager class and the credentials function
from utilities.manager import Manager, get_manager_credentials_from_env
from utilities.tools import save_payload


# -----------------------------------------------------------------------------
@click.group()
@click.pass_context  # Pass the context object to the cli group
def cli(ctx):
    """Command line tool for to collect application names and tunnel performances"""
    log_file_path = "sdwan_api.log"

    logging.basicConfig(
        filename=log_file_path,  # <--- Add this line to specify the log file
        filemode="a",  # <--- Optional: 'a' for append (default), 'w' for overwrite
        format="%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d [%(filename)s])",
        datefmt="%d/%m/%Y %I:%M:%S %p",
        level=logging.INFO,
    )

    # Get manager credentials from environment variables
    print("\n--- Getting Manager credentials from environment variables ---")
    host, port, user, password = get_manager_credentials_from_env()

    # Create session with Cisco Catalyst SD-WAN Manager
    print("\n--- Authenticating to SD-WAN Manager ---")
    manager = Manager(host, port, user, password)
    ctx.obj = manager  # Store the manager object in the context

    # Register a teardown callback to ensure logout happens
    def logout_manager():
        if ctx.obj:  # Check if manager was successfully created
            ctx.obj.logout()
            print("\n--- Logged out from SD-WAN Manager ---")

    ctx.call_on_close(logout_manager)


# -----------------------------------------------------------------------------
@click.command()
@click.pass_context  # Pass the context to the command
def get_org(ctx):
    """
    Get SD_WAN Manager organization
    """

    # Get manager from context
    manager = ctx.obj

    api_path = "/settings/configuration/organization"

    # Fetch API endpoint for org name
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_payload(payload, "org_header_data", "output/settings/")
        save_payload(data, "org_data", "output/settings/")
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
@click.pass_context  # Pass the context to the command
def get_validator(ctx):
    """
    Get vBond IP or name
    """

    # Get manager from context
    manager = ctx.obj

    api_path = "/settings/configuration/device"

    # Fetch API endpoint for org name
    try:
        vbond = ""
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_payload(payload, "validator_header_all", "output/settings/")
        save_payload(data, "validator_data", "output/settings/")
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
    # Add commands to the cli group
    cli.add_command(get_validator)
    cli.add_command(get_org)

    # Call the cli group.
    # The authentication and logout will be handled by the cli group's context and teardown callback.
    cli()
