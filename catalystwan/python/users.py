#! /usr/bin/env python3
# =========================================================================
# Cisco Catalyst SD-WAN Manager APIs
# =========================================================================
#
# Managing users on SD-WAN Manager
#
# Description:
#   List, add, and delete users on Cisco Catalyst SD-WAN Manager.
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
    """Command line tool for managing users on SD-WAN Manager."""
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
    """List all users"""

    # API endpoint for users
    api_path = "/admin/user"

    # Fetch users
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_json(payload, "users_headers_and_data", "output/payloads/users/")
        save_json(data, "users_data", "output/payloads/users/")

        headers = ["Username", "Group"]
        table = []
        for item in data:
            tr = [
                item.get("userName", "N/A"),
                ", ".join(item.get("group", ["N/A"])),
            ]
            table.append(tr)

        if table:
            click.echo(tabulate.tabulate(table, headers, tablefmt="fancy_grid"))
        else:
            click.echo("No users found or data is empty.")

    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
@click.command()
def add():
    """Add a user"""

    api_path = "/admin/user"

    print("\n~~~ Adding user")

    username_input = click.prompt("Enter username to add", type=str)
    password = click.prompt(
        "Enter password for the new user", type=str, hide_input=True
    )
    group_input = click.prompt(
        "Enter user group(s) (comma-separated, e.g., netadmin,admin)",
        type=str,
        default="netadmin",
    )
    groups = [g.strip() for g in group_input.split(",")]

    user_payload = {
        "userName": username_input,
        "description": f"User {username_input} created via CLI",
        "locale": "en_US",
        "group": groups,
        "password": password,
        "resGroupName": "global",
    }

    try:
        response = manager._api_post(api_path, payload=user_payload)

        save_json(response, "users_add", "output/payloads/users/")

        confirmed_username = (
            response.get("userName") if isinstance(response, dict) else None
        )

        if confirmed_username:
            click.echo(f"User '{confirmed_username}' successfully created.")
        else:
            click.echo(f"User '{username_input}' successfully created.")

    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
@click.command()
def delete():
    """Delete a user"""

    print("\n~~~ Deleting user")
    username = click.prompt("Enter username to delete", type=str)

    api_path = f"/admin/user/{username}"

    try:
        response = manager._api_delete(api_path)
        save_json(response, "users_del", "output/payloads/users/")
        click.echo(f"User '{username}' successfully deleted.")
        # The _api_delete method returns a dict with a 'message' key if no JSON content
        if "message" in response:
            click.echo(f"API Confirmation: {response['message']}")

    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return

    log_file_path = "application.log"  # You can make this more dynamic if needed


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
    cli.add_command(add)
    cli.add_command(delete)

    cli()
