import unittest


class TestFactoryResourceBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.factory_resource_builder import FactoryResourceBuilder

        self.assertTrue(callable(FactoryResourceBuilder().build))

    def test_builder_builds_report_from_default_catalog_service(self):
        from manufacturing.factory_resource_builder import FactoryResourceBuilder

        report = FactoryResourceBuilder().build()

        self.assertEqual(report.workers, 3)
        self.assertEqual(report.cnc_machines, 1)
        self.assertEqual(report.edge_banding_machines, 1)
        self.assertEqual(report.assembly_stations, 2)
        self.assertEqual(report.daily_work_hours, 8)
        self.assertEqual(report.workdays_per_week, 5)
        self.assertEqual(report.weekly_capacity_hours, 120)

    def test_builder_uses_injected_catalog_service(self):
        from manufacturing.factory_resource_builder import FactoryResourceBuilder

        class StubService:
            def load(self):
                return {
                    "workers": 4,
                    "cnc_machines": 2,
                    "edge_banding_machines": 1,
                    "assembly_stations": 3,
                    "daily_work_hours": 7.5,
                    "workdays_per_week": 4,
                }

        report = FactoryResourceBuilder(StubService()).build()

        self.assertEqual(report.workers, 4)
        self.assertEqual(report.cnc_machines, 2)
        self.assertEqual(report.edge_banding_machines, 1)
        self.assertEqual(report.assembly_stations, 3)
        self.assertEqual(report.daily_work_hours, 7.5)
        self.assertEqual(report.workdays_per_week, 4)
        self.assertEqual(report.weekly_capacity_hours, 120.0)

    def test_builder_handles_missing_catalog_fields_with_defaults(self):
        from manufacturing.factory_resource_builder import FactoryResourceBuilder

        class StubService:
            def load(self):
                return {"workers": 2}

        report = FactoryResourceBuilder(StubService()).build()

        self.assertEqual(report.workers, 2)
        self.assertEqual(report.cnc_machines, 0)
        self.assertEqual(report.edge_banding_machines, 0)
        self.assertEqual(report.assembly_stations, 0)
        self.assertEqual(report.daily_work_hours, 0.0)
        self.assertEqual(report.workdays_per_week, 0)
        self.assertEqual(report.weekly_capacity_hours, 0.0)


if __name__ == "__main__":
    unittest.main()
