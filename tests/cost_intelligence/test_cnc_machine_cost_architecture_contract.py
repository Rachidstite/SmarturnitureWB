import inspect
import unittest
from dataclasses import fields


class TestCncMachineCostArchitectureContract(unittest.TestCase):

    def test_cnc_time_exists_in_duration_report(self):
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        names = [field.name for field in fields(ManufacturingDurationReport)]

        self.assertIn("estimated_cnc_minutes", names)

    def test_cnc_labor_cost_exists_but_is_separate(self):
        from manufacturing.labor_cost_report import LaborCostReport

        names = [field.name for field in fields(LaborCostReport)]

        self.assertIn("cnc_labor_cost", names)

    def test_factory_capacity_models_cnc_machines(self):
        from manufacturing.factory_resource_report import FactoryResourceReport

        names = [field.name for field in fields(FactoryResourceReport)]

        self.assertIn("cnc_machines", names)

    def test_factory_load_models_cnc_load(self):
        from manufacturing.factory_load_report import FactoryLoadReport

        names = [field.name for field in fields(FactoryLoadReport)]

        self.assertIn("cnc_load_percent", names)

    def test_manufacturing_cost_report_does_not_yet_expose_machine_cost(self):
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )

        names = [field.name for field in fields(ManufacturingCostReport)]

        self.assertNotIn("machine_cost", names)
        self.assertNotIn("cnc_machine_cost", names)

    def test_manufacturing_cost_pipeline_does_not_consume_cnc_machine_cost_yet(self):
        import cost_intelligence.manufacturing_cost_pipeline_builder as pipeline

        source = inspect.getsource(pipeline)

        self.assertNotIn("machine_cost", source)
        self.assertNotIn("cnc_machine_cost", source)

    def test_drilling_cost_already_prices_machining_operations(self):
        from cost_intelligence.manufacturing_cost_calculator import (
            ManufacturingCostCalculator,
        )
        from cost_intelligence.manufacturing_cost_context import (
            ManufacturingCostContext,
        )

        context = ManufacturingCostContext(
            total_drilling_operations=10,
            machining_operations_by_type={"DRILL": 10},
        )
        pricing_catalog = {
            "MACHINING_DRILL": {
                "price_per_operation": 1.5,
            },
        }

        report = ManufacturingCostCalculator().calculate(
            context,
            pricing_catalog=pricing_catalog,
        )

        self.assertEqual(report.drilling_cost, 15.0)

    def test_current_architecture_should_not_add_cnc_machine_cost_blindly(self):
        """
        Protects against double-counting:
        drilling_cost already prices machining operations,
        while cnc machine cost would likely price machine time.
        """

        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )

        names = [field.name for field in fields(ManufacturingCostReport)]

        self.assertIn("drilling_cost", names)
        self.assertNotIn("cnc_machine_cost", names)


if __name__ == "__main__":
    unittest.main()
