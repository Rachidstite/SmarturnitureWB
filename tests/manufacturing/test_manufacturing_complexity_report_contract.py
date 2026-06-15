import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingComplexityReportContract(unittest.TestCase):

    def test_report_exists_and_is_dataclass(self):
        from manufacturing.manufacturing_complexity_report import (
            ManufacturingComplexityReport,
        )

        self.assertTrue(is_dataclass(ManufacturingComplexityReport))

    def test_report_has_required_fields_in_order(self):
        from manufacturing.manufacturing_complexity_report import (
            ManufacturingComplexityReport,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingComplexityReport)],
            [
                "complexity_level",
                "complexity_score",
                "main_drivers",
                "recommendations",
                "warnings",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.manufacturing_complexity_report import (
            ManufacturingComplexityReport,
        )

        report = ManufacturingComplexityReport()

        self.assertEqual(report.complexity_level, "LOW")
        self.assertEqual(report.complexity_score, 0)
        self.assertEqual(report.main_drivers, [])
        self.assertEqual(report.recommendations, [])
        self.assertEqual(report.warnings, [])

    def test_list_defaults_are_independent(self):
        from manufacturing.manufacturing_complexity_report import (
            ManufacturingComplexityReport,
        )

        first = ManufacturingComplexityReport()
        second = ManufacturingComplexityReport()

        first.main_drivers.append("driver")
        first.recommendations.append("recommendation")
        first.warnings.append("warning")

        self.assertEqual(second.main_drivers, [])
        self.assertEqual(second.recommendations, [])
        self.assertEqual(second.warnings, [])
        self.assertIsNot(first.main_drivers, second.main_drivers)
        self.assertIsNot(first.recommendations, second.recommendations)
        self.assertIsNot(first.warnings, second.warnings)


if __name__ == "__main__":
    unittest.main()
