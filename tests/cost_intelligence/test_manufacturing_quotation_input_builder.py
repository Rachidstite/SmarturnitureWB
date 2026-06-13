import unittest


class TestManufacturingQuotationInputBuilder(unittest.TestCase):

    def test_builder_exists(self):
        from cost_intelligence.manufacturing_quotation_input_builder import (
            ManufacturingQuotationInputBuilder,
        )

        self.assertTrue(callable(ManufacturingQuotationInputBuilder().build))

    def test_build_maps_manufacturing_cost_summary_to_quotation_input(self):
        from cost_intelligence.manufacturing_cost_summary import (
            ManufacturingCostSummary,
        )
        from cost_intelligence.manufacturing_quotation_input import (
            ManufacturingQuotationInput,
        )
        from cost_intelligence.manufacturing_quotation_input_builder import (
            ManufacturingQuotationInputBuilder,
        )

        warnings = ["Manufacturing cost warning"]
        summary = ManufacturingCostSummary(
            total_manufacturing_cost=1250.0,
            warnings=warnings,
        )

        quotation_input = ManufacturingQuotationInputBuilder().build(
            summary,
            markup_rate=0.25,
            currency="EUR",
        )

        self.assertIsInstance(quotation_input, ManufacturingQuotationInput)
        self.assertIs(quotation_input.manufacturing_cost_summary, summary)
        self.assertEqual(quotation_input.base_cost, 1250.0)
        self.assertEqual(quotation_input.markup_rate, 0.25)
        self.assertEqual(quotation_input.currency, "EUR")
        self.assertIs(quotation_input.warnings, warnings)

    def test_build_uses_quotation_defaults(self):
        from cost_intelligence.manufacturing_cost_summary import (
            ManufacturingCostSummary,
        )
        from cost_intelligence.manufacturing_quotation_input_builder import (
            ManufacturingQuotationInputBuilder,
        )

        summary = ManufacturingCostSummary()

        quotation_input = ManufacturingQuotationInputBuilder().build(summary)

        self.assertEqual(quotation_input.base_cost, 0.0)
        self.assertEqual(quotation_input.markup_rate, 0.0)
        self.assertEqual(quotation_input.currency, "MAD")
        self.assertIs(quotation_input.warnings, summary.warnings)


if __name__ == "__main__":
    unittest.main()
