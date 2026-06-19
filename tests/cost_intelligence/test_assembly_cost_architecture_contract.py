import inspect
import unittest
from dataclasses import fields


class TestAssemblyCostArchitectureContract(unittest.TestCase):

    def test_assembly_time_exists_in_duration_report(self):
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )

        names = [field.name for field in fields(ManufacturingDurationReport)]

        self.assertIn("estimated_assembly_minutes", names)

    def test_assembly_labor_cost_exists_but_is_separate(self):
        from manufacturing.labor_cost_report import LaborCostReport

        names = [field.name for field in fields(LaborCostReport)]

        self.assertIn("assembly_labor_cost", names)

    def test_assembly_intelligence_exists_but_is_not_cost_source(self):
        from manufacturing.assembly_intelligence_report import (
            AssemblyIntelligenceReport,
        )

        names = [field.name for field in fields(AssemblyIntelligenceReport)]

        self.assertIn("assembly_time_minutes", names)
        self.assertIn("assembly_complexity", names)
        self.assertIn("required_installers", names)

    def test_manufacturing_cost_report_does_not_yet_expose_assembly_cost(self):
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )

        names = [field.name for field in fields(ManufacturingCostReport)]

        self.assertNotIn("assembly_cost", names)

    def test_manufacturing_cost_pipeline_does_not_consume_assembly_labor_yet(self):
        import cost_intelligence.manufacturing_cost_pipeline_builder as pipeline

        source = inspect.getsource(pipeline)

        self.assertNotIn("LaborCostBuilder", source)
        self.assertNotIn("assembly_labor_cost", source)

    def test_quotation_breakdown_does_not_yet_expose_assembly_cost(self):
        from cost_intelligence.quotation_breakdown_report import (
            QuotationBreakdownReport,
        )

        names = [field.name for field in fields(QuotationBreakdownReport)]

        self.assertNotIn("assembly_cost", names)

    def test_panel_handling_cost_is_separate_from_assembly_cost(self):
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )

        names = [field.name for field in fields(ManufacturingCostReport)]

        self.assertIn("panel_handling_cost", names)
        self.assertNotIn("assembly_cost", names)


if __name__ == "__main__":
    unittest.main()
