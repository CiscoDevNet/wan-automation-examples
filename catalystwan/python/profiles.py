#! /usr/bin/env python3
# =========================================================================
# Cisco Catalyst SD-WAN Manager APIs
# =========================================================================
#
# UX 2.0 - Feature Profiles and Parcels on SD-WAN Manager
#
# Description:
#  - List all feature profiles
#  - Give feature profile details
#  - Give parcel details
#
# =========================================================================

import logging

import click
import tabulate

# Import the new unified Manager class and the credentials function
from utilities.manager import Manager, get_manager_credentials_from_env
from utilities.tools import convert_timestamp, save_payload


# --- Profile Class Definition ---
class Profile:
    """
    Represents a Cisco SD-WAN Feature Profile, holding both summary
    and detailed information (including parcels and subparcels).
    """

    def __init__(self, profile_data: dict):
        # Attributes common to both summary and detailed payloads
        self.profile_name = profile_data.get("profileName", "N/A")
        self.profile_id = profile_data.get("profileId", "N/A")
        self.profile_type = profile_data.get("profileType", "N/A")
        self.description = profile_data.get("description", "")
        self.created_by = profile_data.get("createdBy", "N/A")
        self.last_updated_by = profile_data.get("lastUpdatedBy", "N/A")
        self.created_on = convert_timestamp(profile_data.get("createdOn"))
        self.last_updated_on = convert_timestamp(profile_data.get("lastUpdatedOn"))

        # Attributes typically present in the summary API response
        # (or top-level of detail, but 'solution' is often only in summary list)
        self.solution = profile_data.get("solution", "N/A")

        # Attributes for detailed profile information (initialized as empty/None)
        self.total_parcels: int = profile_data.get("profileParcelCount", 0)
        self.associated_parcels: list[ProfileParcel] = []

        # If 'associatedProfileParcels' key exists, it means we have detailed data
        # and should populate the nested parcel objects.
        if "associatedProfileParcels" in profile_data:
            self.associated_parcels = [ProfileParcel(p) for p in profile_data.get("associatedProfileParcels", [])]

        self._raw_data = profile_data  # Keep raw data for completeness if needed

    def to_summary_list_row(self) -> list[str]:
        """
        Returns a list of profile attributes suitable for tabular display in a summary view.
        """
        return [
            self.profile_name,
            self.profile_id,
            self.profile_type,
            self.solution,
            self.created_by,
            self.last_updated_by,
            self.description,
        ]

    def to_detail_string_list(self) -> list[str]:
        """
        Returns a list of formatted strings representing the entire detailed profile.
        This method should only be called if the profile object was initialized
        with detailed data (i.e., associated_parcels are populated).
        """
        output = []
        output.append("--- Cisco SD-WAN Profile Details ---\n")
        output.append(f"Profile Name: {self.profile_name}")
        output.append(f"Description: {self.description}")
        output.append(f"Profile Type: {self.profile_type}")
        output.append(f"Profile ID: {self.profile_id}")
        output.append(f"Created By: {self.created_by}")
        output.append(f"Last Updated By: {self.last_updated_by}")
        output.append(f"Created On: {self.created_on}")
        output.append(f"Last Updated On: {self.last_updated_on}")
        output.append(f"Total Parcels: {self.total_parcels}")
        output.append("\n--- Associated Profile Parcels ---")

        if not self.associated_parcels:
            output.append("No associated parcels found.")
        else:
            for i, parcel in enumerate(self.associated_parcels):
                output.extend(parcel.to_string_list(i))
        return output

    def __repr__(self):
        detail_status = "loaded" if self.associated_parcels else "not loaded"
        return f"Profile(id='{self.profile_id}', name='{self.profile_name}', type='{self.profile_type}', detail_status='{detail_status}')"


