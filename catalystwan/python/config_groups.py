#! /usr/bin/env python3
# =========================================================================
# Cisco Catalyst SD-WAN Manager APIs
# =========================================================================
#
# SD-WAN/SD-Routing UX 2.0 Device Config
# Using Config Group and Feature Profiles
#
# Description:
#   Get config-groups and feature profiles
#   Get devices associated with config-group
#   Get deployment values
#   Save everything under output folder
#
# Output folder hierarchy:
#   config_groups
#       associated
#       groups
#       values
#
#   feature_profiles
#       cli
#       system
#       transport
#       service
#       policy-object
#
# =========================================================================

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional  # Added for type hinting clarity

import requests

# Import the new unified Manager class and the credentials function
from manager import Manager


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
class SDRoutingFeatureProfile:
    """
    Helper class to fetch detailed payload for a single SD-Routing feature profile.
    """

    payload = None

    def __init__(
        self, manager, id, name, solution, type, createdby, lastupdatedby, lastupdatedon
    ):
        self.manager = manager
        self.id = id
        self.name = name
        self.solution = solution
        self.type = type
        self.createdby = createdby
        self.lastupdatedby = lastupdatedby
        self.lastupdatedon = lastupdatedon

        url_base = "/v1/feature-profile/sd-routing/"

        match self.type:
            case "system":
                urlp = url_base + "system/"
            case "transport":
                urlp = url_base + "transport/"
            case "service":
                urlp = url_base + "service/"
            case "cli":
                urlp = url_base + "cli/"
            # case "policy-object": # This case was commented out in original, keeping it that way
            #     urlp = url_base + "policy-object/"
            case _:
                print(f"{self.type} type not supported for SD-Routing feature profile")
                return

        # Get profile_id payload
        # NOTE: details option has been added in 20.12
        path = urlp + self.id
        params = {"details": "true"}
        print(f"Fetching details for profile ID {self.id} from {path}")
        try:
            self.payload = self.manager._api_get(path, params=params)
            self.profile_name = self.payload["profileName"]
            self.profile_type = self.payload["profileType"]
            self.solution = self.payload["solution"]

        except requests.exceptions.RequestException as e:
            print(f"An unexpected error occurred: {e}")
            self.payload = None  # Indicate failure to fetch
            if hasattr(e, "response") and e.response is not None:
                print(f"Status: {e.response.status_code}, Response: {e.response.text}")
            return


# -----------------------------------------------------------------------------
class SDRoutingProfileTable:
    def __init__(self, manager: Manager):
        self.manager = manager
        self.profiles_table = []  # This will store generic Profile objects

        api_path_summary = "/v1/feature-profile/sd-routing/"

        # Get list of profiles (summary)
        try:
            summary_data = self.manager._api_get(api_path_summary)
            save_json(
                summary_data,
                "profiles_table",
                "output/payloads/feature_profiles/sdrouting/",
            )  # save payload response

        except requests.exceptions.RequestException as e:
            print(f"An unexpected error occurred: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Status: {e.response.status_code}, Response: {e.response.text}")
            return

        # For each summary item, fetch full details and create a Profile object
        for item in summary_data:
            profile_id = item["profileId"]
            profile_name = item["profileName"]
            profile_solution = item["solution"]
            profile_type = item["profileType"]
            profile_createdby = item["createdBy"]
            profile_lastupdated = item["lastUpdatedBy"]
            profile_lastUpdatedOn = item["lastUpdatedOn"]

            # Use SDRoutingFeatureProfile to fetch the detailed payload
            sdrouting_feature_profile_fetcher = SDRoutingFeatureProfile(
                self.manager,
                profile_id,
                profile_name,
                profile_solution,
                profile_type,
                profile_createdby,
                profile_lastupdated,
                profile_lastUpdatedOn,
            )

            if not sdrouting_feature_profile_fetcher.payload:
                print(
                    f"Skipping profile ID {profile_id} due to unsupported type or fetch error."
                )
                continue

            full_profile_payload = sdrouting_feature_profile_fetcher.payload
            save_json(
                full_profile_payload,
                f"{profile_name}",
                "output/payloads/feature_profiles/sdrouting/",
            )

            # Now, use the full_profile_payload to create a generic Profile object
            profile = Profile(
                id=full_profile_payload.get("profileId"),
                name=full_profile_payload.get("profileName"),
                solution=full_profile_payload.get("solution"),
                type=full_profile_payload.get("profileType"),
                description=full_profile_payload.get("description"),
                lastUpdatedBy=full_profile_payload.get("lastUpdatedBy"),
                lastUpdatedOn=full_profile_payload.get("lastUpdatedOn"),
                createdBy=full_profile_payload.get("createdBy"),
                createdOn=full_profile_payload.get("createdOn"),
                profileParcelCount=full_profile_payload.get("profileParcelCount"),
                origin=full_profile_payload.get("origin"),
            )
            self.profiles_table.append(profile)

    def list(self):
        print("\n--- SD-Routing Feature Profiles\n")
        for profile in self.profiles_table:
            profile.display()  # Use the display method of the generic Profile object

    def list_categories(self):
        print("\n--- SD-Routing Feature Profiles per category\n")

        categories = [
            "system",
            "transport",
            "service",
            "cli",
            "policy-object",
        ]

        for category_item in categories:
            print(f"\n--- Category: {category_item.upper()} ---")
            found_in_category = False
            for profile in self.profiles_table:
                if profile.type == category_item:
                    profile.display()
                    found_in_category = True
            if not found_in_category:
                print(f"    No profiles found for category '{category_item}'.")

    def save_profiles(self, directory="output/feature_profiles/sdrouting"):
        print(f"\n--- Saving SD-Routing Feature Profiles in {directory}\n")
        # Use the save_to_file method of the generic Profile object
        for profile in self.profiles_table:
            profile.save_to_file(directory)


