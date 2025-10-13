#! /usr/bin/env python3
# =========================================================================
# Cisco Catalyst SD-WAN Manager APIs
# =========================================================================
#
# Authentication and common API methods
#
# Description:
#   Session-based authentication for Cisco SD-WAN Manager
#   Log in with a username and password to establish a session.
#   Get a cross-site request forgery prevention token, necessary for most POST operations
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
    Handles session-based authentication for SD-WAN Manager and provides common API methods.
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
        self.base_url = f"https://{self.host}:{self.port}"  # Base URL for login/token
        self.session = requests.Session()
        self.session.verify = validate_certs
        self.jsessionid = None
        self.token = None
        self.dataservice_base_url = None  # Base URL for API calls (e.g., /dataservice)
        self.version = None  # Will be populated by about() method
        self.applicationVersion = None  # Will be populated by about() method
        self.applicationServer = None  # Will be populated by about() method
        self.time = None  # Will be populated by about() method
        self.timeZone = None  # Will be populated by about() method
        self.status = False  # Indicates if authentication was successful

        # Perform authentication during initialization
        self._authenticate()
        if self.dataservice_base_url:  # Check if authentication was successful
            self.status = True
            print("Authentication successful.")
            logger.info("Successfully authenticated with SD-WAN Manager.")
            logger.info(f"Session headers: {self.session.headers}")
            logger.info(f"Base URL: {self.dataservice_base_url}")

        else:
            print("Authentication failed. Please check sdwan_api.log for details.")
            logger.error("Failed to authenticate with SD-WAN Manager. Exiting.")
            sys.exit(1)  # Exit if authentication fails

        self.about()  # Populate version and other info

    def _login(self):
        """
        Performs the initial login to get the JSESSIONID.
        The requests.Session object will automatically manage the cookies.
        """
        api = "/j_security_check"
        url = self.base_url + api
        payload = {"j_username": self.user, "j_password": self.password}

        response = None
        try:
            response = self.session.post(url=url, data=payload, timeout=self.timeout)
            response.raise_for_status()

            cookies = response.headers.get("Set-Cookie")
            if not cookies:
                raise ValueError("No 'Set-Cookie' header found in login response.")
            self.jsessionid = cookies.split(";")[0]
            return self.jsessionid

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Login failed: {e}. Response: {response.text if response is not None else 'No response'}\n"
            )
            return None  # Indicate failure
        except ValueError as e:
            logger.error(f"Login failed: {e}\n")
            return None  # Indicate failure

    def _get_token(self):
        """
        Retrieves the X-XSRF-TOKEN.
        """
        if not self.jsessionid:
            logger.warning("JSESSIONID not set, attempting login before getting token.")
            if not self._login():  # Try to login if jsessionid is missing
                return None

        api = "/dataservice/client/token"
        url = self.base_url + api

        response = None
        try:
            response = self.session.get(url=url, timeout=self.timeout)
            response.raise_for_status()
            self.token = response.text
            return self.token

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Failed to get X-XSRF-TOKEN: {e}. Status: {response.status_code if response is not None else 'N/A'}, Response: {response.text if response is not None else 'No response'}\n"
            )
            return None

    def _authenticate(self):
        """
        Performs login and token retrieval, then configures the session with default headers.
        Sets self.dataservice_base_url and updates self.session headers.
        """
        self.jsessionid = self._login()
        if not self.jsessionid:
            return  # Authentication failed at login

        self.token = self._get_token()
        # If token retrieval fails, a warning is logged, but we proceed as some APIs might not require it.
        # The session headers are updated regardless.

        self.session.headers.update(
            {
                "Content-Type": "application/json",
            }
        )
        if self.token:
            self.session.headers.update({"X-XSRF-TOKEN": self.token})

        self.dataservice_base_url = f"https://{self.host}:{self.port}/dataservice"

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
            print(f"An unexpected error occurred: {e}")
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
        response = self.session.get(url=url, params=params)
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
        response = self.session.post(url=url, json=payload)
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
        response = self.session.put(url=url, json=payload)
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

    def logout(self):
        """
        Logs out of the SD-WAN Manager session.
        """

        if not self.status:
            raise requests.exceptions.RequestException(
                "Manager not authenticated. Cannot make API call."
            )

        api = "/logout"
        url = self.base_url + api
        # url = cast(str, self.dataservice_base_url) + path
        logger.info(f"Logout: {url}")
        response = self.session.post(url=url)
        response.raise_for_status()
        logger.info("Successfully logged out of SD-WAN Manager.")


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
