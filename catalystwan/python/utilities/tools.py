#! /usr/bin/env python3
# =========================================================================
# Cisco Catalyst SD-WAN Manager APIs
# =========================================================================
#
# Save JSON payloads to files
#
# =========================================================================

import json
import os
from datetime import datetime


# -----------------------------------------------------------------------------
def save_payload(payload: dict, filename: str = "payload", directory: str = "./output/payloads/"):
    """Save Manager API json response payload to a file

    Args:
        payload: JSON response payload
        filename: filename for saved files (default: "payload")
        directory: directory to save the file (default: "./output/payloads/")
    """

    filename = "".join([directory, f"{filename}.json"])

    if not os.path.exists(directory):
        print(f"Creating folder {directory}")
        os.makedirs(directory)  # Create the directory if it doesn't exist

    # Dump entire payload to file
    with open(filename, "w") as file:
        json.dump(payload, file, indent=4)


# -----------------------------------------------------------------------------
def convert_timestamp(timestamp_ms):
    """
    Helper function to convert Unix timestamp to human-readable date
    """
    if timestamp_ms:
        return datetime.fromtimestamp(timestamp_ms / 1000).strftime("%Y-%m-%d %H:%M:%S UTC")
    return "N/A"
