import unittest


class TestFactoryWorkloadBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.factory_workload_builder import FactoryWorkloadBuilder

        self.assertTrue(callable(FactoryWorkloadBuilder().build))

    def test_builder_calculates_workload_from_schedule_reports(self):
        from manufacturing.factory_workload_builder import FactoryWorkloadBuilder
        from manufacturing.production_schedule_report import (
            ProductionScheduleReport,
        )

        reports = [
            ProductionScheduleReport(
                required_work_days=2.0,
                schedule_risk_level="LOW",
            ),
            ProductionScheduleReport(
                required_work_days=4.0,
                schedule_risk_level="MEDIUM",
            ),
        ]

        report = FactoryWorkloadBuilder().build(reports)

        self.assertEqual(report.active_project_count, 2)
        self.assertEqual(report.total_required_work_days, 6.0)
        self.assertEqual(report.average_required_work_days, 3.0)
        self.assertEqual(report.highest_schedule_risk_level, "MEDIUM")

    def test_builder_marks_available_for_light_workload(self):
        from manufacturing.factory_workload_builder import FactoryWorkloadBuilder
        from manufacturing.production_schedule_report import (
            ProductionScheduleReport,
        )

        report = FactoryWorkloadBuilder().build(
            [ProductionScheduleReport(required_work_days=2.0)]
        )

        self.assertEqual(report.factory_workload_status, "AVAILABLE")

    def test_builder_marks_busy_for_medium_workload(self):
        from manufacturing.factory_workload_builder import FactoryWorkloadBuilder
        from manufacturing.production_schedule_report import (
            ProductionScheduleReport,
        )

        report = FactoryWorkloadBuilder().build(
            [ProductionScheduleReport(required_work_days=7.0)]
        )

        self.assertEqual(report.factory_workload_status, "BUSY")

    def test_builder_marks_overloaded_for_high_workload(self):
        from manufacturing.factory_workload_builder import FactoryWorkloadBuilder
        from manufacturing.production_schedule_report import (
            ProductionScheduleReport,
        )

        report = FactoryWorkloadBuilder().build(
            [ProductionScheduleReport(required_work_days=14.0)]
        )

        self.assertEqual(report.factory_workload_status, "OVERLOADED")

    def test_builder_propagates_warnings(self):
        from manufacturing.factory_workload_builder import FactoryWorkloadBuilder
        from manufacturing.production_schedule_report import (
            ProductionScheduleReport,
        )

        report = FactoryWorkloadBuilder().build(
            [
                ProductionScheduleReport(warnings=["Schedule warning"]),
            ]
        )

        self.assertEqual(report.warnings, ["Schedule warning"])


if __name__ == "__main__":
    unittest.main()
