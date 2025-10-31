# ! /usr/bin/env python3
# =========================================================================
# Cisco Meraki Dashboard APIs - Networks
# Revision 1.0 - 10/21/2025
# =========================================================================
#
# Description:
#   Get existing networks within an organization
#   Create a new network within an organization
#   Delete an existing network within an organization
#

import click
import requests
import logging
from meraki_manager import Manager
from parse_yaml_file import parse

# -----------------------------------------------------------------------------
@click.group()
@click.pass_context  # Pass the context object to the cli group
def cli(ctx):
    """Command line tool for to collect application names and tunnel performances"""
    log_file_path = "meraki_api.log"

    logging.basicConfig(
        filename=log_file_path,  # <--- Add this line to specify the log file
        filemode="a",  # <--- Optional: 'a' for append (default), 'w' for overwrite
        format="%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d [%(filename)s])",
        datefmt="%d/%m/%Y %I:%M:%S %p",
        level=logging.INFO,
    )

    # Create requests session with Cisco Meraki Dashboard
    print("\n--- Accessing Meraki Dashboard API Key ---")
    manager = Manager()
    ctx.obj = manager  # Store the manager object in the context


# -----------------------------------------------------------------------------
@click.command()
@click.pass_context  # Pass the context to the command
def get_organization_networks(ctx):

  org_id = click.prompt("Enter organization id", type=str)
  api_path = f"/organizations/{org_id}/networks"
  manager = ctx.obj

  # Get API endpoint
  try:
    data = manager._api_get(api_path)

    for item in data:
      tr = [
        item["id"],
        item["name"],
        item["organizationId"],
        item["productTypes"],
        item["timeZone"],
        item["tags"],
        item["enrollmentString"],
        item["url"],
        item["isBoundToConfigTemplate"],
        item["isVirtual"]
      ]

      print("\nNetwork Information:")
      print("--------------------")
      print("Network ID: ", tr[0])
      print("Network Name: ", tr[1])
      print("Organization ID: ", tr[2])
      print("Product Types: ", tr[3])
      print("Time Zone: ", tr[4])
      print("Tags: ", tr[5])
      print("Enrollment String: ", tr[6])
      print("URL: ", tr[7])
      print("Bound to Config Template: ", tr[8])
      print("Virtual: ", tr[9])

    return
  
  except requests.exceptions.RequestException as e:
    print(f"An unexpected error occurred: {e}")
    if hasattr(e, "response") and e.response is not None:
      print(f"Status: {e.response.status_code}, Response: {e.response.text}")
    return


# -----------------------------------------------------------------------------
@click.command()
@click.pass_context  # Pass the context to the command
def create_organization_network(ctx):
  org_id = click.prompt("Enter organization id", type=str)
  api_path = f"/organizations/{org_id}/networks"
  manager = ctx.obj

  # Post (Create) API endpoint

  try:
    payload_file = click.prompt("Enter payload file", type=str)
    payload = parse(payload_file)
    data = manager._api_post(api_path, payload)
  
    if data:
      tr = [
        data["id"],
        data["name"],
        data["organizationId"],
        data["productTypes"],
        data["timeZone"],
        data["tags"],
        data["enrollmentString"],
        data["url"],
        data["isBoundToConfigTemplate"],
        data["isVirtual"]
      ]

      print("\nNetwork Information:")
      print("--------------------")
      print("Network ID: ", tr[0])
      print("Network Name: ", tr[1])
      print("Organization ID: ", tr[2])
      print("Product Types: ", tr[3])
      print("Time Zone: ", tr[4])
      print("Tags: ", tr[5])
      print("Enrollment String: ", tr[6])
      print("URL: ", tr[7])
      print("Bound to Config Template: ", tr[8])
      print("Virtual: ", tr[9])

    return

  except requests.exceptions.RequestException as e:
    print(f"An unexpected error occurred: {e}")
    if hasattr(e, "response") and e.response is not None:
      print(f"Status: {e.response.status_code}, Response: {e.response.text}")
    return
  

  # -----------------------------------------------------------------------------
@click.command()
@click.pass_context  # Pass the context to the command
def delete_network(ctx):
  network_id = click.prompt("Enter network id", type=str)
  api_path = f"/networks/{network_id}"
  manager = ctx.obj

  # Delete API endpoint

  try:
    data = manager._api_delete(api_path)
  
    if data:
      print(data["message"])
      return

  except requests.exceptions.RequestException as e:
    print(f"An unexpected error occurred: {e}")
    if hasattr(e, "response") and e.response is not None:
      print(f"Status: {e.response.status_code}, Response: {e.response.text}")
    return
  

# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Add commands to the cli group
    cli.add_command(get_organization_networks)
    cli.add_command(create_organization_network)
    cli.add_command(delete_network)

    # Call the cli group.
    cli()