"""API-key client for Cisco Catalyst SD-WAN Manager."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Self

import requests


@dataclass(slots=True)
class ManagerAPIError(RuntimeError):
    """An HTTP or response error returned by SD-WAN Manager."""

    message: str
    method: str | None = None
    path: str | None = None
    status_code: int | None = None
    response_text: str | None = None

    def __str__(self) -> str:
        context = " ".join(part for part in (self.method, self.path) if part)
        status = f"HTTP {self.status_code}" if self.status_code else ""
        prefix = " ".join(part for part in (context, status) if part)
        detail = f": {self.response_text}" if self.response_text else ""
        return f"{prefix}: {self.message}{detail}" if prefix else f"{self.message}{detail}"


class ManagerClient:
    """Authenticated API-key client for the `/dataservice` API.

    The client obtains an XSRF token during construction and sends both the
    bearer API key and token on all subsequent requests. TLS verification is
    enabled unless `verify=False` is explicitly selected for a lab system.
    """

    def __init__(
        self,
        vmanage: str,
        api_key: str,
        *,
        port: int = 443,
        verify: bool | str = True,
        timeout: float = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        if not vmanage.strip():
            raise ValueError("vmanage must not be empty")
        if not api_key.strip():
            raise ValueError("api_key must not be empty")
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")

        host = vmanage.strip().removeprefix("https://").removeprefix("http://")
        self.base_url = f"https://{host.rstrip('/')}:{port}/dataservice"
        self.timeout = timeout
        self.session = session or requests.Session()
        self.session.verify = verify
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
        )
        self.refresh_xsrf_token()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()

    def refresh_xsrf_token(self) -> str:
        """Obtain and install the XSRF token associated with the API key."""
        response = self._send("GET", "/client/token", include_xsrf=False)
        token = response.text.strip()
        if not token or "<html" in token.lower():
            raise ManagerAPIError(
                "Manager returned an invalid XSRF token",
                method="GET",
                path="/client/token",
                status_code=response.status_code,
                response_text=token[:500],
            )
        self.session.headers["X-XSRF-TOKEN"] = token
        return token

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        payload: Any = None,
    ) -> Any:
        """Send an API request and decode its JSON response when present."""
        response = self._send(method, path, params=params, payload=payload)
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except requests.JSONDecodeError:
            content_type = response.headers.get("Content-Type", "")
            if "json" not in content_type.lower():
                return response.text
            raise ManagerAPIError(
                "Manager returned malformed JSON",
                method=method.upper(),
                path=path,
                status_code=response.status_code,
                response_text=response.text[:500],
            ) from None

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self.request("GET", path, params=params)

    def post(
        self,
        path: str,
        *,
        payload: Any = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        return self.request("POST", path, params=params, payload=payload)

    def put(self, path: str, *, payload: Any = None) -> Any:
        return self.request("PUT", path, payload=payload)

    def delete(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self.request("DELETE", path, params=params)

    def about(self) -> Any:
        return self.get("/client/about")

    def _send(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        payload: Any = None,
        include_xsrf: bool = True,
    ) -> requests.Response:
        normalized_path = path if path.startswith("/") else f"/{path}"
        headers = None if include_xsrf else {"X-XSRF-TOKEN": None}
        try:
            response = self.session.request(
                method.upper(),
                f"{self.base_url}{normalized_path}",
                params=params,
                json=payload,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response
        except requests.RequestException as error:
            response = getattr(error, "response", None)
            raise ManagerAPIError(
                "API request failed",
                method=method.upper(),
                path=normalized_path,
                status_code=response.status_code if response is not None else None,
                response_text=(response.text.strip()[:500] if response is not None else str(error)),
            ) from error
