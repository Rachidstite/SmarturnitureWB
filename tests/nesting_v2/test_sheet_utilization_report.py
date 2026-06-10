import unittest

from exports.nesting_engine import NestingPart
from exports.strategies import GuillotineStripStrategy


class TestSheetUtilizationReport(unittest.TestCase):

    def test_current_sheet_result_has_used_area_but_no_utilization_percent(self):

        parts = [
            NestingPart("P1", 100, 50, False),
        ]

        sheets = GuillotineStripStrategy().pack(
            parts,
            sheet_w=300,
            sheet_h=200,
            kerf=4,
        )

        sheet = sheets[0]

        self.assertTrue(
            hasattr(sheet, "used_area"),
        )

        self.assertFalse(
            hasattr(sheet, "utilization_percent"),
        )


if __name__ == "__main__":
    unittest.main()
