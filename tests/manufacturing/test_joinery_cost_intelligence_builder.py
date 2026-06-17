import unittest


class TestJoineryCostIntelligenceBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.joinery_cost_intelligence_builder import (
            JoineryCostIntelligenceBuilder,
        )

        self.builder = JoineryCostIntelligenceBuilder(
            minifix_unit_cost=1.5,
            hinge_unit_cost=6.0,
            drawer_slide_unit_cost=20.0,
            handle_unit_cost=6.0,
        )

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_calculates_costs_from_joinery_counts(self):
        from manufacturing.joinery_intelligence_report import (
            JoineryIntelligenceReport,
        )

        report = self.builder.build(
            JoineryIntelligenceReport(
                total_minifix=4,
                total_hinges=8,
                total_drawer_slides=2,
                total_handles=4,
            )
        )

        self.assertEqual(report.minifix_cost, 6.0)
        self.assertEqual(report.hinge_cost, 48.0)
        self.assertEqual(report.drawer_slide_cost, 40.0)
        self.assertEqual(report.handle_cost, 24.0)
        self.assertEqual(report.total_joinery_cost, 118.0)
        self.assertEqual(
            report.cost_breakdown["minifix"],
            {"count": 4, "unit_cost": 1.5, "cost": 6.0},
        )
        self.assertEqual(
            report.cost_breakdown["hinge"],
            {"count": 8, "unit_cost": 6.0, "cost": 48.0},
        )

    def test_builder_supports_pricing_catalog_object(self):
        from manufacturing.joinery_intelligence_report import (
            JoineryIntelligenceReport,
        )

        pricing_catalog = {
            "MINIFIX_15_V1": {"unit_price": 1.5},
            "HINGE_BLUM_110_V1": {"unit_price": 6.0},
            "DRAWER_SLIDE_SOFTCLOSE_450": {"unit_price": 20.0},
            "HANDLE_128_BLACK": {"unit_price": 6.0},
        }

        from manufacturing.joinery_cost_intelligence_builder import (
            JoineryCostIntelligenceBuilder,
        )

        report = JoineryCostIntelligenceBuilder(
            pricing_catalog=pricing_catalog
        ).build(
            JoineryIntelligenceReport(
                total_minifix=1,
                total_hinges=1,
                total_drawer_slides=1,
                total_handles=1,
            )
        )

        self.assertEqual(report.total_joinery_cost, 33.5)

    def test_builder_does_not_mutate_inputs(self):
        from manufacturing.joinery_intelligence_report import (
            JoineryIntelligenceReport,
        )

        input_report = JoineryIntelligenceReport(
            total_minifix=4,
            total_hinges=8,
            total_drawer_slides=2,
            total_handles=4,
        )
        snapshot = dict(input_report.__dict__)

        self.builder.build(input_report)

        self.assertEqual(input_report.__dict__, snapshot)


if __name__ == "__main__":
    unittest.main()
