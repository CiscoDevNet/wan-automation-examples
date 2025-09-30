#! /usr/bin/env python

# JWT-based Authentication for Cisco SD-WAN Manager
# Introduced in 20.18
#
# This script introduces an AuthenticationJWT class that follows the JWT authentication flow:
#
# Obtain JSESSIONID by authenticating with username/password.
# Use the JSESSIONID to request a JWT token from the /api/v1/user/login endpoint.
# Subsequent API calls will use the JWT token in the X-Auth-Token header.
#
# More information [here](https://developer.cisco.com/docs/sdwan/authentication/#jwt-based-authentication)

#! /usr/bin/env python

import logging
import os
import sys

import requests
import urllib3

logger = logging.getLogger(__name__)

# Disable insecure request warnings globally
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ----------------------------------------------------------
class Authentication:
    """
    Handles jwt-based authentication for SD-WAN Manager.
    """

    def __init__(self, host, port, user, password, validate_certs=False, timeout=10):
        """Initialize Authentication object with session parameters.
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
        self.base_url = f"https://{self.host}:{self.port}"
        self.session = requests.Session()
        self.session.verify = validate_certs  # Set session-wide verification
        self.jsessionid = None
        self.token = None
        self.header = None
        self.dataservice_base_url = None

    def login(self):
        """
        Performs the initial login to get the JSESSIONID.
        """

        api = "/j_security_check"
        url = self.base_url + api
        payload = {"j_username": self.user, "j_password": self.password}

        response = None
        try:
            response = self.session.post(url=url, data=payload, timeout=self.timeout)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

            cookies = response.headers.get("Set-Cookie")
            if not cookies:
                raise ValueError("No 'Set-Cookie' header found in login response.")

            jsessionid_full = cookies.split(";")
            self.jsessionid = jsessionid_full[0]
            return self.jsessionid

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Login failed: {e}. Response: {response.text if response is not None else 'No response'}\n"
            )
            sys.exit(1)

        except ValueError as e:
            logger.error(f"Login failed: {e}\n")
            sys.exit(1)

    def get_token(self):
        """
        Retrieves the X-XSRF-TOKEN.
        """

        if not self.jsessionid:
            logger.warning("JSESSIONID not set, attempting login before getting token.")
            self.login()  # Ensure jsessionid is present

        headers = {
            "Cookie": self.jsessionid
        }  # This cookie is also managed by self.session
        api = "/dataservice/client/token"
        url = self.base_url + api

        response = None

        try:
            response = self.session.get(url=url, headers=headers, timeout=self.timeout)
            response.raise_for_status()  # Raise an exception for HTTP errors
            self.token = response.text
            return self.token

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Failed to get X-XSRF-TOKEN: {e}. Status: {response.status_code if response is not None else 'N/A'}, Response: {response.text if response is not None else 'No response'}\n"
            )
            return None

    def establish_session(self):
        """
        Performs login and token retrieval, then constructs header and base_url.
        """

        self.jsessionid = self.login()
        self.token = self.get_token()

        if self.token:
            self.header = {
                "Content-Type": "application/json",
                "Cookie": self.jsessionid,
                "X-XSRF-TOKEN": self.token,
            }
        else:
            # Fallback if token is not obtained, though it might indicate an issue
            self.header = {
                "Content-Type": "application/json",
                "Cookie": self.jsessionid,
            }
            logger.warning(
                "X-XSRF-TOKEN was not obtained. API calls might fail if it's required."
            )

        self.dataservice_base_url = f"https://{self.host}:{self.port}/dataservice"
        return self.dataservice_base_url, self.header


# ----------------------------------------------------------
class AuthenticationJWT:
    """
    Handles JWT-based authentication for vManage by directly POSTing to /jwt/login.
    """

    def __init__(
        self,
        host,
        port,
        user,
        password,
        validate_certs=False,
        timeout=10,
        token_duration=None,
    ):
        """Initialize AuthenticationJWT object with session parameters.
        Args:
            host (str): hostname or IP address of vManage
            user (str): username for authentication
            password (str): password for authentication
            port (int): default HTTPS port 443
            validate_certs (bool): turn certificate validation on or off.
            timeout (int): how long Requests will wait for a response from the server, default 10 seconds
            token_duration (int, optional): Desired duration for the JWT token in seconds.
                                            Defaults to vManage's default (1800s).
        """

        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.token_duration = token_duration
        self.base_url = f"https://{self.host}:{self.port}"
        self.session = requests.Session()
        self.session.verify = validate_certs  # Set session-wide verification
        self.jwt_token = None
        self.csrf_token = None
        self.header = None
        self.dataservice_base_url = None

    def login_jwt(self):
        """
        Performs the JWT login by POSTing credentials to /jwt/login.
        Retrieves the JWT token and CSRF token from the response.
        """
        api = "/jwt/login"
        url = self.base_url + api

        payload = {"username": self.user, "password": self.password}
        if self.token_duration is not None:
            payload["duration"] = self.token_duration

        headers = {"Content-Type": "application/json"}

        response = None
        try:
            response = self.session.post(
                url=url, headers=headers, json=payload, timeout=self.timeout
            )
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)

            response_json = response.json()
            self.jwt_token = response_json.get("token")
            self.csrf_token = response_json.get("csrf")

            if not self.jwt_token:
                raise ValueError("JWT 'token' not found in login response.")
            # CSRF token might be optional for some GET calls, but good practice to get it.
            if not self.csrf_token:
                logger.warning(
                    "JWT 'csrf' token not found in login response. POST/PUT/DELETE requests might fail."
                )

            logger.info("JWT token and CSRF token obtained successfully.")
            return self.jwt_token, self.csrf_token

        except requests.exceptions.RequestException as e:
            logger.error(
                f"JWT login failed: {e}. Status: {response.status_code if response is not None else 'N/A'}, Response: {response.text if response is not None else 'No response'}\n"
            )
            sys.exit(1)
        except ValueError as e:
            logger.error(f"JWT login failed: {e}\n")
            sys.exit(1)
        except Exception as e:
            logger.error(f"An unexpected error occurred during JWT login: {e}\n")
            sys.exit(1)

    def establish_session_jwt(self):
        """
        Performs JWT login and constructs the header and base_url for subsequent API calls.
        """
        self.jwt_token, self.csrf_token = self.login_jwt()

        if self.jwt_token:
            self.header = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.jwt_token}",
            }
            if self.csrf_token:  # Include CSRF token if it was successfully obtained
                self.header["X-XSRF-TOKEN"] = self.csrf_token
            logger.info("JWT session header created.")
        else:
            logger.error("JWT token was not obtained. Cannot establish session.")
            sys.exit(1)

        self.dataservice_base_url = f"https://{self.host}:{self.port}/dataservice"
        return self.dataservice_base_url, self.header


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

    return manager_host, manager_port, manager_username, manager_password


# ----------------------------------------------------------
def get_authenticated_session_details():
    """
    Orchestrates the retrieval of credentials, authentication (session-based),
    and returns the base URL and header for API calls.
    """
    host, port, user, password = get_manager_credentials_from_env()
    auth_manager = Authentication(host, port, user, password)
    base_url, header = auth_manager.establish_session()
    return base_url, header


# ----------------------------------------------------------
def get_authenticated_session_details_jwt(token_duration=None):
    """
    Orchestrates the retrieval of credentials, authentication (JWT-based),
    and returns the base URL and header for API calls.
    Args:
        token_duration (int, optional): Desired duration for the JWT token in seconds.
                                        Defaults to vManage's default (1800s).
    """
    host, port, user, password = get_manager_credentials_from_env()
    auth_manager_jwt = AuthenticationJWT(
        host, port, user, password, token_duration=token_duration
    )
    base_url, header = auth_manager_jwt.establish_session_jwt()
    return base_url, header


# Example usage (uncomment to test):
if __name__ == "__main__":
    # Configure logging for better visibility
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    print("Attempting JWT-based authentication...")
    try:
        # You can specify a token_duration here, e.g., 3600 for 1 hour
        jwt_base_url, jwt_header = get_authenticated_session_details_jwt(
            token_duration=3600
        )
        print(f"\nJWT Authentication Successful!")
        print(f"Base URL: {jwt_base_url}")
        print(f"Header for API calls: {jwt_header}")
        # You can now use jwt_base_url and jwt_header to make API calls
        # For example:
        # response = requests.get(f"{jwt_base_url}/device", headers=jwt_header, verify=False)
        # print(response.json())
    except SystemExit:
        print(
            "\nJWT Authentication failed. Please check environment variables and vManage connectivity/credentials."
        )
    except Exception as e:
        print(f"\nAn unexpected error occurred during JWT authentication: {e}")

    print(
        "\nAttempting Session-based authentication (original method) for comparison..."
    )
    try:
        session_base_url, session_header = get_authenticated_session_details()
        print(f"\nSession-based Authentication Successful!")
        print(f"Base URL: {session_base_url}")
        print(f"Header for API calls: {session_header}")
    except SystemExit:
        print(
            "\nSession-based Authentication failed. Please check environment variables and vManage connectivity/credentials."
        )
    except Exception as e:
        print(
            f"\nAn unexpected error occurred during Session-based authentication: {e}"
        )
