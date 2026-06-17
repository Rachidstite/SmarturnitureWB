import unittest
from dataclasses import fields, is_dataclass


class TestFactoryResourceReportContract(unittest.TestCase):

    def test_report_exists_and_is_dataclass(self):
        from manufacturing.factory_resource_report import FactoryResourceReport

        self.assertTrue(is_dataclass(FactoryResourceReport))

    def test_report_has_required_fields_in_order(self):
        from manufacturing.factory_resource_report import FactoryResourceReport

        self.assertEqual(
            [field.name for field in fields(FactoryResourceReport)],
            [
                "workers",
                "cnc_machines",
                "edge_banding_machines",
                "assembly_stations",
                "daily_work_hours",
                "workdays_per_week",
                "weekly_capacity_hours",
            ],
        )

    def test_report_has_safe_defaults(self):
        from manufacturing.factory_resource_report import FactoryResourceReport

        report = FactoryResourceReport()

        self.assertEqual(report.workers, 0)
        self.assertEqual(report.cnc_machines, 0)
        self.assertEqual(report.edge_banding_machines, 0)
        self.assertEqual(report.assembly_stations, 0)
        self.assertEqual(report.daily_work_hours, 0.0)
        self.assertEqual(report.workdays_per_week, 0)
        self.assertEqual(report.weekly_capacity_hours, 0.0)


if __name__ == "__main__":
    unittest.main()
