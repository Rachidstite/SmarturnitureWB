import unittest
from dataclasses import fields, is_dataclass
import importlib
import inspect


class TestManufacturingProductionPackageContract(unittest.TestCase):

    def test_contract_exists_and_is_dataclass(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        self.assertTrue(is_dataclass(ManufacturingProductionPackage))

    def test_contract_has_required_fields(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingProductionPackage)],
            [
                "cutlist_report",
                "edge_report",
                "machining_report",
                "summary_report",
                "validation_summary_report",
                "release_ready",
                "warnings",
            ],
        )

    def test_contract_defaults(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        package = ManufacturingProductionPackage()

        self.assertIsNone(package.cutlist_report)
        self.assertIsNone(package.edge_report)
        self.assertIsNone(package.machining_report)
        self.assertIsNone(package.summary_report)
        self.assertIsNone(package.validation_summary_report)
        self.assertFalse(package.release_ready)
        self.assertEqual(package.warnings, [])

    def test_warning_defaults_are_independent(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        first_package = ManufacturingProductionPackage()
        second_package = ManufacturingProductionPackage()

        first_package.warnings.append("warning")

        self.assertEqual(second_package.warnings, [])
        self.assertIsNot(first_package.warnings, second_package.warnings)

    def test_validation_summary_report_defaults_to_none(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        package = ManufacturingProductionPackage()

        self.assertIsNone(package.validation_summary_report)

    def test_validation_summary_report_accepts_summary_report(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )
        from manufacturing.manufacturing_validation_summary_report import (
            ManufacturingValidationSummaryReport,
        )

        summary_report = ManufacturingValidationSummaryReport(
            ready_for_manufacturing=True,
            total_rule_count=3,
            passed_rule_count=3,
            failed_rule_count=0,
            warning_count=0,
            blocking_issue_count=0,
            blocking_messages=[],
            warning_messages=[],
            source="manufacturing-validation-summary",
        )

        package = ManufacturingProductionPackage(
            validation_summary_report=summary_report,
        )

        self.assertIs(package.validation_summary_report, summary_report)

    def test_backward_compatibility_is_preserved(self):
        from manufacturing.manufacturing_production_package import (
            ManufacturingProductionPackage,
        )

        package = ManufacturingProductionPackage(
            cutlist_report="cutlist",
            edge_report="edge",
            machining_report="machining",
            summary_report="summary",
            release_ready=True,
            warnings=["warning"],
        )

        self.assertEqual(package.cutlist_report, "cutlist")
        self.assertEqual(package.edge_report, "edge")
        self.assertEqual(package.machining_report, "machining")
        self.assertEqual(package.summary_report, "summary")
        self.assertIsNone(package.validation_summary_report)
        self.assertTrue(package.release_ready)
        self.assertEqual(package.warnings, ["warning"])

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "manufacturing.manufacturing_production_package"
        )

        source = inspect.getsource(module)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "manufacturing.manufacturing_production_package"
        )

        source = inspect.getsource(module)
        for token in (
            "manufacturing_release_validator",
            "manufacturing_validator",
            "validation logic",
            "CNC",
            "export",
            "cost",
            "geometry",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
