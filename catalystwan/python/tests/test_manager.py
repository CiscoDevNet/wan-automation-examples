"""Unit tests for API-key authentication and HTTP handling."""

from __future__ import annotations

import unittest
from typing import Any

from utilities.manager import ManagerClient


class FakeResponse:
    def __init__(self, *, text: str = "", payload: Any = None, status_code: int = 200):
        self.text = text
        self._payload = payload
        self.status_code = status_code
        self.content = text.encode() if payload is None else b"json"
        self.headers = {"Content-Type": "application/json"}

    def raise_for_status(self) -> None:
        return None

    def json(self) -> Any:
        return self._payload


class FakeSession:
    def __init__(self) -> None:
        self.headers: dict[str, str] = {}
        self.verify: bool | str = True
        self.calls: list[tuple[str, str, dict[str, Any]]] = []
        self.closed = False

    def request(self, method: str, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append((method, url, kwargs))
        if url.endswith("/client/token"):
            return FakeResponse(text="test-xsrf-token")
        return FakeResponse(payload={"data": [{"ok": True}]})

    def close(self) -> None:
        self.closed = True


class ManagerClientTests(unittest.TestCase):
    def test_api_key_fetches_xsrf_and_is_used_for_requests(self) -> None:
        session = FakeSession()
        client = ManagerClient("manager.example", "secret-key", session=session)

        self.assertEqual(session.headers["Authorization"], "Bearer secret-key")
        self.assertEqual(session.headers["X-XSRF-TOKEN"], "test-xsrf-token")
        self.assertEqual(session.calls[0][0], "GET")
        self.assertTrue(session.calls[0][1].endswith("/dataservice/client/token"))
        self.assertEqual(session.calls[0][2]["headers"], {"X-XSRF-TOKEN": None})

        payload = client.get("/client/about")
        self.assertEqual(payload, {"data": [{"ok": True}]})
        self.assertTrue(session.calls[1][1].endswith("/dataservice/client/about"))

        client.close()
        self.assertTrue(session.closed)


if __name__ == "__main__":
    unittest.main()
