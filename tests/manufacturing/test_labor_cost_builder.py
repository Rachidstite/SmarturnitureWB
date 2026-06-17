import unittest


class TestLaborCostBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.labor_cost_builder import LaborCostBuilder

        self.builder = LaborCostBuilder(
            cnc_hourly_rate=60.0,
            drilling_hourly_rate=30.0,
            edge_banding_hourly_rate=45.0,
            assembly_hourly_rate=90.0,
            currency="MAD",
        )

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_calculates_labor_costs(self):
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = self.builder.build(
            ManufacturingDurationReport(
                estimated_cnc_minutes=120.0,
                estimated_drilling_minutes=60.0,
                estimated_edge_banding_minutes=30.0,
                estimated_assembly_minutes=90.0,
            )
        )

        self.assertEqual(report.cnc_labor_cost, 120.0)
        self.assertEqual(report.drilling_labor_cost, 30.0)
        self.assertEqual(report.edge_banding_labor_cost, 22.5)
        self.assertEqual(report.assembly_labor_cost, 135.0)
        self.assertEqual(report.total_labor_cost, 307.5)
        self.assertEqual(report.currency, "MAD")

    def test_builder_warns_when_rates_default_to_zero(self):
        from manufacturing.labor_cost_builder import LaborCostBuilder
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = LaborCostBuilder().build(
            ManufacturingDurationReport(
                estimated_cnc_minutes=60.0,
                estimated_drilling_minutes=60.0,
                estimated_edge_banding_minutes=60.0,
                estimated_assembly_minutes=60.0,
            )
        )

        self.assertEqual(report.total_labor_cost, 0.0)
        self.assertIn("Labor hourly rates are defaulting to zero", report.warnings)

    def test_builder_does_not_mutate_input_report(self):
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        duration_report = ManufacturingDurationReport(
            estimated_cnc_minutes=120.0,
            estimated_drilling_minutes=60.0,
            estimated_edge_banding_minutes=30.0,
            estimated_assembly_minutes=90.0,
            warnings=["duration warning"],
        )
        snapshot = dict(duration_report.__dict__)

        self.builder.build(duration_report)

        self.assertEqual(duration_report.__dict__, snapshot)


if __name__ == "__main__":
    unittest.main()
