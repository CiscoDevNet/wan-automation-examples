#! /usr/bin/env python3
# =========================================================================
# Cisco Catalyst SD-WAN Manager APIs
# =========================================================================
#
# Managing devices on SD-WAN Manager
#
# Description:
#   List devices, get device by IP, get device configuration
#
# =========================================================================

import logging

import click
import requests
import tabulate

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
def ls(ctx):
    """
    Get Device list
    """
    type = "vedges"

    api_path = "/system/device/%s" % (type)

    # Get manager from context
    manager = ctx.obj

    # Fetch API endpoint
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_payload(payload, "devices_all", "output/devices/")
        save_payload(data, "devices_data", "output/devices/")
        app_headers = [
            "UUID",
            "Model",
            "Certificate",
            "Configured Hostname",
            "System IP",
            "Configured Site ID",
        ]

        table = list()

        for item in data:
            tr = [
                item.get("uuid", "N/A"),
                item.get("deviceModel", "N/A"),
                item.get("vedgeCertificateState", "N/A"),
                item.get("host-name", "N/A"),
                item.get("configuredSystemIP", "N/A"),  # Using .get() with default value
                item.get("siteId", "N/A"),
            ]
            table.append(tr)

        click.echo(tabulate.tabulate(table, app_headers, tablefmt="fancy_grid"))

    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
@click.command()
@click.pass_context  # Pass the context to the command
def get_device_by_ip(ctx):
    """
    Get Device by IP
    /system/device/{type}?deviceIP={ip_address}
    """

    # Get manager from context
    manager = ctx.obj

    type = "vedges"
    systemip = click.prompt("Enter device system-ip", type=str)
    api_path = f"/system/device/{type}?deviceIP={systemip}"

    # Fetch API endpoint
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_payload(payload, "device_by_ip_all", "output/devices/")
        save_payload(data, "device_by_ip_data", "output/devices/")

        for item in data:
            tr = [
                item["configStatusMessage"],
                item["uuid"],
                item["deviceModel"],
                item["vedgeCertificateState"],
                item["deviceIP"],
                item["host-name"],
                item["version"],
                item["vmanageConnectionState"],
            ]

        print("\nDevice Information:")
        print("------------------")
        print("Device name: ", tr[5])
        print("Device IP: ", tr[4])
        print("UUID: ", tr[1])
        print("Device Model: ", tr[2])
        print("vManage Connection State: ", tr[7])
        print("Certificate state: ", tr[3])
        print("Version: ", tr[6])
        print("Config status: ", tr[0])

    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
@click.command()
@click.pass_context  # Pass the context to the command
def get_config(ctx):
    """
    Get Device Configuration
    dataservice/template/config/running/{uuid}
    """

    # Get manager from context
    manager = ctx.obj

    uuid = click.prompt("Enter device uuid", type=str)
    api_path = f"/template/config/running/{uuid}"

    # Fetch API endpoint
    try:
        payload = manager._api_get(api_path)
        data = payload.get("config", [])
        save_payload(payload, "device_config_header_data", "output/devices/")
        save_payload(data, "device_config_data", "output/devices/")
        running_config = payload["config"]
        print(running_config)

    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Add commands to the cli group
    cli.add_command(ls)
    cli.add_command(get_config)
    cli.add_command(get_device_by_ip)

    # Call the cli group.
    # The authentication and logout will be handled by the cli group's context and teardown callback.
    cli()