# -----------------------------------------------------------------------------
class SDWANFeatureProfile:
    """
    Helper class to fetch detailed payload for a single SD-WAN feature profile.
    """

    payload = None

    def __init__(
        self, manager, id, name, solution, type, createdby, lastupdatedby, lastupdatedon
    ):
        self.manager = manager
        self.id = id
        self.name = name
        self.solution = solution
        self.type = type
        self.createdby = createdby
        self.lastupdatedby = lastupdatedby
        self.lastupdatedon = lastupdatedon

        print(f"Fetching details for profile {self.name} ({self.id})")

        api_url = "/v1/feature-profile/sdwan/"

        match self.type:
            case "system":
                urlp = api_url + "system/"
            case "transport":
                urlp = api_url + "transport/"
            case "service":
                urlp = api_url + "service/"
            case "cli":
                urlp = api_url + "cli/"
            # case "policy-object": # This case was commented out in original, keeping it that way
            #     urlp = api_url + "policy-object/"
            case _:
                print(f"{self.type} type not supported for SD-WAN feature profile")
                return

        # Get profile_id payload
        # NOTE: details option has been added in 20.12
        path = urlp + self.id
        params = {"details": "true"}
        try:
            self.payload = self.manager._api_get(path, params=params)
            self.profile_name = self.payload.get("profileName")
            self.profile_type = self.payload.get("profileType")
            self.solution = self.payload.get("solution")

        except requests.exceptions.RequestException as e:
            print(f"An unexpected error occurred: {e}")
            self.payload = None  # Indicate failure to fetch
            if hasattr(e, "response") and e.response is not None:
                print(f"Status: {e.response.status_code}, Response: {e.response.text}")
            return


