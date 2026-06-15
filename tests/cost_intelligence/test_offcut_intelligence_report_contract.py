import unittest
from dataclasses import fields, is_dataclass


class TestOffcutIntelligenceReportContract(unittest.TestCase):

    def test_report_is_dataclass_with_required_fields(self):
        from cost_intelligence.offcut_intelligence_report import (
            OffcutIntelligenceReport,
        )

        self.assertTrue(is_dataclass(OffcutIntelligenceReport))
        self.assertEqual(
            [field.name for field in fields(OffcutIntelligenceReport)],
            [
                "reuse_rate",
                "waste_recovery_score",
                "recommendation",
                "warnings",
                "reusable_area",
                "largest_reusable_area",
                "estimated_recovered_value",
            ],
        )

    def test_report_has_safe_reuse_intelligence_defaults(self):
        from cost_intelligence.offcut_intelligence_report import (
            OffcutIntelligenceReport,
        )

        report = OffcutIntelligenceReport()

        self.assertEqual(report.reusable_area, 0.0)
        self.assertEqual(report.largest_reusable_area, 0.0)
        self.assertEqual(report.estimated_recovered_value, 0.0)


if __name__ == "__main__":
    unittest.main()
