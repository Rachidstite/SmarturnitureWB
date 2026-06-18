import unittest
from types import SimpleNamespace


class TestHardwareCostIntegrityContract(unittest.TestCase):

    FOCUS_SKUS = (
        "CONFIRMAT_50_V1",
        "SHELF_PIN_5MM",
        "DRAWER_SLIDE_SOFTCLOSE_450",
        "DRAWER_SLIDE_STANDARD_450",
        "HANDLE_128_BLACK",
    )

    def test_default_pricing_catalog_contains_all_manufacturing_cost_skus(self):
        from cost_intelligence.default_catalog_service import (
            DefaultCatalogService,
        )

        catalog = DefaultCatalogService().load_default_catalog()

        missing = [
            sku
            for sku in self.FOCUS_SKUS
            if catalog.get(sku) is None
        ]

        self.assertEqual(missing, [])

    def test_handle_128_black_flows_from_report_to_cost_quotation_and_profitability(self):
        from cost_intelligence.hardware_report_cost_service import (
            HardwareReportCostService,
        )
        from cost_intelligence.profitability_calculator import (
            ProfitabilityCalculator,
        )
        from cost_intelligence.project_cost_calculator import ProjectCostCalculator
        from cost_intelligence.quotation_calculator import QuotationCalculator
        from exports.hardware_report import HardwareReportEngine

        project = SimpleNamespace(
            placements=[
                SimpleNamespace(hardware_intent="INTENT_HANDLE"),
            ],
        )
        context = SimpleNamespace(
            hardware_profile={
                "INTENT_HANDLE": "HANDLE_128_BLACK",
            },
        )
        pricing_catalog = {
            "HANDLE_128_BLACK": {"unit_price": 6.0},
        }

        report = HardwareReportEngine.generate_from_project(project, context)
        hardware_cost = HardwareReportCostService.estimate_from_project(
            project,
            context,
            pricing_catalog=pricing_catalog,
        )
        cost_report = ProjectCostCalculator().estimate(
            project=project,
            context=context,
            pricing_catalog=pricing_catalog,
        )
        quotation = QuotationCalculator(markup_rate=0.20).build(cost_report)
        profitability = ProfitabilityCalculator().build(quotation)

        self.assertEqual(report.hardware_items.get("HANDLE"), 1)
        self.assertEqual(hardware_cost.hardware_cost, 6.0)
        self.assertEqual(cost_report.hardware_cost, 6.0)
        self.assertEqual(quotation.production_cost, 6.0)
        self.assertEqual(quotation.selling_price, 7.2)
        self.assertAlmostEqual(profitability.gross_profit, 1.2)

    def test_drawer_slide_standard_profile_override_preserves_sku_through_cost_path(self):
        from cost_intelligence.profitability_calculator import (
            ProfitabilityCalculator,
        )
        from cost_intelligence.project_cost_calculator import ProjectCostCalculator
        from cost_intelligence.quotation_calculator import QuotationCalculator

        project = SimpleNamespace(
            placements=[
                SimpleNamespace(hardware_intent="INTENT_DRAWER_SLIDE"),
            ],
        )
        context = SimpleNamespace(
            hardware_profile={
                "INTENT_DRAWER_SLIDE": "DRAWER_SLIDE_STANDARD_450",
            },
        )
        pricing_catalog = {
            "DRAWER_SLIDE_STANDARD_450": {"unit_price": 20.0},
            "DRAWER_SLIDE_SOFTCLOSE_450": {"unit_price": 30.0},
        }

        cost_report = ProjectCostCalculator().estimate(
            project=project,
            context=context,
            pricing_catalog=pricing_catalog,
        )
        quotation = QuotationCalculator(markup_rate=0.20).build(cost_report)
        profitability = ProfitabilityCalculator().build(quotation)

        self.assertEqual(cost_report.hardware_cost, 20.0)
        self.assertEqual(quotation.production_cost, 20.0)
        self.assertEqual(quotation.selling_price, 24.0)
        self.assertEqual(profitability.production_cost, 20.0)
        self.assertAlmostEqual(profitability.gross_profit, 4.0)


if __name__ == "__main__":
    unittest.main()