# -----------------------------------------------------------------------------
class SDWANProfileTable:
    def __init__(self, manager: Manager):
        self.manager = manager
        self.profiles_table = []  # This will now store generic Profile objects

        api_path_summary = "/v1/feature-profile/sdwan/"

        print("\n--- Collecting Feature Profiles ---")

        # Get list of profiles (summary)
        try:
            summary_data = self.manager._api_get(api_path_summary)
            save_json(
                summary_data,
                "profiles_table",
                "output/payloads/feature_profiles/sdwan/",
            )  # save payload response

        except requests.exceptions.RequestException as e:
            print(f"An unexpected error occurred: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"Status: {e.response.status_code}, Response: {e.response.text}")
            return

        # For each summary item, fetch full details and create a Profile object
        for item in summary_data:
            profile_id = item["profileId"]
            profile_name = item["profileName"]
            profile_solution = item["solution"]
            profile_type = item["profileType"]
            profile_createdby = item["createdBy"]
            profile_lastupdated = item["lastUpdatedBy"]
            profile_lastUpdatedOn = item["lastUpdatedOn"]

            # Use SDWANFeatureProfile to fetch the detailed payload
            # This class makes the API call for details of a single profile
            sdwan_feature_profile_fetcher = SDWANFeatureProfile(
                self.manager,
                profile_id,
                profile_name,
                profile_solution,
                profile_type,
                profile_createdby,
                profile_lastupdated,
                profile_lastUpdatedOn,
            )
            if not sdwan_feature_profile_fetcher.payload:
                print(
                    f"Skipping profile {profile_name} ({profile_id}) due to unsupported type or fetch error."
                )
                continue
            full_profile_payload = sdwan_feature_profile_fetcher.payload
            save_json(
                full_profile_payload,
                f"{profile_name}",
                "output/payloads/feature_profiles/sdwan/",
            )

            # Now, use the full_profile_payload to create a generic Profile object
            # Using .get() for robustness in case a key is missing in the payload
            profile = Profile(
                id=full_profile_payload.get("profileId"),
                name=full_profile_payload.get("profileName"),
                solution=full_profile_payload.get("solution"),
                type=full_profile_payload.get("profileType"),
                description=full_profile_payload.get("description"),
                lastUpdatedBy=full_profile_payload.get("lastUpdatedBy"),
                lastUpdatedOn=full_profile_payload.get("lastUpdatedOn"),
                createdBy=full_profile_payload.get("createdBy"),
                createdOn=full_profile_payload.get("createdOn"),
                profileParcelCount=full_profile_payload.get("profileParcelCount"),
                origin=full_profile_payload.get("origin"),
            )
            self.profiles_table.append(profile)

    def list(self):
        print("\n--- SD-WAN Feature Profiles\n")
        for profile in self.profiles_table:
            profile.display()  # Use the display method of the generic Profile object

    def list_categories(self):
        print("\n--- SD-WAN Feature Profiles per category\n")

        categories = [
            "system",
            "transport",
            "service",
            "cli",
            "policy-object",
        ]

        for category_item in categories:
            print(f"\n--- Category: {category_item.upper()} ---")
            found_in_category = False
            for profile in self.profiles_table:
                if profile.type == category_item:
                    profile.display()
                    found_in_category = True
            if not found_in_category:
                print(f"    No profiles found for category '{category_item}'.")

    def save_profiles(self, directory="output/feature_profiles/sdwan"):
        print(f"\n--- Saving SD-WAN Feature Profiles in {directory}\n")
        # Use the save_to_file method of the generic Profile object
        for profile in self.profiles_table:
            profile.save_to_file(directory)


# -----------------------------------------------------------------------------
class Device:
    """
    Represents a device associated with a configuration group, including its variables.
    """

    def __init__(self, device_data: dict):
        self.id = device_data.get(
            "id"
        )  # This 'id' comes from the /device/associate API
        self.site_name = device_data.get("site-name")
        self.host_name = device_data.get("host-name")
        self.site_id = device_data.get("site-id")
        self.device_model = device_data.get("deviceModel")
        self.tags = device_data.get("tags", [])
        self.device_lock = device_data.get("device-lock")
        self.added_by_rule = device_data.get("addedByRule")
        self.config_status_message = device_data.get("configStatusMessage")
        self.device_ip = device_data.get("deviceIP")
        self.config_group_last_updated_on = device_data.get("configGroupLastUpdatedOn")
        self.unsupported_features = device_data.get("unsupportedFeatures", [])
        self.hierarchy_name_path = device_data.get("hierarchyNamePath")
        self.hierarchy_type_path = device_data.get("hierarchyTypePath")
        self.group_topology_label = device_data.get("groupTopologyLabel")
        self.config_group_up_to_date = device_data.get("configGroupUpToDate")
        self.is_deployable = device_data.get("isDeployable")
        self.license_status = device_data.get("licenseStatus")
        self.variables: List[
            Dict[str, str]
        ] = []  # New attribute to store device variables

    def to_dict(self):
        """Converts the Device object to a dictionary for JSON serialization."""
        data = {
            "id": self.id,
            "site-name": self.site_name,
            "host-name": self.host_name,
            "site-id": self.site_id,
            "deviceModel": self.device_model,
            "tags": self.tags,
            "device-lock": self.device_lock,
            "addedByRule": self.added_by_rule,
            "configStatusMessage": self.config_status_message,
            "deviceIP": self.device_ip,
            "configGroupLastUpdatedOn": self.config_group_last_updated_on,
            "unsupportedFeatures": self.unsupported_features,
            "hierarchyNamePath": self.hierarchy_name_path,
            "hierarchyTypePath": self.hierarchy_type_path,
            "groupTopologyLabel": self.group_topology_label,
            "configGroupUpToDate": self.config_group_up_to_date,
            "isDeployable": self.is_deployable,
            "licenseStatus": self.license_status,
        }
        if self.variables:  # Only include if variables exist
            data["variables"] = self.variables
        return data

    def display(self):
        """Prints the details of the device."""
        print(f"    > Hostname: {self.host_name}")
        print(f"        ID: {self.id}")
        print(f"        IP: {self.device_ip}")
        print(f"        Model: {self.device_model}")
        print(f"        Site: {self.site_name} (ID: {self.site_id})")
        print(f"        hierarchy name: {self.hierarchy_name_path}")
        print(f"        hierarchy type: {self.hierarchy_type_path}")
        print(f"        Config Status: {self.config_status_message}")
        if self.variables:
            print(f"        Variables ({len(self.variables)}):")
            for var in self.variables:
                # Some variables might not have a 'value' key (e.g., 'ipv6_strict_control')
                print(
                    f"          - Name: {var.get('name')}, Value: {var.get('value', 'N/A')}, Type: {var.get('type', 'N/A')}"
                )
        # Add more details as needed

    def save_to_file(self, directory="output/config_groups/associated"):
        """
        Saves the Device object's data to a JSON file.

        Args:
            directory (str): The directory where the file will be saved.
            Defaults to 'output/config_groups/associated'.
        """
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        # Sanitize the hostname to create a valid filename
        sanitized_name = "".join(
            c for c in self.host_name if c.isalnum() or c in (" ", ".", "_", "-")
        ).strip()
        sanitized_name = sanitized_name.replace(" ", "_")

        if not sanitized_name:
            filename = f"device_{self.id}.json"
        else:
            filename = f"{sanitized_name}.json"

        filepath = os.path.join(directory, filename)

        try:
            with open(filepath, "w") as f:
                json.dump(self.to_dict(), f, indent=4)
            print(f"Successfully saved Device '{self.host_name}' to '{filepath}'")
        except Exception as e:
            print(f"Error saving Device '{self.host_name}' to '{filepath}': {e}")


# -----------------------------------------------------------------------------
class Profile:
    """
    Represents a feature profile (SD-WAN or SD-Routing).
    """

    def __init__(
        self,
        id,
        name,
        solution,
        type,
        description,
        lastUpdatedBy,
        lastUpdatedOn,
        createdBy,
        createdOn,
        profileParcelCount,
        origin,
    ):
        self.id = id
        self.name = name
        self.solution = solution
        self.type = type
        self.description = description
        self.lastUpdatedBy = lastUpdatedBy
        self.lastUpdatedOn = self._convert_timestamp_to_datetime(lastUpdatedOn)
        self.createdBy = createdBy
        self.createdOn = self._convert_timestamp_to_datetime(createdOn)
        self.profileParcelCount = profileParcelCount
        self.origin = origin

    def _convert_timestamp_to_datetime(self, timestamp):
        """Converts a Unix timestamp (milliseconds) to a datetime object."""
        if timestamp is not None:
            return datetime.fromtimestamp(timestamp / 1000)  # Convert ms to seconds
        return None

    def _convert_datetime_to_timestamp(self, dt_obj):
        """Converts a datetime object to a Unix timestamp (milliseconds)."""
        if dt_obj is not None:
            return int(dt_obj.timestamp() * 1000)
        return None

    def to_dict(self):
        """Converts the Profile object to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "solution": self.solution,
            "type": self.type,
            "description": self.description,
            "lastUpdatedBy": self.lastUpdatedBy,
            "lastUpdatedOn": self._convert_datetime_to_timestamp(self.lastUpdatedOn),
            "createdBy": self.createdBy,
            "createdOn": self._convert_datetime_to_timestamp(self.createdOn),
            "profileParcelCount": self.profileParcelCount,
            "origin": self.origin,
        }

    def save_to_file(self, base_directory="output/feature_profiles"):
        """
        Saves the Profile object's data to a JSON file within a subfolder
        based on its type (self.type).

        Args:
            base_directory (str): The base directory where type-specific subfolders
            will be created. Defaults to 'output/feature_profiles'.
        """
        if not self.type:
            print(
                f"Warning: Profile '{self.name}' (ID: {self.id}) has no type. Saving to base directory."
            )
            target_directory = base_directory
        else:
            # Sanitize the type name for directory creation (good practice for file paths)
            # This keeps alphanumeric characters, underscores, and hyphens.
            sanitized_type = "".join(
                c for c in self.type if c.isalnum() or c in ("_", "-")
            ).strip()
            if not sanitized_type:
                sanitized_type = (
                    "unknown_type"  # Fallback if type becomes empty after sanitization
                )

            # Construct the full path for the type-specific subfolder
            target_directory = os.path.join(base_directory, sanitized_type)

        # Create the target directory (including any necessary parent directories)
        # if it doesn't exist. exist_ok=True prevents an error if the directory already exists.
        try:
            os.makedirs(target_directory, exist_ok=True)
        except OSError as e:
            print(f"Error creating directory '{target_directory}': {e}")
            return  # Exit the function if directory creation fails

        # Sanitize the profile name to create a valid filename
        # Replace non-alphanumeric characters (except spaces, dots, underscores, hyphens) with nothing
        # Then replace spaces with underscores for better filename compatibility
        sanitized_name = "".join(
            c for c in self.name if c.isalnum() or c in (" ", ".", "_", "-")
        ).strip()
        sanitized_name = sanitized_name.replace(" ", "_")

        # Fallback if name becomes empty or invalid after sanitization
        if not sanitized_name:
            filename = f"profile_{self.id}.json"
        else:
            filename = f"{sanitized_name}.json"

        # Construct the full file path
        filepath = os.path.join(target_directory, filename)

        try:
            with open(filepath, "w") as f:
                json.dump(
                    self.to_dict(), f, indent=4
                )  # Use indent=4 for pretty-printing JSON
            print(f"Successfully saved Profile '{self.name}' to '{filepath}'")
        except Exception as e:
            print(f"Error saving Profile '{self.name}' to '{filepath}': {e}")

    def __repr__(self):
        return f"Profile(name='{self.name}', id='{self.id}', type='{self.type}')"

    def display(self):
        """Prints the details of the profile."""
        print(f"    > Profile Name ❯ {self.name}")
        print(f"      ID: {self.id}")
        print(f"      Type: {self.type}")
        print(f"      Solution: {self.solution}")
        print(f"      Last Updated On: {self.lastUpdatedOn}")
        print(f"      Created On: {self.createdOn}")
        print(f"      Parcel Count: {self.profileParcelCount}")
        # print("-" * 40)  # Separator for readability


# -----------------------------------------------------------------------------
class ConfigGroup:
    """
    Represents a configuration group, its associated profiles, devices, and their deployment values.
    """

    def __init__(
        self,
        id,
        name,
        description,
        source,
        solution,
        lastUpdatedBy,
        lastUpdatedOn,
        createdBy,
        createdOn,
        profiles_data,
        version,
        state,
        devices_data,  # Raw list of device dictionaries from /device/associate
        numberOfDevices,
        numberOfDevicesUpToDate,
        origin,
        copyInfo,
        originInfo,
        topology,
        fullConfigCli,
        iosConfigCli,
        versionIncrementReason,
        device_variables_data: Optional[
            List[Dict[str, Any]]
        ] = None,  # Raw list of device variable dictionaries from /device/variables (extracted 'devices' list)
    ):
        self.id = id
        self.name = name
        self.description = description
        self.source = source
        self.solution = solution
        self.lastUpdatedBy = lastUpdatedBy
        self.lastUpdatedOn = self._convert_timestamp_to_datetime(lastUpdatedOn)
        self.createdBy = createdBy
        self.createdOn = self._convert_timestamp_to_datetime(createdOn)
        self.profiles = []

        # Get profiles list
        if profiles_data and isinstance(profiles_data, list):
            for profile_dict in profiles_data:
                self.profiles.append(
                    Profile(
                        id=profile_dict.get("id"),
                        name=profile_dict.get("name"),
                        solution=profile_dict.get("solution"),
                        type=profile_dict.get("type"),
                        description=profile_dict.get("description"),
                        lastUpdatedBy=profile_dict.get("lastUpdatedBy"),
                        lastUpdatedOn=profile_dict.get("lastUpdatedOn"),
                        createdBy=profile_dict.get("createdBy"),
                        createdOn=profile_dict.get("createdOn"),
                        profileParcelCount=profile_dict.get("profileParcelCount"),
                        origin=profile_dict.get("origin"),
                    )
                )

        # Get devices list and map variables to them
        self.devices = []
        if devices_data and isinstance(devices_data, list):
            # Create a temporary mapping of deviceId to Device object for easy lookup
            # The 'id' key comes from the /device/associate API response
            devices_by_id = {}
            for device_dict in devices_data:
                device_obj = Device(device_dict)
                self.devices.append(device_obj)
                devices_by_id[device_obj.id] = device_obj

            # Now, if device_variables_data is provided, assign variables to the correct Device objects
            if device_variables_data and isinstance(device_variables_data, list):
                for var_entry in device_variables_data:
                    # Use 'device-id' as per the API response for /device/variables
                    device_id_from_variables_payload = var_entry.get("device-id")
                    variables_list = var_entry.get("variables", [])

                    # Match the device ID from the variables payload to the Device object's ID
                    if (
                        device_id_from_variables_payload
                        and device_id_from_variables_payload in devices_by_id
                    ):
                        devices_by_id[
                            device_id_from_variables_payload
                        ].variables = variables_list

        self.version = version
        self.state = state
        self.numberOfDevices = numberOfDevices
        self.numberOfDevicesUpToDate = numberOfDevicesUpToDate
        self.origin = origin
        self.copyInfo = copyInfo
        self.originInfo = originInfo
        self.topology = topology
        self.fullConfigCli = fullConfigCli
        self.iosConfigCli = iosConfigCli
        self.versionIncrementReason = versionIncrementReason

    def _convert_timestamp_to_datetime(self, timestamp):
        """Converts a Unix timestamp (milliseconds) to a datetime object."""
        if timestamp is not None:
            return datetime.fromtimestamp(timestamp / 1000)  # Convert ms to seconds
        return None

    def _convert_datetime_to_timestamp(self, dt_obj):
        """Converts a datetime object to a Unix timestamp (milliseconds)."""
        if dt_obj is not None:
            return int(dt_obj.timestamp() * 1000)
        return None

    def to_dict(self):
        """Converts the ConfigGroup object to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "source": self.source,
            "solution": self.solution,
            "lastUpdatedBy": self.lastUpdatedBy,
            "lastUpdatedOn": self._convert_datetime_to_timestamp(self.lastUpdatedOn),
            "createdBy": self.createdBy,
            "createdOn": self._convert_datetime_to_timestamp(self.createdOn),
            "profiles": [
                profile.to_dict() for profile in self.profiles
            ],  # Recursively call to_dict for profiles
            "version": self.version,
            "state": self.state,
            "devices": [
                device.to_dict() for device in self.devices
            ],  # Recursively call to_dict for devices (now includes variables)
            "numberOfDevices": self.numberOfDevices,
            "numberOfDevicesUpToDate": self.numberOfDevicesUpToDate,
            "origin": self.origin,
            "copyInfo": self.copyInfo,
            "originInfo": self.originInfo,
            "topology": self.topology,
            "fullConfigCli": self.fullConfigCli,
            "iosConfigCli": self.iosConfigCli,
            "versionIncrementReason": self.versionIncrementReason,
        }

    def get_device_variables_for_saving(self) -> List[Dict[str, Any]]:
        """
        Extracts device variables from associated Device objects in the format
        expected for saving to the 'values' directory.
        """
        variables_list = []
        for device in self.devices:
            if device.variables:
                variables_list.append(
                    {
                        "deviceId": device.id,  # Using 'deviceId' for saving, as it's common practice
                        "hostName": device.host_name,  # Include hostname for readability
                        "variables": device.variables,
                    }
                )
        return variables_list

    def save_to_file(self, base_output_directory="output/config_groups"):
        """
        Saves the ConfigGroup object's data to a JSON file in a 'groups' subfolder,
        and also saves associated devices to an 'associated' subfolder within
        a config group specific directory.

        Args:
            base_output_directory (str): The root directory for saving config group related data.
            Defaults to 'output/config_groups'.
        """
        # Directory for the config group JSON itself (e.g., output/config_groups/groups)
        group_json_directory = os.path.join(base_output_directory, "groups")
        if not os.path.exists(group_json_directory):
            os.makedirs(group_json_directory, exist_ok=True)

        # Sanitize the name to create a valid filename
        sanitized_name = "".join(
            c for c in self.name if c.isalnum() or c in (" ", ".", "_", "-")
        ).strip()
        sanitized_name = sanitized_name.replace(" ", "_")

        if not sanitized_name:
            filename = f"config_group_{self.id}.json"
        else:
            filename = f"{sanitized_name}.json"

        filepath = os.path.join(group_json_directory, filename)

        try:
            with open(filepath, "w") as f:
                json.dump(self.to_dict(), f, indent=4)
            print(f"Successfully saved ConfigGroup '{self.name}' to '{filepath}'")
        except Exception as e:
            print(f"Error saving ConfigGroup '{self.name}' to '{filepath}': {e}")

        # Now, save associated devices to the 'associated' subdirectory
        if self.devices:
            # Create a specific directory for devices of this config group
            # e.g., output/config_groups/associated/My_Config_Group_Name/
            config_group_devices_directory = os.path.join(
                base_output_directory, "associated", sanitized_name
            )
            if not os.path.exists(config_group_devices_directory):
                os.makedirs(config_group_devices_directory, exist_ok=True)

            print(
                f"Saving associated devices for '{self.name}' to '{config_group_devices_directory}'..."
            )
            for device in self.devices:
                device.save_to_file(
                    config_group_devices_directory
                )  # Call the new method on Device

    def __repr__(self):
        return f"ConfigGroup(name='{self.name}', id='{self.id}', profiles_count={len(self.profiles)}, devices_count={len(self.devices)})"

    def display(self):
        """Prints the details of the config group and its profiles, and associated devices."""
        print(f"\n* Config Group: {self.name} (ID: {self.id})")
        print(f"  Description: {self.description}")
        print(f"  Solution: {self.solution}")
        print(f"  Last Updated On: {self.lastUpdatedOn}")
        print(f"  Number of Devices: {self.numberOfDevices}")
        print(f"  Number of Devices Up-to-Date: {self.numberOfDevicesUpToDate}")

        # Display Profiles
        print(f"  Profiles ({len(self.profiles)}):")
        if self.profiles:
            for profile in self.profiles:
                profile.display()
        else:
            print("    No profiles associated with this configuration group.")

        # Display Associated Devices (Now using Device objects)
        print(f"  Associated Devices ({len(self.devices)}):")
        if self.devices:
            for device in self.devices:
                device.display()  # Call the display method of the Device object
        else:
            print("    No devices associated with this configuration group.")


