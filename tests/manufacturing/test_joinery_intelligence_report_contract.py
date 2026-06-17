import unittest
from dataclasses import fields, is_dataclass


class TestJoineryIntelligenceReportContract(unittest.TestCase):

    def test_report_is_dataclass_with_exact_field_order(self):
        from manufacturing.joinery_intelligence_report import (
            JoineryIntelligenceReport,
        )

        self.assertTrue(is_dataclass(JoineryIntelligenceReport))
        self.assertEqual(
            [field.name for field in fields(JoineryIntelligenceReport)],
            [
                "total_minifix",
                "total_hinges",
                "total_drawer_slides",
                "total_handles",
                "total_face_holes",
                "total_edge_holes",
                "total_cam_holes",
                "joinery_complexity_score",
                "warnings",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.joinery_intelligence_report import (
            JoineryIntelligenceReport,
        )

        report = JoineryIntelligenceReport()

        self.assertEqual(report.total_minifix, 0)
        self.assertEqual(report.total_hinges, 0)
        self.assertEqual(report.total_drawer_slides, 0)
        self.assertEqual(report.total_handles, 0)
        self.assertEqual(report.total_face_holes, 0)
        self.assertEqual(report.total_edge_holes, 0)
        self.assertEqual(report.total_cam_holes, 0)
        self.assertEqual(report.joinery_complexity_score, 0)
        self.assertEqual(report.warnings, [])


if __name__ == "__main__":
    unittest.main()
