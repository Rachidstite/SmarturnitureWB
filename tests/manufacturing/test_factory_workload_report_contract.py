import unittest
from dataclasses import fields, is_dataclass


class TestFactoryWorkloadReportContract(unittest.TestCase):

    def test_report_exists_and_is_dataclass(self):
        from manufacturing.factory_workload_report import FactoryWorkloadReport

        self.assertTrue(is_dataclass(FactoryWorkloadReport))

    def test_report_has_required_fields(self):
        from manufacturing.factory_workload_report import FactoryWorkloadReport

        self.assertEqual(
            [field.name for field in fields(FactoryWorkloadReport)],
            [
                "active_project_count",
                "total_required_work_days",
                "average_required_work_days",
                "highest_schedule_risk_level",
                "factory_workload_status",
                "warnings",
            ],
        )


if __name__ == "__main__":
    unittest.main()
