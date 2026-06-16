import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingDurationReportContract(unittest.TestCase):

    def test_report_exists_and_is_dataclass(self):
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        self.assertTrue(is_dataclass(ManufacturingDurationReport))

    def test_report_has_required_fields(self):
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingDurationReport)],
            [
                "estimated_cnc_minutes",
                "estimated_drilling_minutes",
                "estimated_edge_banding_minutes",
                "estimated_assembly_minutes",
                "total_production_minutes",
                "warnings",
            ],
        )


if __name__ == "__main__":
    unittest.main()
