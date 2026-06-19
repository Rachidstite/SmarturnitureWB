import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestBackPanelFixingStrategyContract(unittest.TestCase):

    def test_strategy_enum_exists(self):
        from manufacturing.back_panel_fixing_strategy import (
            BackPanelFixingStrategy,
        )

        self.assertTrue(hasattr(BackPanelFixingStrategy, "GROOVE"))
        self.assertTrue(hasattr(BackPanelFixingStrategy, "SCREWED"))
        self.assertTrue(hasattr(BackPanelFixingStrategy, "STAPLED"))

    def test_three_strategies_exist(self):
        from manufacturing.back_panel_fixing_strategy import (
            BackPanelFixingStrategy,
        )

        self.assertEqual(
            [strategy.value for strategy in BackPanelFixingStrategy],
            ["GROOVE", "SCREWED", "STAPLED"],
        )

    def test_report_contract_exists(self):
        from manufacturing.back_panel_fixing_report import (
            BackPanelFixingReport,
        )

        self.assertTrue(is_dataclass(BackPanelFixingReport))

    def test_report_fields_and_defaults(self):
        from manufacturing.back_panel_fixing_report import (
            BackPanelFixingReport,
        )
        from manufacturing.back_panel_fixing_strategy import (
            BackPanelFixingStrategy,
        )

        self.assertEqual(
            [field.name for field in fields(BackPanelFixingReport)],
            [
                "strategy",
                "requires_holes",
                "requires_groove",
                "requires_fasteners",
                "structural_rating",
                "manufacturing_notes",
            ],
        )

        report = BackPanelFixingReport()

        self.assertEqual(report.strategy, BackPanelFixingStrategy.GROOVE)
        self.assertFalse(report.requires_holes)
        self.assertTrue(report.requires_groove)
        self.assertFalse(report.requires_fasteners)
        self.assertEqual(report.structural_rating, 0.0)
        self.assertEqual(report.manufacturing_notes, "")

    def test_contract_rules(self):
        from manufacturing.back_panel_fixing_report import (
            BackPanelFixingReport,
        )
        from manufacturing.back_panel_fixing_strategy import (
            BackPanelFixingStrategy,
        )

        scenarios = [
            (
                BackPanelFixingStrategy.GROOVE,
                BackPanelFixingReport(
                    strategy=BackPanelFixingStrategy.GROOVE,
                    requires_holes=False,
                    requires_groove=True,
                    requires_fasteners=False,
                ),
                (False, True, False),
            ),
            (
                BackPanelFixingStrategy.SCREWED,
                BackPanelFixingReport(
                    strategy=BackPanelFixingStrategy.SCREWED,
                    requires_holes=True,
                    requires_groove=False,
                    requires_fasteners=True,
                ),
                (True, False, True),
            ),
            (
                BackPanelFixingStrategy.STAPLED,
                BackPanelFixingReport(
                    strategy=BackPanelFixingStrategy.STAPLED,
                    requires_holes=False,
                    requires_groove=False,
                    requires_fasteners=True,
                ),
                (False, False, True),
            ),
        ]

        for strategy, report, expected in scenarios:
            with self.subTest(strategy=strategy.value):
                self.assertEqual(
                    (report.requires_holes, report.requires_groove, report.requires_fasteners),
                    expected,
                )

    def test_no_manufacturing_behavior_changes(self):
        from domain.back_panel_engine import BackPanelEngine, BackPanelRule

        rule = BackPanelRule()

        self.assertEqual(BackPanelEngine.groove_width(rule), rule.thickness + rule.groove_clearance)
        self.assertEqual(BackPanelEngine.insertion_depth(rule), rule.groove_depth)
        self.assertEqual(BackPanelEngine.offset(rule), rule.groove_offset)

    def test_no_runtime_behavior_imports(self):
        import manufacturing.back_panel_fixing_report as report_module
        import manufacturing.back_panel_fixing_strategy as strategy_module

        report_source = inspect.getsource(report_module)
        strategy_source = inspect.getsource(strategy_module)

        self.assertNotIn("FactoryDecisionBuilder", report_source)
        self.assertNotIn("FactoryDecisionBuilder", strategy_source)
        self.assertNotIn("ProductionReadinessBuilder", report_source)
        self.assertNotIn("ProductionReadinessBuilder", strategy_source)
        self.assertNotIn("FactoryDecisionIntelligenceBuilder", report_source)
        self.assertNotIn("FactoryDecisionIntelligenceBuilder", strategy_source)


if __name__ == "__main__":
    unittest.main()