# --- Parcel class definition ---
class ProfileParcel:
    """
    Represents an associated parcel within a feature profile.
    """

    def __init__(self, parcel_data: dict):
        self.parcel_type = parcel_data.get("parcelType", "N/A")
        self.parcel_id = parcel_data.get("parcelId", "N/A")

        payload = parcel_data.get("payload", {})
        self.name = payload.get("name", "N/A")
        self.description = payload.get("description", "N/A")

        self.created_by = parcel_data.get("createdBy", "N/A")
        self.last_updated_by = parcel_data.get("lastUpdatedBy", "N/A")
        self.created_on = convert_timestamp(parcel_data.get("createdOn"))
        self.last_updated_on = convert_timestamp(parcel_data.get("lastUpdatedOn"))

        self.subparcels: list[SubParcel] = [SubParcel(sp) for sp in parcel_data.get("subparcels", [])]

    def to_string_list(self, index: int, indent_level: int = 0) -> list[str]:
        """
        Returns a list of formatted strings representing the parcel details.
        """
        indent = "  " * indent_level
        output = []
        output.append(f"\n{indent}  Parcel {index + 1}:")
        output.append(f"{indent}    Parcel Type: {self.parcel_type}")
        output.append(f"{indent}    Parcel ID: {self.parcel_id}")
        output.append(f"{indent}    Name: {self.name}")
        output.append(f"{indent}    Description: {self.description}")
        output.append(f"{indent}    Created By: {self.created_by}")
        output.append(f"{indent}    Last Updated By: {self.last_updated_by}")
        output.append(f"{indent}    Created On: {self.created_on}")
        output.append(f"{indent}    Last Updated On: {self.last_updated_on}")

        if self.subparcels:
            output.append(f"\n{indent}    --- Associated Sub-Parcels ---")
            for j, sub_parcel in enumerate(self.subparcels):
                output.append(f"\n{indent}      Sub-Parcel {j + 1}:")
                output.extend(sub_parcel.to_string_list(indent_level + 1))
        return output

    def __repr__(self):
        return f"ProfileParcel(id='{self.parcel_id}', name='{self.name}', subparcels={len(self.subparcels)})"


# --- Sub-parcel class definition ---
class SubParcel:
    """
    Represents a sub-parcel within a feature profile parcel.
    """

    def __init__(self, sub_parcel_data: dict):
        self.parcel_type = sub_parcel_data.get("parcelType", "N/A")
        self.parcel_id = sub_parcel_data.get("parcelId", "N/A")

        payload = sub_parcel_data.get("payload", {})
        self.name = payload.get("name", "N/A")
        self.description = payload.get("description", "N/A")

        self.created_by = sub_parcel_data.get("createdBy", "N/A")
        self.last_updated_by = sub_parcel_data.get("lastUpdatedBy", "N/A")
        self.created_on = convert_timestamp(sub_parcel_data.get("createdOn"))
        self.last_updated_on = convert_timestamp(sub_parcel_data.get("lastUpdatedOn"))

    def to_string_list(self, indent_level: int = 0) -> list[str]:
        """
        Returns a list of formatted strings representing the sub-parcel details.
        """
        indent = "  " * indent_level
        output = []
        output.append(f"{indent}      Parcel Type: {self.parcel_type}")
        output.append(f"{indent}      Parcel ID: {self.parcel_id}")
        output.append(f"{indent}      Name: {self.name}")
        output.append(f"{indent}      Description: {self.description}")
        output.append(f"{indent}      Created By: {self.created_by}")
        output.append(f"{indent}      Last Updated By: {self.last_updated_by}")
        output.append(f"{indent}      Created On: {self.created_on}")
        output.append(f"{indent}      Last Updated On: {self.last_updated_on}")
        return output

    def __repr__(self):
        return f"SubParcel(id='{self.parcel_id}', name='{self.name}')"


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


# -----------------------------------------------------------------------------
@click.command()
@click.pass_context  # Pass the context to the command
@click.option("--profile-id", "profile_id", required=True, help="Feature profile ID")
@click.option("--bfd-parcel-id", "parcel_id", required=True, help="BFD parcel ID")
def get_bfd(ctx, profile_id: str, parcel_id: str) -> dict:
    """Get BFD configuration for a given feature profile and parcel ID

    Args:
        --profile-id <Feature profile ID>
        --bfd-parcel-id: <BFD parcel ID>

    Returns:
        dict: BFD configuration data
    """

    # Get manager from context
    manager = ctx.obj

    api_path = f"/v1/feature-profile/sdwan/system/{profile_id}/bfd/{parcel_id}"
    payload = manager._api_get(api_path)
    data = payload.get("payload", [])

    save_payload(payload, "bfd", "output/config-groups/")
    save_payload(data, "bfd", "output/config-groups/")

    click.echo(f"BFD configuration retrieved for profile {profile_id} and parcel {parcel_id}.")
    return data


