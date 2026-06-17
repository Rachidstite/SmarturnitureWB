import unittest
from dataclasses import fields, is_dataclass


class TestAssemblyIntelligenceReportContract(unittest.TestCase):

    def test_report_is_dataclass_with_exact_field_order(self):
        from manufacturing.assembly_intelligence_report import (
            AssemblyIntelligenceReport,
        )

        self.assertTrue(is_dataclass(AssemblyIntelligenceReport))
        self.assertEqual(
            [field.name for field in fields(AssemblyIntelligenceReport)],
            [
                "assembly_time_minutes",
                "assembly_complexity",
                "required_installers",
                "joinery_density",
                "installation_risk",
                "warnings",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.assembly_intelligence_report import (
            AssemblyIntelligenceReport,
        )

        report = AssemblyIntelligenceReport()

        self.assertEqual(report.assembly_time_minutes, 0.0)
        self.assertEqual(report.assembly_complexity, "LOW")
        self.assertEqual(report.required_installers, 1)
        self.assertEqual(report.joinery_density, 0)
        self.assertEqual(report.installation_risk, "LOW")
        self.assertEqual(report.warnings, [])


if __name__ == "__main__":
    unittest.main()