# -----------------------------------------------------------------------------
class ConfigGroupTable:
    """
    Manages a collection of configuration groups, fetching their details,
    associated devices, and device variables.
    """

    config_groups_objects: List["ConfigGroup"] = []  # Type hint for clarity

    def __init__(
        self,
        manager: Manager,
        sdwan_profiles_table: Optional["SDWANProfileTable"] = None,
        sdrouting_profiles_table: Optional["SDRoutingProfileTable"] = None,
    ):
        """
        Initializes ConfigGroupTable and fetches config group data.
        Optionally takes SDWANProfileTable and SDRoutingProfileTable instances to save all data together.
        """

        self.manager = manager
        self.sdwan_profiles_table = sdwan_profiles_table
        self.sdrouting_profiles_table = sdrouting_profiles_table
        self.config_groups_objects = []

        # API endpoint for config group summary
        api_path = "/v1/config-group/"
        try:
            # Fetch summary data first
            summary_data = self.manager._api_get(api_path)
            save_json(
                summary_data, "config_groups_table", "output/payloads/config_groups/"
            )  # save payload response

        except requests.exceptions.RequestException as e:
            print(
                f"An unexpected error occurred during config group summary fetch: {e}"
            )
            if hasattr(e, "response") and e.response is not None:
                print(f"Status: {e.response.status_code}, Response: {e.response.text}")
            return

        print("\n--- Collecting Config Groups and Associated Data ---")
        # Iterate through the raw data and create ConfigGroup objects
        for group_dict in summary_data:  # Iterate through the summary data
            config_group_id = group_dict.get("id")
            config_group_name = group_dict.get("name", "Unknown Config Group")
            number_of_devices = group_dict.get("numberOfDevices", 0)
            detailed_devices_list_raw = []  # Will store raw device dictionaries
            device_variables_raw = []  # Will store raw device variables (extracted from API response)

            # If there are devices associated, fetch their details from the specific API
            if number_of_devices > 0 and config_group_id:
                # Corrected API endpoint for associated devices
                device_api_path = f"/v1/config-group/{config_group_id}/device/associate"
                print(
                    f"  Fetching {number_of_devices} devices for Config Group '{config_group_name}' (ID: {config_group_id})"
                )
                try:
                    # The API returns a dictionary with a 'devices' key
                    response_data = self.manager._api_get(device_api_path)
                    detailed_devices_list_raw = response_data.get("devices", [])
                    save_json(
                        detailed_devices_list_raw,
                        f"{config_group_name}_associated_devices",
                        "output/payloads/config_groups/associated/",
                    )

                except requests.exceptions.RequestException as e:
                    print(
                        f"Error fetching devices for Config Group '{config_group_name}' (ID: {config_group_id}): {e}"
                    )
                    if hasattr(e, "response") and e.response is not None:
                        print(
                            f"Status: {e.response.status_code}, Response: {e.response.text}"
                        )
                    # Keep detailed_devices_list_raw as empty if there's an error

                # Fetch device variables for this config group
                variables_api_path = (
                    f"/v1/config-group/{config_group_id}/device/variables"
                )
                print(
                    f"  Fetching device variables for Config Group '{config_group_name}' (ID: {config_group_id})"
                )
                try:
                    # This API returns a dictionary with a 'devices' key, containing the list of device variables
                    full_variables_response = self.manager._api_get(variables_api_path)
                    # Save the full response for debugging/inspection
                    save_json(
                        full_variables_response,
                        f"{config_group_name}_device_variables_full_payload",
                        "output/payloads/config_groups/values/",
                    )

                    # Extract the actual list of device variables from the 'devices' key
                    device_variables_raw = full_variables_response.get("devices", [])

                except requests.exceptions.RequestException as e:
                    print(
                        f"Error fetching device variables for Config Group '{config_group_name}' (ID: {config_group_id}): {e}"
                    )
                    if hasattr(e, "response") and e.response is not None:
                        print(
                            f"Status: {e.response.status_code}, Response: {e.response.text}"
                        )
                    device_variables_raw = []  # Keep empty on error

            # Create the ConfigGroup object, passing profile, device, and device variable dictionaries
            config_group = ConfigGroup(
                id=config_group_id,
                name=config_group_name,
                description=group_dict.get("description"),
                source=group_dict.get("source"),
                solution=group_dict.get("solution"),
                lastUpdatedBy=group_dict.get("lastUpdatedBy"),
                lastUpdatedOn=group_dict.get("lastUpdatedOn"),
                createdBy=group_dict.get("createdBy"),
                createdOn=group_dict.get("createdOn"),
                profiles_data=group_dict.get("profiles"),  # Pass the profiles dict
                version=group_dict.get("version"),
                state=group_dict.get("state"),
                devices_data=detailed_devices_list_raw,  # Pass the device dictionaries
                numberOfDevices=number_of_devices,
                numberOfDevicesUpToDate=group_dict.get("numberOfDevicesUpToDate"),
                origin=group_dict.get("origin"),
                copyInfo=group_dict.get("copyInfo"),
                originInfo=group_dict.get("originInfo"),
                topology=group_dict.get("topology"),
                fullConfigCli=group_dict.get("fullConfigCli"),
                iosConfigCli=group_dict.get("iosConfigCli"),
                versionIncrementReason=group_dict.get("versionIncrementReason"),
                device_variables_data=device_variables_raw,  # Pass the extracted device variables list
            )
            self.config_groups_objects.append(config_group)

    def display(self):
        print("\n--- Displaying ConfigGroup Objects ---")
        for cg_obj in self.config_groups_objects:
            cg_obj.display()

    def save_groups(self, directory="output/config_groups"):
        print("\n---  Saving ConfigGroup Objects and Associated Data ---")
        # Save each config group and its associated devices
        for cg_obj in self.config_groups_objects:
            cg_obj.save_to_file(directory)

        # Now, also save the feature profiles if the instances were provided
        if self.sdwan_profiles_table:
            print("\n--- Saving SD-WAN Feature Profiles ---")
            self.sdwan_profiles_table.save_profiles()
        if self.sdrouting_profiles_table:
            print("\n--- Saving SD-Routing Feature Profiles ---")
            self.sdrouting_profiles_table.save_profiles()

        # NEW: Call the method to save device variables separately
        self.save_device_variables(os.path.join(directory, "values"))

        print(
            "\nAll Config Groups, Associated Devices, and Feature Profiles saved successfully!"
        )

    def save_device_variables(self, directory="output/config_groups/values"):
        """
        Saves the deployment values (device variables) for each config group
        into separate JSON files.
        """
        print(f"\n--- Saving Device Variables to {directory} ---")
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        for cg_obj in self.config_groups_objects:
            variables_to_save = cg_obj.get_device_variables_for_saving()
            if variables_to_save:
                # Sanitize the config group name for the filename
                sanitized_name = "".join(
                    c for c in cg_obj.name if c.isalnum() or c in (" ", ".", "_", "-")
                ).strip()
                sanitized_name = sanitized_name.replace(" ", "_")

                if not sanitized_name:
                    filename = f"variables_config_group_{cg_obj.id}.json"
                else:
                    filename = f"{sanitized_name}_variables.json"

                filepath = os.path.join(directory, filename)

                try:
                    with open(filepath, "w") as f:
                        json.dump(variables_to_save, f, indent=4)
                    print(
                        f"Successfully saved variables for ConfigGroup '{cg_obj.name}' to '{filepath}'"
                    )
                except Exception as e:
                    print(
                        f"Error saving variables for ConfigGroup '{cg_obj.name}' to '{filepath}': {e}"
                    )
            else:
                print(f"No variables found for ConfigGroup '{cg_obj.name}'.")

    def access_data(self):
        print("\n--- Example: Accessing data from the second ConfigGroup object ---")
        if self.config_groups_objects:
            first_config_group = self.config_groups_objects[1]
            print(f"First Config Group Name: {first_config_group.name}")
            print(f"First Config Group ID: {first_config_group.id}")
            if first_config_group.profiles:
                print(f"Profiles in '{first_config_group.name}':")
                for profile in first_config_group.profiles:
                    print(
                        f"  - Profile Name: {profile.name}, Type: {profile.type}, ID: {profile.id}"
                    )
            else:
                print("No profiles found for the first config group.")

            if first_config_group.devices:
                print(f"Associated Devices for '{first_config_group.name}':")
                for device in first_config_group.devices:
                    print(
                        f"  - Device Hostname: {device.host_name}, IP: {device.device_ip}, Model: {device.device_model}"
                    )
                    if device.variables:
                        print(f"    Variables for {device.host_name}:")
                        for var in device.variables:
                            print(
                                f"      - {var.get('name')}: {var.get('value', 'N/A')}"
                            )  # Use .get() with default for safety
            else:
                print("No devices associated with the first config group.")
