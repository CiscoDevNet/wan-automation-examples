#! /usr/bin/env python3
# =========================================================================
# Cisco Catalyst SD-WAN Manager APIs
# =========================================================================
#
# Managing App Route Statistics and Applications
#
# Description:
#   List applications
#   List App route statistics between two routers
#
# =========================================================================

import cmd
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
def app_list(ctx):
    """
    Retrieve the list of Applications.
    Example command: python approute.py app-list
    """

    print("Application List ")

    api_path = "/device/dpi/application-mapping"

    # Get manager from context
    manager = ctx.obj

    # Fetch API endpoint
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_payload(payload, "applications_header_data", "output/approute/")
        save_payload(data, "applications_data", "output/approute/")
        app_headers = ["App name", "Family", "ID"]

        table = list()
        # cli = cmd.Cmd() # This line is not needed here as cmd.Cmd is not used for columnize

        for item in data:
            tr = [item["name"], item["family"], item["appId"]]
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
def app_list2(ctx):
    """
    Retrieve the list of Applications (alternative display).
    Display app-name and family in multi-column view
    Example command: python approute.py app-list2
    """
    print("Application List (2)")

    api_path = "/device/dpi/application-mapping"

    # Get manager from context
    manager = ctx.obj

    # Fetch API endpoint for org name
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_payload(payload, "app_header_data", "output/approute/")
        save_payload(data, "app_data", "output/approute/")

        table = list()
        local_cmd_cli = cmd.Cmd()  # Instantiate cmd.Cmd locally where it's used

        for item in data:
            table.append(item["name"] + "(" + item["family"] + ")")

        click.echo(local_cmd_cli.columnize(table, displaywidth=120))

    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
@click.command()
@click.pass_context  # Pass the context to the command
def app_qosmos(ctx):
    """
    Retrieve the list of Qosmos Applications (original Viptela classification engine)
    Example command: python approute.py app-qosmos
    """
    print("Application List (qosmos)")

    api_path = "/device/dpi/qosmos-static/applications"

    # Get manager from context
    manager = ctx.obj

    # Fetch API endpoint
    try:
        payload = manager._api_get(api_path)
        data = payload.get("data", [])
        save_payload(payload, "app_qosmos_header_data", "output/approute/")
        save_payload(data, "app_qosmos_data", "output/approute/")
        app_headers = ["App name", "Family", "ID"]

        table = list()

        for item in data:
            tr = [item["name"], item["family"], item["appId"]]
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
def approute_fields(ctx):
    """
    Retrieve App route Aggregation API Query fields.
    Example command: python approute.py approute-fields
    """

    api_path = "/statistics/approute/fields"

    # Get manager from context
    manager = ctx.obj

    # Fetch API endpoint for org name
    try:
        payload = manager._api_get(api_path)
        save_payload(payload, "approute-fields", "output/approute/")

        tags = list()
        local_cmd_cli = cmd.Cmd()  # Instantiate cmd.Cmd locally where it's used

        for item in payload:
            tags.append(item["property"] + "(" + item["dataType"] + ")")

        click.echo(local_cmd_cli.columnize(tags, displaywidth=120))

    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
