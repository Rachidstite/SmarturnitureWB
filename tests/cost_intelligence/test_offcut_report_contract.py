import unittest
from dataclasses import fields, is_dataclass


class TestOffcutReportContract(unittest.TestCase):

    def test_offcut_report_exists_and_is_dataclass(self):

        try:
            from cost_intelligence.offcut_report import OffcutReport
        except ImportError:
            self.fail(
                "OffcutReport does not exist"
            )

        self.assertTrue(
            is_dataclass(OffcutReport),
        )

    def test_offcut_report_contains_required_fields(self):

        from cost_intelligence.offcut_report import OffcutReport

        field_names = {
            field.name
            for field in fields(OffcutReport)
        }

        self.assertEqual(
            field_names,
            {
                "offcuts",
                "total_offcuts",
                "reusable_offcuts",
                "total_offcut_area",
                "largest_offcut_area",
                "warnings",
            },
        )

    def test_offcut_report_can_be_created_with_summary_values(self):

        from cost_intelligence.offcut import Offcut
        from cost_intelligence.offcut_report import OffcutReport

        offcut = Offcut(
            id="OFFCUT-001",
            material="MDF",
            thickness=18,
            width=600,
            height=400,
            source_sheet="SHEET-001",
        )

        report = OffcutReport(
            offcuts=[offcut],
            total_offcuts=1,
            reusable_offcuts=1,
            total_offcut_area=240000,
            largest_offcut_area=240000,
            warnings=[],
        )

        self.assertEqual(
            report.offcuts,
            [offcut],
        )
        self.assertEqual(
            report.total_offcuts,
            1,
        )
        self.assertEqual(
            report.reusable_offcuts,
            1,
        )
        self.assertEqual(
            report.total_offcut_area,
            240000,
        )
        self.assertEqual(
            report.largest_offcut_area,
            240000,
        )

    def test_offcut_report_has_safe_list_defaults(self):

        from cost_intelligence.offcut_report import OffcutReport

        first_report = OffcutReport()
        second_report = OffcutReport()

        first_report.offcuts.append(
            object(),
        )
        first_report.warnings.append(
            "warning",
        )

        self.assertEqual(
            second_report.offcuts,
            [],
        )
        self.assertEqual(
            second_report.warnings,
            [],
        )


if __name__ == "__main__":
    unittest.main()
