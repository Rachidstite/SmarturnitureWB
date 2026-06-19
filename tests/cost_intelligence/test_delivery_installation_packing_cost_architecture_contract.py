import inspect
import unittest
from dataclasses import fields


class TestDeliveryInstallationPackingCostArchitectureContract(unittest.TestCase):

    def test_delivery_intelligence_exists_but_is_not_cost_source(self):
        from manufacturing.delivery_intelligence_report import (
            DeliveryIntelligenceReport,
        )

        names = [field.name for field in fields(DeliveryIntelligenceReport)]

        self.assertIn("delivery_risk", names)
        self.assertIn("recommendation", names)
        self.assertNotIn("delivery_cost", names)

    def test_installation_risk_exists_but_installation_cost_does_not(self):
        from manufacturing.assembly_intelligence_report import (
            AssemblyIntelligenceReport,
        )

        names = [field.name for field in fields(AssemblyIntelligenceReport)]

        self.assertIn("installation_risk", names)
        self.assertNotIn("installation_cost", names)

    def test_manufacturing_cost_report_does_not_expose_delivery_installation_or_packing_cost(self):
        from cost_intelligence.manufacturing_cost_report import (
            ManufacturingCostReport,
        )

        names = [field.name for field in fields(ManufacturingCostReport)]

        self.assertNotIn("delivery_cost", names)
        self.assertNotIn("installation_cost", names)
        self.assertNotIn("packing_cost", names)

    def test_quotation_breakdown_does_not_expose_delivery_installation_or_packing_cost(self):
        from cost_intelligence.quotation_breakdown_report import (
            QuotationBreakdownReport,
        )

        names = [field.name for field in fields(QuotationBreakdownReport)]

        self.assertNotIn("delivery_cost", names)
        self.assertNotIn("installation_cost", names)
        self.assertNotIn("packing_cost", names)

    def test_manufacturing_cost_pipeline_does_not_consume_delivery_installation_or_packing_cost(self):
        import cost_intelligence.manufacturing_cost_pipeline_builder as pipeline

        source = inspect.getsource(pipeline)

        self.assertNotIn("delivery_cost", source)
        self.assertNotIn("installation_cost", source)
        self.assertNotIn("packing_cost", source)

    def test_delivery_terms_are_risk_intelligence_not_cost_intelligence_today(self):
        import manufacturing.delivery_intelligence_builder as delivery_builder

        source = inspect.getsource(delivery_builder)

        self.assertIn("delivery_risk", source)
        self.assertNotIn("delivery_cost", source)


if __name__ == "__main__":
    unittest.main()
