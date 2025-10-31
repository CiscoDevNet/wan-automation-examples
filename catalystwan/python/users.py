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
    """List all users"""

    # API endpoint for users
    api_path = "/admin/user"

    # Get manager from context
    manager = ctx.obj

    # Fetch users
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_payload(payload, "users_headers_and_data", "output/users/")
        save_payload(data, "users_data", "output/users/")

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
@click.pass_context  # Pass the context to the command
def add(ctx):
    """Add a user"""

    api_path = "/admin/user"

    # Get manager from context
    manager = ctx.obj

    print("\n~~~ Adding user")

    username_input = click.prompt("Enter username to add", type=str)
    password = click.prompt("Enter password for the new user", type=str, hide_input=True)
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

        save_payload(response, "users_add", "output/users/")

        confirmed_username = response.get("userName") if isinstance(response, dict) else None

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
@click.pass_context  # Pass the context to the command
def delete(ctx):
    """Delete a user"""

    print("\n~~~ Deleting user")
    username = click.prompt("Enter username to delete", type=str)

    api_path = f"/admin/user/{username}"

    # Get manager from context
    manager = ctx.obj

    try:
        response = manager._api_delete(api_path)
        save_payload(response, "users_del", "output/users/")
        click.echo(f"User '{username}' successfully deleted.")
        # The _api_delete method returns a dict with a 'message' key if no JSON content
        if "message" in response:
            click.echo(f"API Confirmation: {response['message']}")

    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Add commands to the cli group
    cli.add_command(ls)
    cli.add_command(add)
    cli.add_command(delete)

    # Call the cli group.
    # The authentication and logout will be handled by the cli group's context and teardown callback.
    cli()
