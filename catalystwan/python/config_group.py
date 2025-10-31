#! /usr/bin/env python3
# =========================================================================
# Cisco Catalyst SD-WAN Manager APIs
# =========================================================================
#
# UX 2.0 - Configuration Groups on SD-WAN Manager
#
# Description:
#  - List all config groups
#  - List associated feature profiles for each config group
#
# =========================================================================

import logging

import click

# Import the new unified Manager class and the credentials function
from utilities.manager import Manager, get_manager_credentials_from_env
from utilities.tools import convert_timestamp, save_payload


# -----------------------------------------------------------------------------
@click.group()
@click.pass_context  # Pass the context object to the cli group
def cli(ctx):
    """Command line tool for to collect application names and tunnel performances"""
    log_file_path = "sdwan_api.log"

    logging.basicConfig(
        filename=log_file_path,  # <--- Specify the log file
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


class Profile:
    """Represents an SD-WAN Config Group Profile."""

    def __init__(self, data):
        self.name = data.get("name", "N/A")
        self.id = data.get("id", "N/A")
        self.solution = data.get("solution", "N/A")
        self.type = data.get("type", "N/A")
        self.description = data.get("description", "N/A")
        self.created_by = data.get("createdBy", "N/A")
        self.last_updated_by = data.get("lastUpdatedBy", "N/A")
        self.created_on = convert_timestamp(data.get("createdOn"))
        self.last_updated_on = convert_timestamp(data.get("lastUpdatedOn"))
        self.profile_parcel_count = data.get("profileParcelCount", 0)

    def __str__(self):
        return (
            f"    Profile Name: {self.name}\n"
            f"    Profile ID: {self.id}\n"
            f"    Solution: {self.solution}\n"
            f"    Type: {self.type}\n"
            f"    Description: {self.description}\n"
            f"    Created By: {self.created_by}\n"
            f"    Last Updated By: {self.last_updated_by}\n"
            f"    Created On: {self.created_on}\n"
            f"    Last Updated On: {self.last_updated_on}\n"
            f"    Profile Parcel Count: {self.profile_parcel_count}"
        )


class ConfigGroup:
    """Represents an SD-WAN Config Group."""

    def __init__(self, data):
        self.name = data.get("name", "N/A")
        self.id = data.get("id", "N/A")
        self.description = data.get("description", "N/A")
        self.solution = data.get("solution", "N/A")
        self.created_by = data.get("createdBy", "N/A")
        self.last_updated_by = data.get("lastUpdatedBy", "N/A")
        self.created_on = convert_timestamp(data.get("createdOn"))
        self.last_updated_on = convert_timestamp(data.get("lastUpdatedOn"))
        self.number_of_devices = data.get("numberOfDevices", 0)
        self.number_of_devices_up_to_date = data.get("numberOfDevicesUpToDate", 0)
        self.profiles = [Profile(p_data) for p_data in data.get("profiles", [])]

    def __str__(self):
        output_str = (
            f" Config Group Name: {self.name}\n"
            f" Config Group ID: {self.id}\n"
            f" Description: {self.description}\n"
            f" Solution: {self.solution}\n"
            f" Created By: {self.created_by}\n"
            f" Last Updated By: {self.last_updated_by}\n"
            f" Created On: {self.created_on}\n"
            f" Last Updated On: {self.last_updated_on}\n"
            f" Number of Devices: {self.number_of_devices}\n"
            f" Number of Devices Up To Date: {self.number_of_devices_up_to_date}"
        )
        if self.profiles:
            output_str += "\n\n--- Associated Profiles ---\n"
            for j, profile in enumerate(self.profiles):
                output_str += f"\n  Profile {j + 1}:\n{profile}"
        else:
            output_str += "\nNo associated profiles found for this config group."
        return output_str


# -----------------------------------------------------------------------------
@click.command()
@click.pass_context  # Pass the context to the command
def get_config_groups(ctx):
    """
    Get list of Config Groups and store them as objects.
    """
    manager = ctx.obj
    config_group_objects = []

    api_path = "/v1/config-group/"
    data = manager._api_get(api_path)

    if not data:
        click.echo("No config groups found")
        return []

    save_payload(data, "config_groups", "output/config-groups/")

    for config_group_data in data:
        config_group_objects.append(ConfigGroup(config_group_data))

    if not config_group_objects:
        click.echo("No config groups to display.")
        return

    for i, config_group in enumerate(config_group_objects):
        click.echo(f"\n*** Cisco SD-WAN Config Group Details ({i + 1}/{len(config_group_objects)}) ***\n")
        click.echo(str(config_group))


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Add commands to the cli group
    cli.add_command(get_config_groups)

    # Call the cli group.
    # The authentication and logout will be handled by the cli group's context and teardown callback.
    cli()
