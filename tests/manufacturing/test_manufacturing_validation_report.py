import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingValidationReport(unittest.TestCase):
    def test_defaults_all_counts_to_zero(self):
        from manufacturing.manufacturing_validation_report import (
            ManufacturingValidationReport,
        )

        report = ManufacturingValidationReport()

        self.assertEqual(report.total_rule_count, 0)
        self.assertEqual(report.passed_rule_count, 0)
        self.assertEqual(report.failed_rule_count, 0)
        self.assertEqual(report.warning_count, 0)
        self.assertEqual(report.blocking_issue_count, 0)

    def test_defaults_ready_for_manufacturing_to_false(self):
        from manufacturing.manufacturing_validation_report import (
            ManufacturingValidationReport,
        )

        report = ManufacturingValidationReport()

        self.assertFalse(report.ready_for_manufacturing)

    def test_defaults_source_to_empty_string(self):
        from manufacturing.manufacturing_validation_report import (
            ManufacturingValidationReport,
        )

        report = ManufacturingValidationReport()

        self.assertEqual(report.source, "")

    def test_can_store_all_fields(self):
        from manufacturing.manufacturing_validation_report import (
            ManufacturingValidationReport,
        )

        report = ManufacturingValidationReport(
            total_rule_count=7,
            passed_rule_count=4,
            failed_rule_count=3,
            warning_count=2,
            blocking_issue_count=1,
            ready_for_manufacturing=True,
            source="manufacturing-validation-aggregator",
        )

        self.assertEqual(report.total_rule_count, 7)
        self.assertEqual(report.passed_rule_count, 4)
        self.assertEqual(report.failed_rule_count, 3)
        self.assertEqual(report.warning_count, 2)
        self.assertEqual(report.blocking_issue_count, 1)
        self.assertTrue(report.ready_for_manufacturing)
        self.assertEqual(report.source, "manufacturing-validation-aggregator")

    def test_dataclass_fields_are_exact(self):
        from manufacturing.manufacturing_validation_report import (
            ManufacturingValidationReport,
        )

        self.assertTrue(is_dataclass(ManufacturingValidationReport))
        self.assertEqual(
            [field.name for field in fields(ManufacturingValidationReport)],
            [
                "total_rule_count",
                "passed_rule_count",
                "failed_rule_count",
                "warning_count",
                "blocking_issue_count",
                "ready_for_manufacturing",
                "source",
            ],
        )

        signature = inspect.signature(ManufacturingValidationReport)
        self.assertEqual(
            list(signature.parameters),
            [
                "total_rule_count",
                "passed_rule_count",
                "failed_rule_count",
                "warning_count",
                "blocking_issue_count",
                "ready_for_manufacturing",
                "source",
            ],
        )

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "manufacturing.manufacturing_validation_report"
        )
        source = inspect.getsource(module)

        self.assertIn("ManufacturingValidationReport", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "manufacturing.manufacturing_validation_report"
        )
        source = inspect.getsource(module)

        for token in (
            "builder",
            "decision",
            "cost",
            "export",
            "CNC",
            "nesting",
            "geometry",
            "SceneGraph",
            "FreeCAD",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_does_not_contain_logic_keywords(self):
        module = importlib.import_module(
            "manufacturing.manufacturing_validation_report"
        )
        source = inspect.getsource(module)

        for token in (
            "builder",
            "decision",
            "cost",
            "export",
            "CNC",
            "nesting",
            "geometry",
            "if ",
            "for ",
            "while ",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
