#! /usr/bin/env python3
# =======================================================================================
# Cisco Catalyst SD-WAN Manager APIs
# =======================================================================================
#
# Authentication and common API methods
#
# Description:
#   JWT-based authentication for Cisco SD-WAN Manager
#   Log in with a username and password to obtain a JWT token.
#   The JWT token is then used in the Authorization header for subsequent API calls.
#
# =======================================================================================

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
class ManagerJWT:
    """
    Handles JWT-based authentication for SD-WAN Manager and provides common API methods.
    """

    def __init__(self, host, port, user, password, validate_certs=False, timeout=10):
        """
        Initialize Manager object with session parameters and perform authentication.
        Args:
            host (str): hostname or IP address of SD-WAN Manager
            user (str): username for authentication
            password (str): password for authentication
            port (int): default HTTPS port 443
            validate_certs (bool): turn certificate validation on or off.
            timeout (int): how long Requests will wait for a response from the server, default 10 seconds
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.base_url = (
            f"https://{self.host}:{self.port}"  # Base URL for authentication
        )
        self.session = requests.Session()
        self.session.verify = validate_certs
        self.jwt_token = None  # Will store the JWT token
        self.dataservice_base_url = None  # Base URL for API calls (e.g., /dataservice)
        self.version = None  # Will be populated by about() method
        self.applicationVersion = None  # Will be populated by about() method
        self.applicationServer = None  # Will be populated by about() method
        self.time = None  # Will be populated by about() method
        self.timeZone = None  # Will be populated by about() method
        self.status = False  # Indicates if authentication was successful

        # Perform authentication during initialization
        self._authenticate()
        if self.status:  # Check if authentication was successful
            logger.info("Successfully authenticated with SD-WAN Manager using JWT.")
            logger.info(f"Base URL: {self.dataservice_base_url}")
        else:
            logger.error("Failed to authenticate with SD-WAN Manager. Exiting.")
            sys.exit(1)  # Exit if authentication fails

        self.about()  # Populate version and other info

    def _authenticate(self):
        """
        Performs JWT token retrieval and configures the session with the Authorization header.
        Sets self.dataservice_base_url and updates self.session headers.
        """
        # Endpoint for JWT token retrieval (as per Cisco SD-WAN documentation)
        # with username/password in body
        api_path = "/jwt/login"
        url = self.base_url + api_path
        payload = {
            "username": self.user,
            "password": self.password,
            "duration": 3600,  # Token validity duration in seconds
        }

        response = None
        try:
            # For JWT, the content type for sending credentials is often JSON
            response = self.session.post(url=url, json=payload, timeout=self.timeout)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            response_data = response.json()
            self.jwt_token = response_data.get("token")  # Extract the JWT token

            if not self.jwt_token:
                raise ValueError("JWT token not found in the response.")

            # Set the Authorization header for all subsequent requests
            self.session.headers.update(
                {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.jwt_token}",
                }
            )
            self.dataservice_base_url = f"https://{self.host}:{self.port}/dataservice"
            self.status = True  # Mark authentication as successful

        except requests.exceptions.RequestException as e:
            logger.error(
                f"JWT authentication failed: {e}. "
                f"Status: {response.status_code if response is not None else 'N/A'}, "
                f"Response: {response.text if response is not None else 'No response'}\n"
            )
            self.status = False
        except ValueError as e:
            logger.error(f"JWT authentication failed: {e}\n")
            self.status = False
        except json.JSONDecodeError:
            logger.error(
                f"JWT authentication failed: Failed to decode JSON response. Response: {response.text if response is not None else 'No response'}\n"
            )
            self.status = False

    def about(self):
        """
        Fetches and returns key information about the SD-WAN Manager application.

        Returns:
            Optional[Dict[str, Any]]: A dictionary containing 'version',
            'applicationVersion', 'applicationServer', 'time', and 'timeZone'
            if successful, otherwise None.
        """
        api_path = "/client/about"

        try:
            # _api_get will automatically use the JWT token in the session headers
            full_payload = self._api_get(api_path)

            # The actual data is nested under the "data" key in the payload
            data = full_payload.get("data")

            self.version = data.get("version")
            self.applicationVersion = data.get("applicationVersion")
            self.applicationServer = data.get("applicationServer")
            self.time = data.get("time")
            self.timeZone = data.get("timeZone")

            # Print the information
            print("\nSD-WAN Manager Information:")
            print(f" Version: {self.version}")
            print(f" Application Version: {self.applicationVersion}")
            print(f" Application Server: {self.applicationServer}")
            print(f" Time: {self.time}")
            print(f" Time Zone: {self.timeZone}")
            print()

        except requests.exceptions.RequestException as e:
            print(
                f"An unexpected error occurred while fetching 'about' information: {e}"
            )
            if hasattr(e, "response") and e.response is not None:
                print(f"Status: {e.response.status_code}, Response: {e.response.text}")
            return

    def _api_get(self, path: str, params: Optional[dict] = None):
        """
        Helper method to make a GET request to the SD-WAN Manager API.
        Handles URL construction, uses the authenticated session, and checks for HTTP errors.

        Args:
            path (str): The API endpoint path (e.g., "/v1/config-group/").
            params (dict, optional): Dictionary of query parameters. Defaults to None.

        Returns:
            dict: The JSON response from the API.

        Raises:
            requests.exceptions.RequestException: If the API call fails or manager is not authenticated.
        """
        if not self.status:
            raise requests.exceptions.RequestException(
                "Manager not authenticated. Cannot make API call."
            )

        url = cast(str, self.dataservice_base_url) + path
        logger.info(f"Making GET request to: {url} with params: {params}")
        response = self.session.get(url=url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def _api_post(self, path: str, payload: Optional[dict] = None):
        """
        Helper method to make a POST request to the SD-WAN Manager API.
        Handles URL construction, uses the authenticated session, and checks for HTTP errors.

        Args:
            path (str): The API endpoint path (e.g., "/v1/config-group/").
            payload (dict, optional): Dictionary to send in the body of the POST request. Defaults to None.

        Returns:
            dict: The JSON response from the API.

        Raises:
            requests.exceptions.RequestException: If the API call fails or manager is not authenticated.
        """
        if not self.status:
            raise requests.exceptions.RequestException(
                "Manager not authenticated. Cannot make API call."
            )

        url = cast(str, self.dataservice_base_url) + path
        logger.info(f"Making POST request to: {url} with payload: {payload}")
        response = self.session.post(url=url, json=payload, timeout=self.timeout)
        response.raise_for_status()

        return response.json()

    def _api_put(self, path: str, payload: Optional[dict] = None):
        """
        Helper method to make a PUT request to the SD-WAN Manager API.
        Handles URL construction, uses the authenticated session, and checks for HTTP errors.

        Args:
            path (str): The API endpoint path.
            payload (dict, optional): Dictionary to send in the body of the PUT request. Defaults to None.

        Returns:
            dict: The JSON response from the API.

        Raises:
            requests.exceptions.RequestException: If the API call fails or manager is not authenticated.
        """
        if not self.status:
            raise requests.exceptions.RequestException(
                "Manager not authenticated. Cannot make API call."
            )

        url = cast(str, self.dataservice_base_url) + path
        logger.info(f"Making PUT request to: {url} with payload: {payload}")
        response = self.session.put(url=url, json=payload, timeout=self.timeout)
        response.raise_for_status()

        return response.json()

    def _api_delete(self, path: str, params: Optional[dict] = None):
        """
        Helper method to make a DELETE request to the SD-WAN Manager API.
        Handles URL construction, uses the authenticated session, and checks for HTTP errors.

        Args:
            path (str): The API endpoint path.
            params (dict, optional): Dictionary of query parameters. Defaults to None.

        Returns:
            dict: The JSON response from the API (often empty or a confirmation message).

        Raises:
            requests.exceptions.RequestException: If the API call fails or manager is not authenticated.
        """
        if not self.status:
            raise requests.exceptions.RequestException(
                "Manager not authenticated. Cannot make API call."
            )

        url = cast(str, self.dataservice_base_url) + path
        response = self.session.delete(url=url, params=params, timeout=self.timeout)
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
def get_manager_credentials_from_env():
    """
    Retrieves manager credentials from environment variables.
    Exits if any required variable is missing.
    """

    manager_host = os.environ.get("manager_host")
    manager_port = os.environ.get("manager_port")
    manager_username = os.environ.get("manager_username")
    manager_password = os.environ.get("manager_password")

    # Check for None values first
    if not all([manager_host, manager_port, manager_username, manager_password]):
        print(
            "Manager details must be set via environment variables using below commands:\n"
            "For Windows Workstation:\n"
            "  set manager_host=198.18.1.10\n"
            "  set manager_port=8443\n"
            "  set manager_username=admin\n"
            "  set manager_password=admin\n"
            "For MAC OSX / Linux Workstation:\n"
            "  export manager_host=198.18.1.10\n"
            "  export manager_port=8443\n"
            "  export manager_username=admin\n"
            "  export manager_password=admin"
        )
        sys.exit(1)

    return (
        manager_host,
        int(manager_port),
        manager_username,
        manager_password,
    )
