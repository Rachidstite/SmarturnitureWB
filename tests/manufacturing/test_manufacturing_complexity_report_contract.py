import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingComplexityReportContract(unittest.TestCase):

    def test_report_exists_and_is_dataclass(self):
        from manufacturing.manufacturing_complexity_report import (
            ManufacturingComplexityReport,
        )

        self.assertTrue(is_dataclass(ManufacturingComplexityReport))

    def test_report_has_required_fields(self):
        from manufacturing.manufacturing_complexity_report import (
            ManufacturingComplexityReport,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingComplexityReport)],
            [
                "complexity_level",
                "complexity_score",
                "engineering_complexity",
                "estimated_engineering_minutes",
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
        self.assertEqual(report.engineering_complexity, "LOW")
        self.assertEqual(report.estimated_engineering_minutes, 0.0)
        self.assertEqual(report.main_drivers, [])
        self.assertEqual(report.recommendations, [])
        self.assertEqual(report.warnings, [])


if __name__ == "__main__":
    unittest.main()
