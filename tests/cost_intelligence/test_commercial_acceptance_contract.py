import unittest
from dataclasses import fields, is_dataclass


class TestCommercialAcceptanceContract(unittest.TestCase):

    def test_contract_is_dataclass(self):
        from cost_intelligence.commercial_acceptance_contract import (
            CommercialAcceptanceContract,
        )

        self.assertTrue(is_dataclass(CommercialAcceptanceContract))

    def test_contract_has_stable_field_order(self):
        from cost_intelligence.commercial_acceptance_contract import (
            CommercialAcceptanceContract,
        )

        self.assertEqual(
            [field.name for field in fields(CommercialAcceptanceContract)],
            [
                "acceptance_status",
                "quote_reference",
                "customer_reference",
                "quote_revision_reference",
                "accepted_at",
                "approved_at",
                "confirmed_at",
                "accepted_by",
                "approved_by",
                "confirmed_by",
            ],
        )

    def test_contract_has_safe_defaults(self):
        from cost_intelligence.commercial_acceptance_contract import (
            CommercialAcceptanceContract,
        )

        contract = CommercialAcceptanceContract()

        self.assertEqual(contract.acceptance_status, "DRAFT")
        self.assertEqual(contract.quote_reference, "")
        self.assertEqual(contract.customer_reference, "")
        self.assertEqual(contract.quote_revision_reference, "")
        self.assertEqual(contract.accepted_at, "")
        self.assertEqual(contract.approved_at, "")
        self.assertEqual(contract.confirmed_at, "")
        self.assertEqual(contract.accepted_by, "")
        self.assertEqual(contract.approved_by, "")
        self.assertEqual(contract.confirmed_by, "")

    def test_quote_accepted_behavior(self):
        from cost_intelligence.commercial_acceptance_contract import (
            CommercialAcceptanceContract,
        )

        self.assertFalse(
            CommercialAcceptanceContract(acceptance_status="DRAFT").quote_accepted
        )
        self.assertTrue(
            CommercialAcceptanceContract(
                acceptance_status="ACCEPTED"
            ).quote_accepted
        )
        self.assertTrue(
            CommercialAcceptanceContract(
                acceptance_status="APPROVED"
            ).quote_accepted
        )
        self.assertTrue(
            CommercialAcceptanceContract(
                acceptance_status="CONFIRMED"
            ).quote_accepted
        )

    def test_customer_approved_behavior(self):
        from cost_intelligence.commercial_acceptance_contract import (
            CommercialAcceptanceContract,
        )

        self.assertFalse(
            CommercialAcceptanceContract(acceptance_status="DRAFT").customer_approved
        )
        self.assertFalse(
            CommercialAcceptanceContract(
                acceptance_status="ACCEPTED"
            ).customer_approved
        )
        self.assertTrue(
            CommercialAcceptanceContract(
                acceptance_status="APPROVED"
            ).customer_approved
        )
        self.assertTrue(
            CommercialAcceptanceContract(
                acceptance_status="CONFIRMED"
            ).customer_approved
        )

    def test_confirmed_order_behavior(self):
        from cost_intelligence.commercial_acceptance_contract import (
            CommercialAcceptanceContract,
        )

        self.assertFalse(
            CommercialAcceptanceContract(acceptance_status="DRAFT").confirmed_order
        )
        self.assertFalse(
            CommercialAcceptanceContract(
                acceptance_status="ACCEPTED"
            ).confirmed_order
        )
        self.assertFalse(
            CommercialAcceptanceContract(
                acceptance_status="APPROVED"
            ).confirmed_order
        )
        self.assertTrue(
            CommercialAcceptanceContract(
                acceptance_status="CONFIRMED"
            ).confirmed_order
        )

    def test_contract_contains_no_pricing_manufacturing_or_governance_fields(self):
        from cost_intelligence.commercial_acceptance_contract import (
            CommercialAcceptanceContract,
        )

        names = [field.name for field in fields(CommercialAcceptanceContract)]

        for forbidden in (
            "price",
            "selling_price",
            "markup_rate",
            "markup_amount",
            "discount_amount",
            "tax_amount",
            "production_cost",
            "total_cost",
            "waste_cost",
            "manufacturing",
            "governance",
            "decision",
            "capacity",
            "schedule",
        ):
            self.assertNotIn(forbidden, names)


if __name__ == "__main__":
    unittest.main()
