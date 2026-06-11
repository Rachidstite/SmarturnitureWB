import unittest


class TestOffcutReportBuilder(unittest.TestCase):

    def test_offcut_report_builder_exists(self):

        try:
            from cost_intelligence.offcut_report_builder import (
                OffcutReportBuilder,
            )
        except ImportError:
            self.fail(
                "OffcutReportBuilder does not exist"
            )

    def test_builder_summarizes_offcuts(self):

        from cost_intelligence.offcut import Offcut
        from cost_intelligence.offcut_report import OffcutReport
        from cost_intelligence.offcut_report_builder import (
            OffcutReportBuilder,
        )

        offcuts = [
            Offcut(
                id="OFFCUT-001",
                material="MDF",
                thickness=18,
                width=600,
                height=400,
                source_sheet="SHEET-001",
            ),
            Offcut(
                id="OFFCUT-002",
                material="MDF",
                thickness=18,
                width=300,
                height=200,
                source_sheet="SHEET-001",
                reusable=False,
            ),
        ]

        report = OffcutReportBuilder().build(
            offcuts,
        )

        self.assertIsInstance(
            report,
            OffcutReport,
        )
        self.assertEqual(
            report.offcuts,
            offcuts,
        )
        self.assertEqual(
            report.total_offcuts,
            2,
        )
        self.assertEqual(
            report.reusable_offcuts,
            1,
        )
        self.assertEqual(
            report.total_offcut_area,
            300000,
        )
        self.assertEqual(
            report.largest_offcut_area,
            240000,
        )

    def test_builder_supports_empty_offcuts(self):

        from cost_intelligence.offcut_report_builder import (
            OffcutReportBuilder,
        )

        report = OffcutReportBuilder().build(
            [],
        )

        self.assertEqual(
            report.total_offcuts,
            0,
        )
        self.assertEqual(
            report.reusable_offcuts,
            0,
        )
        self.assertEqual(
            report.total_offcut_area,
            0,
        )
        self.assertEqual(
            report.largest_offcut_area,
            0,
        )


if __name__ == "__main__":
    unittest.main()
