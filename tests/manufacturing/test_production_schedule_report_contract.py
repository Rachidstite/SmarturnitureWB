import unittest
from dataclasses import fields, is_dataclass


class TestProductionScheduleReportContract(unittest.TestCase):

    def test_report_exists_and_is_dataclass(self):
        from manufacturing.production_schedule_report import (
            ProductionScheduleReport,
        )

        self.assertTrue(is_dataclass(ProductionScheduleReport))

    def test_report_has_required_fields(self):
        from manufacturing.production_schedule_report import (
            ProductionScheduleReport,
        )

        self.assertEqual(
            [field.name for field in fields(ProductionScheduleReport)],
            [
                "required_work_days",
                "required_machine_days",
                "required_operator_days",
                "capacity_utilization_percent",
                "schedule_risk_level",
                "warnings",
            ],
        )


if __name__ == "__main__":
    unittest.main()
