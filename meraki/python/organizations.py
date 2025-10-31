# ! /usr/bin/env python3
# =========================================================================
# Cisco Meraki Dashboard APIs - Organizations
# Revision 1.0 - 10/21/2025
# =========================================================================
#
# Description:
#   Get organizations
#   Create a new organization
#   Delete an existing organization (Organization must have no networks, 
#   users, licenses, or devices claimed in its inventory.)
#

import click
import requests
import json
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
def get_organizations(ctx):
  api_path = "/organizations"
  manager = ctx.obj

  # Get (Read) API endpoint
  try:
    data = manager._api_get(api_path)

    for item in data:
      tr = [
        item["id"],
        item["name"],
        item["url"],
        item["samlConsumerUrls"],
        item["samlConsumerUrl"],
        item["api"]["enabled"],
        item["licensing"]["model"],
        item["cloud"]["region"]["name"],
        item["cloud"]["region"]["host"]["name"],
        item["management"]["details"]
      ]

      print("\nOrganization Information:")
      print("-------------------------")
      print("Organization ID: ", tr[0])
      print("Organization name: ", tr[1])
      print("Organization URL: ", tr[2])
      print("Region Name: ", tr[7])
      print("Location Name: ", tr[8])
      print("API Access Enabled: ", tr[5])
      print("Licensing model: ", tr[6])
      print("Management Details: ", tr[9])
      print("SAML consumer URLs: ", tr[3])
      print("SAML consumer URL: ", tr[4])

    return
  
  except requests.exceptions.RequestException as e:
    print(f"An unexpected error occurred: {e}")
    if hasattr(e, "response") and e.response is not None:
      print(f"Status: {e.response.status_code}, Response: {e.response.text}")
    return


# -----------------------------------------------------------------------------
@click.command()
@click.pass_context  # Pass the context to the command
def create_organization(ctx):
  api_path = "/organizations"
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
        data["url"],
        data["api"]["enabled"],
        data["licensing"]["model"],
        data["cloud"]["region"]["name"],
        data["cloud"]["region"]["host"]["name"],
        data["management"]["details"]
      ]

      print("\nOrganization Information:")
      print("-------------------------")
      print("Organization ID: ", tr[0])
      print("Organization name: ", tr[1])
      print("Organization URL: ", tr[2])
      print("Region Name: ", tr[5])
      print("Location Name: ", tr[6])
      print("API Access Enabled: ", tr[3])
      print("Licensing model: ", tr[4])
      print("Management Details: ", tr[7])

    return

  except requests.exceptions.RequestException as e:
    print(f"An unexpected error occurred: {e}")
    if hasattr(e, "response") and e.response is not None:
      print(f"Status: {e.response.status_code}, Response: {e.response.text}")
    return


# -----------------------------------------------------------------------------
@click.command()
@click.pass_context  # Pass the context to the command
def delete_organization(ctx):
  org_id = click.prompt("Enter organization id", type=str)
  api_path = f"/organizations/{org_id}"
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
    cli.add_command(get_organizations)
    cli.add_command(create_organization)
    cli.add_command(delete_organization)

    # Call the cli group.
    cli()
