import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestCabinetOperationalReadinessReport(unittest.TestCase):
    def test_default_report_is_ready(self):
        from project_engineering.cabinet_operational_readiness_report import (
            CabinetOperationalReadinessReport,
        )

        report = CabinetOperationalReadinessReport(cabinet_id="cabinet-1")

        self.assertTrue(is_dataclass(CabinetOperationalReadinessReport))
        self.assertEqual(
            [field.name for field in fields(CabinetOperationalReadinessReport)],
            [
                "cabinet_id",
                "ready_for_operation",
                "ready_for_installation",
                "ready_for_service",
                "overall_ready",
                "warnings",
                "violations",
                "source",
            ],
        )
        self.assertEqual(report.cabinet_id, "cabinet-1")
        self.assertTrue(report.ready_for_operation)
        self.assertTrue(report.ready_for_installation)
        self.assertTrue(report.ready_for_service)
        self.assertTrue(report.overall_ready)
        self.assertEqual(report.warnings, [])
        self.assertEqual(report.violations, [])
        self.assertEqual(report.source, "")

    def test_stores_cabinet_id_source_warnings_and_violations(self):
        from project_engineering.cabinet_operational_readiness_report import (
            CabinetOperationalReadinessReport,
        )

        report = CabinetOperationalReadinessReport(
            cabinet_id="cabinet-7",
            warnings=["review clear access"],
            violations=["service access blocked"],
            source="p3-readiness",
        )

        self.assertEqual(report.cabinet_id, "cabinet-7")
        self.assertEqual(report.warnings, ["review clear access"])
        self.assertEqual(report.violations, ["service access blocked"])
        self.assertEqual(report.source, "p3-readiness")

    def test_overall_ready_can_be_explicitly_false(self):
        from project_engineering.cabinet_operational_readiness_report import (
            CabinetOperationalReadinessReport,
        )

        report = CabinetOperationalReadinessReport(
            cabinet_id="cabinet-9",
            overall_ready=False,
        )

        self.assertFalse(report.overall_ready)
        self.assertTrue(report.ready_for_operation)
        self.assertTrue(report.ready_for_installation)
        self.assertTrue(report.ready_for_service)

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.cabinet_operational_readiness_report"
        )
        source = inspect.getsource(module)

        self.assertIn("CabinetOperationalReadinessReport", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.cabinet_operational_readiness_report"
        )
        source = inspect.getsource(module)

        for token in (
            "manufacturing",
            "cost",
            "exports",
            "FreeCAD",
            "operational_capability_contract",
            "operational_decision_from_rule_results",
            "operational_rule_result",
            "operational_decision_report",
            "motion_contract",
            "accessibility_contract",
            "installation_sequence_contract",
            "serviceability_contract",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_contract_is_cabinet_level_without_component_specific_fields(self):
        from project_engineering.cabinet_operational_readiness_report import (
            CabinetOperationalReadinessReport,
        )

        signature = inspect.signature(CabinetOperationalReadinessReport)
        self.assertEqual(
            list(signature.parameters),
            [
                "cabinet_id",
                "ready_for_operation",
                "ready_for_installation",
                "ready_for_service",
                "overall_ready",
                "warnings",
                "violations",
                "source",
            ],
        )
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)


if __name__ == "__main__":
    unittest.main()
