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

import json
import logging
import os

import click
import requests
import tabulate

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
def ls():
    """
    Get Device list
    """
    type = "vedges"

    api_path = "/system/device/%s" % (type)

    # Fetch API endpoint
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_json(payload, "devices_all", "output/payloads/devices/")
        save_json(data, "devices_data", "output/payloads/devices/")
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
                item.get(
                    "configuredSystemIP", "N/A"
                ),  # Using .get() with default value
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
def get_device_by_ip():
    """
    Get Device by IP
    /system/device/{type}?deviceIP={ip_address}
    """

    type = "vedges"
    systemip = click.prompt("Enter device system-ip", type=str)
    api_path = f"/system/device/{type}?deviceIP={systemip}"

    # Fetch API endpoint
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_json(payload, "device_by_ip_all", "output/payloads/devices/")
        save_json(data, "device_by_ip_data", "output/payloads/devices/")

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
def get_config():
    """
    Get Device Configuration
    dataservice/template/config/running/{uuid}
    """

    uuid = click.prompt("Enter device uuid", type=str)
    api_path = f"/template/config/running/{uuid}"

    # Fetch API endpoint
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_json(payload, "device_config_all", "output/payloads/devices/")
        running_config = payload["config"]
        print(running_config)

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
    cli.add_command(ls)
    cli.add_command(get_config)
    cli.add_command(get_device_by_ip)
    cli()
