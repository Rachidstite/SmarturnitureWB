import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingValidationSummaryReport(unittest.TestCase):
    def test_defaults_counts_to_zero(self):
        from manufacturing.manufacturing_validation_summary_report import (
            ManufacturingValidationSummaryReport,
        )

        report = ManufacturingValidationSummaryReport()

        self.assertEqual(report.total_rule_count, 0)
        self.assertEqual(report.passed_rule_count, 0)
        self.assertEqual(report.failed_rule_count, 0)
        self.assertEqual(report.warning_count, 0)
        self.assertEqual(report.blocking_issue_count, 0)

    def test_defaults_ready_for_manufacturing_to_false(self):
        from manufacturing.manufacturing_validation_summary_report import (
            ManufacturingValidationSummaryReport,
        )

        report = ManufacturingValidationSummaryReport()

        self.assertFalse(report.ready_for_manufacturing)

    def test_defaults_message_lists_to_empty_lists(self):
        from manufacturing.manufacturing_validation_summary_report import (
            ManufacturingValidationSummaryReport,
        )

        report = ManufacturingValidationSummaryReport()

        self.assertEqual(report.blocking_messages, [])
        self.assertEqual(report.warning_messages, [])

    def test_message_lists_are_independent_per_instance(self):
        from manufacturing.manufacturing_validation_summary_report import (
            ManufacturingValidationSummaryReport,
        )

        first = ManufacturingValidationSummaryReport()
        second = ManufacturingValidationSummaryReport()

        first.blocking_messages.append("blocking")
        first.warning_messages.append("warning")

        self.assertEqual(second.blocking_messages, [])
        self.assertEqual(second.warning_messages, [])

    def test_defaults_source_to_empty_string(self):
        from manufacturing.manufacturing_validation_summary_report import (
            ManufacturingValidationSummaryReport,
        )

        report = ManufacturingValidationSummaryReport()

        self.assertEqual(report.source, "")

    def test_can_store_all_fields(self):
        from manufacturing.manufacturing_validation_summary_report import (
            ManufacturingValidationSummaryReport,
        )

        report = ManufacturingValidationSummaryReport(
            ready_for_manufacturing=True,
            total_rule_count=5,
            passed_rule_count=4,
            failed_rule_count=1,
            warning_count=2,
            blocking_issue_count=1,
            blocking_messages=["panel-1 missing material"],
            warning_messages=["panel-2 edge incomplete"],
            source="manufacturing-validation-summary",
        )

        self.assertTrue(report.ready_for_manufacturing)
        self.assertEqual(report.total_rule_count, 5)
        self.assertEqual(report.passed_rule_count, 4)
        self.assertEqual(report.failed_rule_count, 1)
        self.assertEqual(report.warning_count, 2)
        self.assertEqual(report.blocking_issue_count, 1)
        self.assertEqual(report.blocking_messages, ["panel-1 missing material"])
        self.assertEqual(report.warning_messages, ["panel-2 edge incomplete"])
        self.assertEqual(report.source, "manufacturing-validation-summary")

    def test_dataclass_fields_are_exact(self):
        from manufacturing.manufacturing_validation_summary_report import (
            ManufacturingValidationSummaryReport,
        )

        self.assertTrue(is_dataclass(ManufacturingValidationSummaryReport))
        self.assertEqual(
            [field.name for field in fields(ManufacturingValidationSummaryReport)],
            [
                "ready_for_manufacturing",
                "total_rule_count",
                "passed_rule_count",
                "failed_rule_count",
                "warning_count",
                "blocking_issue_count",
                "blocking_messages",
                "warning_messages",
                "source",
            ],
        )

        signature = inspect.signature(ManufacturingValidationSummaryReport)
        self.assertEqual(
            list(signature.parameters),
            [
                "ready_for_manufacturing",
                "total_rule_count",
                "passed_rule_count",
                "failed_rule_count",
                "warning_count",
                "blocking_issue_count",
                "blocking_messages",
                "warning_messages",
                "source",
            ],
        )

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "manufacturing.manufacturing_validation_summary_report"
        )
        source = inspect.getsource(module)

        self.assertIn("ManufacturingValidationSummaryReport", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "manufacturing.manufacturing_validation_summary_report"
        )
        source = inspect.getsource(module)

        for token in (
            "builder",
            "decision",
            "UI",
            "dashboard",
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
            "manufacturing.manufacturing_validation_summary_report"
        )
        source = inspect.getsource(module)

        for token in (
            "builder",
            "decision",
            "UI",
            "dashboard",
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
