"""Unit tests for reusable monitoring request builders."""

from __future__ import annotations

import unittest

from monitoring.cases import (
    CASES,
    MonitoringOptions,
    application_query,
    availability_query,
    run_case,
)


class FakeClient:
    def __init__(self) -> None:
        self.last_call = None

    def get(self, path, *, params=None):
        self.last_call = ("GET", path, params, None)
        return {"data": []}

    def post(self, path, *, payload=None, params=None):
        self.last_call = ("POST", path, params, payload)
        return {"data": []}


class MonitoringCasesTests(unittest.TestCase):
    def test_registry_contains_all_documented_cases(self) -> None:
        self.assertEqual(
            set(CASES),
            {
                "system-status",
                "interfaces",
                "bfd-state",
                "tunnel-traffic",
                "applications",
                "sites",
                "circuits",
            },
        )

    def test_application_window_is_configurable(self) -> None:
        query = application_query(1000)
        self.assertEqual(query["query"]["rules"][0]["value"], ["1000"])

    def test_site_and_link_queries_use_expected_dimensions(self) -> None:
        site = availability_query(24, "site")
        link = availability_query(24, "link")
        self.assertEqual(site["query"]["rules"][1]["value"], ["site"])
        self.assertEqual(site["aggregation"]["field"][0]["property"], "site_id")
        self.assertEqual(link["query"]["rules"][1]["value"], ["link"])
        self.assertEqual(link["aggregation"]["field"][1]["property"], "color")

    def test_run_case_keeps_transport_out_of_domain_logic(self) -> None:
        client = FakeClient()
        case, _ = run_case(client, "applications", MonitoringOptions(hours=48))
        self.assertEqual(case.key, "applications")
        self.assertEqual(client.last_call[0:2], ("POST", "/statistics/dpi/aggregation"))
        self.assertEqual(client.last_call[3]["query"]["rules"][0]["value"], ["48"])


if __name__ == "__main__":
    unittest.main()
