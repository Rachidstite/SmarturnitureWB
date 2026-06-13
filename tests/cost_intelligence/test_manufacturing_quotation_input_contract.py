import unittest
from dataclasses import fields, is_dataclass


class TestManufacturingQuotationInputContract(unittest.TestCase):

    def test_contract_exists_and_is_dataclass(self):
        from cost_intelligence.manufacturing_quotation_input import (
            ManufacturingQuotationInput,
        )

        self.assertTrue(is_dataclass(ManufacturingQuotationInput))

    def test_contract_has_required_fields(self):
        from cost_intelligence.manufacturing_quotation_input import (
            ManufacturingQuotationInput,
        )

        self.assertEqual(
            [field.name for field in fields(ManufacturingQuotationInput)],
            [
                "manufacturing_cost_summary",
                "base_cost",
                "markup_rate",
                "currency",
                "warnings",
            ],
        )

    def test_contract_defaults(self):
        from cost_intelligence.manufacturing_quotation_input import (
            ManufacturingQuotationInput,
        )

        quotation_input = ManufacturingQuotationInput()

        self.assertIsNone(quotation_input.manufacturing_cost_summary)
        self.assertEqual(quotation_input.base_cost, 0.0)
        self.assertEqual(quotation_input.markup_rate, 0.0)
        self.assertEqual(quotation_input.currency, "MAD")
        self.assertEqual(quotation_input.warnings, [])

    def test_warning_defaults_are_independent(self):
        from cost_intelligence.manufacturing_quotation_input import (
            ManufacturingQuotationInput,
        )

        first_input = ManufacturingQuotationInput()
        second_input = ManufacturingQuotationInput()

        self.assertIsNot(first_input.warnings, second_input.warnings)

    def test_contract_accepts_manufacturing_cost_summary(self):
        from cost_intelligence.manufacturing_cost_summary import (
            ManufacturingCostSummary,
        )
        from cost_intelligence.manufacturing_quotation_input import (
            ManufacturingQuotationInput,
        )

        summary = ManufacturingCostSummary()
        quotation_input = ManufacturingQuotationInput(
            manufacturing_cost_summary=summary,
        )

        self.assertIs(quotation_input.manufacturing_cost_summary, summary)


if __name__ == "__main__":
    unittest.main()
