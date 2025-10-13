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

import logging

# Import the new unified Manager class and the credentials function
from config_groups import ConfigGroupTable, SDRoutingProfileTable, SDWANProfileTable

# Import the new unified Manager class and the credentials function
from manager import Manager, get_manager_credentials_from_env
from prompt import Prompt  # Ensure this import is present


# -----------------------------------------------------------------------------
def help():
    print("Define vManage parameters in .env file")
    exit(1)


# -----------------------------------------------------------------------------
def list_groups():
    config_group_table.display()


# -----------------------------------------------------------------------------
def save_groups():
    # This function now simply calls the ConfigGroupTable's save_groups,
    # which internally handles saving profiles as well.
    config_group_table.save_groups()


# -----------------------------------------------------------------------------
def access_groups():
    config_group_table.access_data()


# -----------------------------------------------------------------------------
def list_sdwan_profiles():
    sdwan_profiles_table.list()


# -----------------------------------------------------------------------------
def list_sdrouting_profiles():
    sdrouting_profiles_table.list()


# -----------------------------------------------------------------------------
def list_sdwan_profile_categories():
    sdwan_profiles_table.list_categories()


# -----------------------------------------------------------------------------
def list_sdrouting_profile_categories():
    sdrouting_profiles_table.list_categories()


# -----------------------------------------------------------------------------
def quit():
    print("Quitting ...")
    # manager.close()
    raise SystemExit  # This will now be caught by the main loop's try-except


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    log_file_path = "sdwan_api.log"  # You can make this more dynamic if needed

    logging.basicConfig(
        filename=log_file_path,  # <--- Add this line to specify the log file
        filemode="a",  # <--- Optional: 'a' for append (default), 'w' for overwrite
        format="%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d [%(filename)s])",
        datefmt="%d/%m/%Y %I:%M:%S %p",
        level=logging.INFO,
    )

    print("\n--- Authenticating to SD-WAN Manager ---")
    host, port, user, password = get_manager_credentials_from_env()
    manager = Manager(host, port, user, password)

    # Collecting Config Groups and Feature Profiles from SD-WAN Manager
    sdwan_profiles_table = SDWANProfileTable(manager)
    sdrouting_profiles_table = SDRoutingProfileTable(manager)
    config_group_table = ConfigGroupTable(
        manager, sdwan_profiles_table, sdrouting_profiles_table
    )

    # Menu
    options = {
        "List Configuration Groups": list_groups,
        "List SD-WAN Feature Profiles": list_sdwan_profiles,
        "List SD-Routing Feature Profiles": list_sdrouting_profiles,
        "List SD-WAN Feature Profiles per category": list_sdwan_profile_categories,
        "List SD-Routing Feature Profiles per category": list_sdrouting_profile_categories,
        "Save Configuration Groups to files (and all Feature Profiles)": save_groups,
        "Example: Accessing data from the first ConfigGroup object": access_groups,
        "Quit": quit,
    }

    while True:
        print("")  # Print a blank line before displaying the menu for better separation
        selected_option_name, selected_function = Prompt.dict_menu(
            options
        )  # Get the chosen function and its name

        # Add clear separators and the chosen option name
        print(f"\n{'=' * 80}")
        print(f"--- Executing: {selected_option_name} ---".center(80))
        print(f"{'=' * 80}\n")

        try:
            selected_function()  # Execute the chosen function
        except SystemExit:  # Catch SystemExit (e.g., from 'quit' option)
            break  # Exit the main loop gracefully
        except Exception as e:
            # Print a distinct error separator if an unexpected error occurs during execution
            print(f"\n{'!' * 80}")
            print(
                f"!!! An error occurred during '{selected_option_name}' execution: {e} !!!".center(
                    80
                )
            )
            print(f"{'!' * 80}\n")
            # The loop will continue, re-displaying the menu after the error

        # Print a clear separator after the function finishes
        print(f"\n{'=' * 80}")
        print(f"--- Finished: {selected_option_name} ---".center(80))
        print(f"{'=' * 80}\n")
        # The loop will continue, re-displaying the menu for the next choice
