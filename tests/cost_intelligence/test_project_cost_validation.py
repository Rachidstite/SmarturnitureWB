import unittest
from types import SimpleNamespace


class TestProjectCostValidation(unittest.TestCase):

    def test_authoritative_cost_components_equal_total_cost(self):

        from cost_intelligence.cost_report import CostReport
        from cost_intelligence.project_cost_calculator import (
            ProjectCostCalculator,
        )
        from exports.cutlist_engine import CutListItem

        panel = CutListItem(
            identity="P1",
            width=1000,
            height=500,
            thickness=18,
            material="MDF",
            group="TEST",
            role="SHELF",
            quantity=1,
        )

        nesting_results = {
            "MDF_18MM": [
                SimpleNamespace(
                    waste_ratio=0.30,
                ),
            ],
        }

        hardware_items = [
            {
                "sku": "HINGE_STD",
                "quantity": 4,
            },
        ]

        pricing_catalog = {
            "MDF_18MM": {
                "price_per_sheet": 280,
                "price_per_m2": 100,
                "currency": "MAD",
            },
            "HINGE_STD": {
                "unit_price": 12,
                "currency": "MAD",
            },
        }

        report = ProjectCostCalculator().estimate(
            cutlist_items=[panel],
            nesting_results=nesting_results,
            hardware_items=hardware_items,
            pricing_catalog=pricing_catalog,
        )

        self.assertIsInstance(
            report,
            CostReport,
        )
        self.assertEqual(
            (
                report.sheet_cost
                + report.hardware_cost
            ),
            report.total_cost,
        )
        self.assertGreater(
            report.material_cost,
            0,
        )
        self.assertGreater(
            report.waste_cost,
            0,
        )


if __name__ == "__main__":
    unittest.main()
