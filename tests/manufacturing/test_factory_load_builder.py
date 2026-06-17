import unittest


class TestFactoryLoadBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from manufacturing.factory_load_builder import FactoryLoadBuilder

        self.assertTrue(callable(FactoryLoadBuilder().build))

    def test_builder_calculates_low_load(self):
        from manufacturing.factory_load_builder import FactoryLoadBuilder
        from manufacturing.factory_resource_report import FactoryResourceReport
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = FactoryLoadBuilder().build(
            FactoryResourceReport(weekly_capacity_hours=10),
            ManufacturingDurationReport(
                estimated_cnc_minutes=100.0,
                estimated_assembly_minutes=80.0,
                estimated_edge_banding_minutes=60.0,
            ),
        )

        self.assertEqual(report.cnc_load_percent, (100.0 / 600.0) * 100)
        self.assertEqual(report.assembly_load_percent, (80.0 / 600.0) * 100)
        self.assertEqual(report.edge_banding_load_percent, (60.0 / 600.0) * 100)
        self.assertEqual(report.bottleneck, "CNC")
        self.assertEqual(report.status, "LOW")

    def test_builder_calculates_medium_load(self):
        from manufacturing.factory_load_builder import FactoryLoadBuilder
        from manufacturing.factory_resource_report import FactoryResourceReport
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = FactoryLoadBuilder().build(
            FactoryResourceReport(weekly_capacity_hours=10),
            ManufacturingDurationReport(
                estimated_cnc_minutes=200.0,
                estimated_assembly_minutes=500.0,
                estimated_edge_banding_minutes=50.0,
            ),
        )

        self.assertEqual(report.bottleneck, "ASSEMBLY")
        self.assertEqual(report.status, "MEDIUM")

    def test_builder_calculates_high_load(self):
        from manufacturing.factory_load_builder import FactoryLoadBuilder
        from manufacturing.factory_resource_report import FactoryResourceReport
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = FactoryLoadBuilder().build(
            FactoryResourceReport(weekly_capacity_hours=10),
            ManufacturingDurationReport(
                estimated_cnc_minutes=200.0,
                estimated_assembly_minutes=800.0,
                estimated_edge_banding_minutes=50.0,
            ),
        )

        self.assertEqual(report.bottleneck, "ASSEMBLY")
        self.assertEqual(report.status, "HIGH")

    def test_builder_handles_zero_capacity_safely(self):
        from manufacturing.factory_load_builder import FactoryLoadBuilder
        from manufacturing.factory_resource_report import FactoryResourceReport
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = FactoryLoadBuilder().build(
            FactoryResourceReport(),
            ManufacturingDurationReport(
                estimated_cnc_minutes=100.0,
                estimated_assembly_minutes=80.0,
                estimated_edge_banding_minutes=60.0,
            ),
        )

        self.assertEqual(report.cnc_load_percent, 0.0)
        self.assertEqual(report.assembly_load_percent, 0.0)
        self.assertEqual(report.edge_banding_load_percent, 0.0)
        self.assertEqual(report.bottleneck, "CNC")
        self.assertEqual(report.status, "LOW")


if __name__ == "__main__":
    unittest.main()