# -----------------------------------------------------------------------------
@click.command()
@click.argument("profile_id")  # Declare profile_id as a command-line argument
@click.option(
    "--type",
    "profile_type",
    type=click.Choice(["system", "transport", "service", "cli", "policy-object"], case_sensitive=False),
    required=False,
    help="Profile type (system, transport, service, cli, policy-object)",
)
@click.pass_context  # Pass the context to the command
def get_profile_details(ctx, profile_id: str, profile_type: str | None) -> Profile | None:  # <--- Type hint change
    """
    Get detailed information for a specific feature profile, store it in a Profile object,
    and then print the object's formatted details. The profile_type can be auto-discovered.
    """
    # Get manager from context
    manager = ctx.obj

    # --- Discover profile_type if not provided ---
    if profile_type is None:
        click.echo(f"Profile type not provided. Attempting to auto-discover for profile ID '{profile_id}'...")
        summary_api_path = "/v1/feature-profile/sdwan"
        summary_data = manager._api_get(summary_api_path)

        if not summary_data:
            click.echo("Failed to retrieve summary profiles to auto-discover type. Cannot proceed.")
            return None

        found_type = None
        for p in summary_data:
            if p.get("profileId") == profile_id:
                found_type = p.get("profileType")
                break

        if found_type:
            profile_type = found_type
            click.echo(f"Auto-discovered profile type: '{profile_type}' for ID '{profile_id}'.\n")
        else:
            click.echo(f"Error: Could not find profile ID '{profile_id}' in summary list. Please provide --type explicitly if you believe it exists.")
            return None

    api_path = f"/v1/feature-profile/sdwan/{profile_type}/{profile_id}"
    payload = manager._api_get(api_path)

    if not payload:
        click.echo(f"No detailed profile data found for ID '{profile_id}' and type '{profile_type}'.")
        return None  # Return None if no data is found

    save_payload(payload, f"profile_details_{profile_type}", "output/config-groups/")

    # Create the Profile object using the detailed payload
    profile_obj = Profile(payload)

    # Generate the output list from the object's detail method and print it
    output_lines = profile_obj.to_detail_string_list()
    click.echo("\n".join(output_lines))

    # Return the structured object
    return profile_obj


# -----------------------------------------------------------------------------
@click.command()
@click.pass_context  # Pass the context to the command
def get_profiles(ctx) -> list[Profile]:
    """
    Get the list of all profiles, store them as Profile objects (summary view),
    and then print them in a tabular format.
    """
    # Get manager from context
    manager = ctx.obj

    api_path = "/v1/feature-profile/sdwan"
    data = manager._api_get(api_path)
    save_payload(data, "profiles", "output/config-groups/")

    profile_objects: list[Profile] = []  # This list will store our custom Profile objects

    if not data:
        click.echo("No profiles found in the provided data.")
        return []  # Return an empty list of objects

    # Iterate through the raw data and create Profile objects (summary view)
    for profile_dict in data:
        profile_obj = Profile(profile_dict)
        profile_objects.append(profile_obj)

    # Prepare data for tabulate from the list of Profile objects
    # We use the to_summary_list_row() method of each Profile object
    tabulate_data = [p.to_summary_list_row() for p in profile_objects]

    headers = [
        "Profile Name",
        "Profile ID",
        "Profile Type",
        "Solution",
        "Created By",
        "Last Updated By",
        "Description",
    ]

    # Print the object (list of Profile objects) in a tabular format
    click.echo(tabulate.tabulate(tabulate_data, headers=headers, tablefmt="grid"))

    # Return the list of Profile objects for potential further processing
    return profile_objects


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Add commands to the cli group
    cli.add_command(get_profiles)
    cli.add_command(get_profile_details)
    cli.add_command(get_bfd)

    # Call the cli group.
    # The authentication and logout will be handled by the cli group's context and teardown callback.
    cli()