@click.command()
@click.pass_context  # Pass the context to the command
def approute_stats(ctx):
    """
    Create Average Approute statistics for all tunnels between provided 2 routers for last 1 hour.
    Example command: python approute.py approute-stats
    """

    api_path = "/statistics/approute/aggregation"

    # Get manager from context
    manager = ctx.obj

    # Routers System IPs

    rtr1_systemip = input("Enter Router-1 System IP address : ")
    rtr2_systemip = input("Enter Router-2 System IP address : ")

    # Query payloads

    payload_r1_r2 = {
        "query": {
            "condition": "AND",
            "rules": [
                {
                    "value": ["1"],
                    "field": "entry_time",
                    "type": "date",
                    "operator": "last_n_hours",
                },
                {
                    "value": [rtr1_systemip],
                    "field": "local_system_ip",
                    "type": "string",
                    "operator": "in",
                },
                {
                    "value": [rtr2_systemip],
                    "field": "remote_system_ip",
                    "type": "string",
                    "operator": "in",
                },
            ],
        },
        "aggregation": {
            "field": [{"property": "name", "sequence": 1, "size": 6000}],
            "metrics": [
                {"property": "loss_percentage", "type": "avg"},
                {"property": "vqoe_score", "type": "avg"},
                {"property": "latency", "type": "avg"},
                {"property": "jitter", "type": "avg"},
            ],
        },
    }

    payload_r2_r1 = {
        "query": {
            "condition": "AND",
            "rules": [
                {
                    "value": ["1"],
                    "field": "entry_time",
                    "type": "date",
                    "operator": "last_n_hours",
                },
                {
                    "value": [rtr2_systemip],
                    "field": "local_system_ip",
                    "type": "string",
                    "operator": "in",
                },
                {
                    "value": [rtr1_systemip],
                    "field": "remote_system_ip",
                    "type": "string",
                    "operator": "in",
                },
            ],
        },
        "aggregation": {
            "field": [{"property": "name", "sequence": 1, "size": 6000}],
            "metrics": [
                {"property": "loss_percentage", "type": "avg"},
                {"property": "vqoe_score", "type": "avg"},
                {"property": "latency", "type": "avg"},
                {"property": "jitter", "type": "avg"},
            ],
        },
    }

    try:
        response = manager._api_post(api_path, payload=payload_r1_r2)
        app_route_stats = response.get("data")
        save_payload(response, "approute_stats_r1r2_header_data", "output/approute/")
        save_payload(app_route_stats, "approute_stats_r1r2_data", "output/approute/")
        app_route_stats_headers = [
            "Tunnel name",
            "vQoE score",
            "Latency",
            "Loss percentage",
            "Jitter",
        ]
        table = list()

        click.echo("\nAverage App route statistics between %s and %s for last 1 hour\n" % (rtr1_systemip, rtr2_systemip))

        for item in app_route_stats:
            tr = [
                item["name"],
                item["vqoe_score"],
                item["latency"],
                item["loss_percentage"],
                item["jitter"],
            ]
            table.append(tr)

        click.echo(tabulate.tabulate(table, app_route_stats_headers, tablefmt="fancy_grid"))

        # Get app route statistics for tunnels from router-2 to router-1
        response = manager._api_post(api_path, payload=payload_r2_r1)
        app_route_stats = response.get("data")

        save_payload(response, "approute_stats_r2r1_header_data", "output/approute/")
        save_payload(app_route_stats, "approute_stats_r2r1_data", "output/approute/")

        app_route_stats_headers = [
            "Tunnel name",
            "vQoE score",
            "Latency",
            "Loss percentage",
            "Jitter",
        ]
        table = list()

        click.echo("\nAverage App route statistics between %s and %s for last 1 hour\n" % (rtr2_systemip, rtr1_systemip))
        for item in app_route_stats:
            tr = [
                item["name"],
                item["vqoe_score"],
                item["latency"],
                item["loss_percentage"],
                item["jitter"],
            ]
            table.append(tr)
        click.echo(tabulate.tabulate(table, app_route_stats_headers, tablefmt="fancy_grid"))

    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
@click.command()
@click.pass_context  # Pass the context to the command
def approute_device(ctx):
    """
    Get Realtime Approute statistics for a specific tunnel for provided router and remote.
    Example command: python approute.py approute-device
    """

    # Get manager from context
    manager = ctx.obj

    # Input parameters

    rtr1_systemip = input("Enter System IP address : ")
    rtr2_systemip = input("Enter Remote System IP address : ")
    color = input("Enter color : ")

    # API path with parameters

    api_path = "/device/app-route/statistics?remote-system-ip=%s&local-color=%s&remote-color=%s&deviceId=%s" % (
        rtr2_systemip,
        color,
        color,
        rtr1_systemip,
    )

    # Fetch users
    try:
        payload = manager._api_get(api_path)
        app_route_stats = payload.get("data")
        save_payload(payload, "approute_device_header_data", "output/approute/")
        save_payload(app_route_stats, "approute_device_data", "output/approute/")

        app_route_stats_headers = [
            "vdevice-host-name",
            "remote-system-ip",
            "Index",
            "Mean Latency",
            "Mean Jitter",
            "Mean Loss",
            "average-latency",
            "average-jitter",
            "loss",
        ]
        table = list()

        click.echo("\nRealtime App route statistics for %s to %s\n" % (rtr1_systemip, rtr2_systemip))
        for item in app_route_stats:
            tr = [
                item["vdevice-host-name"],
                item["remote-system-ip"],
                item["index"],
                item["mean-latency"],
                item["mean-jitter"],
                item["mean-loss"],
                item["average-latency"],
                item["average-jitter"],
                item["loss"],
            ]
            table.append(tr)
        try:
            click.echo(tabulate.tabulate(table, app_route_stats_headers, tablefmt="fancy_grid"))
        except UnicodeEncodeError:
            click.echo(tabulate.tabulate(table, app_route_stats_headers, tablefmt="grid"))

    except requests.exceptions.RequestException as e:
        print(f"An unexpected error occurred: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Status: {e.response.status_code}, Response: {e.response.text}")
        return


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Add commands to the cli group
    cli.add_command(app_list)
    cli.add_command(app_list2)
    cli.add_command(app_qosmos)
    cli.add_command(approute_fields)
    cli.add_command(approute_stats)
    cli.add_command(approute_device)

    # Call the cli group.
    # The authentication and logout will be handled by the cli group's context and teardown callback.
    cli()
