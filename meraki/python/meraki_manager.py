#! /usr/bin/env python3
# =========================================================================
# Cisco Meraki Dashboard APIs
# Revision 1.0 - 10/17/2025
# =========================================================================
#
# API key retrieval and common API methods
#
# Description:
#   API key-based authentication to the Cisco Dashboard
#   Retrieve API key configured as the environmental variable
#   MERAKI_API_KEY from the device running this program.
#   Use the API key for subsequent GET, POST, PUT, and DELETE
#   operations.
#
# =========================================================================

import json
import logging
import os
import sys
from typing import Optional, cast

import requests
import urllib3

logger = logging.getLogger(__name__)

# Disable insecure request warnings globally
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ----------------------------------------------------------
class Manager:
    """
    Handles API key retrieval for Cisco Meraki Dashboard and provides 
    common API methods.
    """

    def __init__(self, validate_certs=False, timeout=10):
        """
        Initialize Manager object with session parameters and retrieve API key.
        Args:
            validate_certs (bool): turn certificate validation on or off.
            timeout (int): how long Requests will wait for a response from the
            server, default 10 seconds
        """
        self.api_key = get_api_key_from_env()
        self.dataservice_base_url = "https://api.meraki.com/api/v1"   
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json", 
                "Authorization": "Bearer " + self.api_key
            }
        )
        self.session.verify = validate_certs
        self.timeout = timeout

    def _api_get(self, path: str, params: Optional[dict] = None):
        """
        Helper method to make a GET request to the Meraki Dashboard API.
        Handles URL construction, uses the session, and checks for HTTP errors.

        Args:
            path (str): The API endpoint path (e.g., "/organizations").
            params (dict, optional): Dictionary of query parameters. Defaults to None.

        Returns:
            dict: The JSON response from the API.

        Raises:
            requests.exceptions.RequestException: If the API call fails or API key
            is not valid.
        """

        url = cast(str, self.dataservice_base_url) + path
        logger.info(f"Making GET request to: {url} with params: {params}")
        response = self.session.get(url=url, params=params)
        response.raise_for_status()
        return response.json()

    def _api_post(self, path: str, payload: Optional[dict] = None):
        """
        Helper method to make a POST request to the Meraki Dashboard API.
        Handles URL construction, uses the session, and checks for HTTP errors.

        Args:
            path (str): The API endpoint path (e.g., "/organizations").
            payload (dict, optional): Dictionary to send in the body of the POST request. Defaults to None.

        Returns:
            dict: The JSON response from the API.

        Raises:
            requests.exceptions.RequestException: If the API call fails or API key
            is not valid.
        """

        url = cast(str, self.dataservice_base_url) + path
        logger.info(f"Making POST request to: {url} with payload: {payload}")
        response = self.session.post(url=url, json=payload)
        response.raise_for_status()

        return response.json()

    def _api_put(self, path: str, payload: Optional[dict] = None):
        """
        Helper method to make a PUT request to the Meraki Dashboard API.
        Handles URL construction, uses the session, and checks for HTTP errors.

        Args:
            path (str): The API endpoint path.
            payload (dict, optional): Dictionary to send in the body of the PUT request. Defaults to None.

        Returns:
            dict: The JSON response from the API.

        Raises:
            requests.exceptions.RequestException: If the API call fails or API key
            is not valid.
        """

        url = cast(str, self.dataservice_base_url) + path
        logger.info(f"Making PUT request to: {url} with payload: {payload}")
        response = self.session.put(url=url, json=payload)
        response.raise_for_status()

        return response.json()

    def _api_delete(self, path: str, params: Optional[dict] = None):
        """
        Helper method to make a DELETE request to the Meraki Dashboard API.
        Handles URL construction, uses the session, and checks for HTTP errors.

        Args:
            path (str): The API endpoint path.
            params (dict, optional): Dictionary of query parameters. Defaults to None.

        Returns:
            dict: The JSON response from the API (often empty or a confirmation message).

        Raises:
            requests.exceptions.RequestException: If the API call fails or API key
            is not valid.
        """

        url = cast(str, self.dataservice_base_url) + path
        response = self.session.delete(url=url, params=params)
        logger.info(f"Making DELETE request to: {url} with params: {params}")
        response.raise_for_status()

        # DELETE requests often return 204 No Content, so response.json() might fail.
        # Check if there's content before trying to parse JSON.
        if response.content:
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.warning(f"DELETE response content is not JSON: {response.text}")
                return {"message": "Operation successful, no JSON response content."}
        else:
            return {"message": "Operation successful, no content returned."}


# ----------------------------------------------------------
def get_api_key_from_env():
    """
    Retrieves Dashboard API key from the environment variable MERAKI_API_KEY. 
    Exits if the API key is missing.
    """

    api_key = os.environ.get("MERAKI_API_KEY")

    # Check for None values first
    if not api_key:
        print(
            "API key must be set via environment variable using below commands:\n"
            "For Windows Workstation:\n"
            "  set MERAKI_API_KEY=<your_api_key>\n"
            "For MAC OSX / Linux Workstation:\n"
            "  export MERAKI_API_KEY=<your_api_key>\n"
        )
        sys.exit(1)

    return (
        api_key
    )
