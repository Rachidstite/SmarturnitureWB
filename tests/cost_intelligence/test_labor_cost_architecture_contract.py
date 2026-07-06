import inspect
import unittest


class TestLaborCostArchitectureContract(unittest.TestCase):

    def test_manufacturing_cost_calculator_already_prices_drilling_and_edge_banding(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        context = ManufacturingCostContext(
            total_edge_meters=20.0,
            total_drilling_operations=30,
        )

        report = ManufacturingCostCalculator().calculate(context)

        self.assertGreater(report.edge_banding_cost, 0.0)
        self.assertGreater(report.drilling_cost, 0.0)

    def test_labor_cost_builder_prices_drilling_and_edge_banding_labor_separately(self):
        from manufacturing.labor_cost_builder import LaborCostBuilder
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        report = LaborCostBuilder(
            drilling_hourly_rate=60.0,
            edge_banding_hourly_rate=60.0,
        ).build(
            ManufacturingDurationReport(
                estimated_drilling_minutes=30.0,
                estimated_edge_banding_minutes=15.0,
            )
        )

        self.assertGreater(report.drilling_labor_cost, 0.0)
        self.assertGreater(report.edge_banding_labor_cost, 0.0)

    def test_labor_cost_builder_is_now_consumed_by_cost_intelligence_pipeline(self):
        import cost_intelligence.manufacturing_cost_pipeline_builder as pipeline

        source = inspect.getsource(pipeline)

        self.assertIn("LaborCostBuilder", source)
        self.assertIn("labor_cost_report", source)

    def test_labor_report_contains_unique_and_overlapping_labor_categories(self):
        from dataclasses import fields
        from manufacturing.labor_cost_report import LaborCostReport

        names = [field.name for field in fields(LaborCostReport)]

        self.assertIn("cnc_labor_cost", names)
        self.assertIn("assembly_labor_cost", names)
        self.assertIn("drilling_labor_cost", names)
        self.assertIn("edge_banding_labor_cost", names)

    def test_current_architecture_now_integrates_total_labor_cost(self):
        """
        Labor cost is now integrated into the manufacturing cost report.
        The calculator combines labor_cost_report fields into the
        ManufacturingCostReport and adds total_labor_cost to
        total_manufacturing_cost.
        """
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )
        from dataclasses import fields

        names = [field.name for field in fields(ManufacturingCostReport)]

        self.assertIn("total_labor_cost", names)
        self.assertIn("cnc_labor_cost", names)
        self.assertIn("drilling_labor_cost", names)
        self.assertIn("edge_banding_labor_cost", names)
        self.assertIn("assembly_labor_cost", names)


if __name__ == "__main__":
    unittest.main()
