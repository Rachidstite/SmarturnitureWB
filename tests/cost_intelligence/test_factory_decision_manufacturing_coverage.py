import unittest


class TestFactoryDecisionManufacturingCoverage(unittest.TestCase):

    def setUp(self):
        from cost_intelligence.factory_decision_builder import (
            FactoryDecisionBuilder,
        )

        self.builder = FactoryDecisionBuilder()

    def test_drawer_blocked_decision_forces_factory_blocked(self):
        report = self.builder.build(
            *self._inputs(),
            manufacturing_decision_reports=[
                self._drawer_decision_report(
                    decision_status="BLOCKED",
                    is_blocked=True,
                    blocking_reason="Drawer clearance too tight",
                    warning_reason="Drawer warning",
                    recommended_fix="Review drawer manufacturability before production",
                )
            ],
        )

        self.assertEqual(report.decision_status, "BLOCKED")

    def test_drawer_review_required_decision_forces_factory_review_when_base_is_approved(self):
        report = self.builder.build(
            *self._inputs(),
            manufacturing_decision_reports=[
                self._drawer_decision_report(
                    decision_status="REVIEW_REQUIRED",
                    requires_review=True,
                    warning_reason="Drawer requires review",
                    recommended_fix="Review drawer manufacturing readiness",
                )
            ],
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_approved_drawer_decision_does_not_change_approved_factory_decision(self):
        report = self.builder.build(
            *self._inputs(),
            manufacturing_decision_reports=[
                self._drawer_decision_report(
                    decision_status="APPROVED",
                    is_manufacturable=True,
                )
            ],
        )

        self.assertEqual(report.decision_status, "APPROVED")

    def test_multiple_approved_manufacturing_decisions_preserve_factory_decision(self):
        report = self.builder.build(
            *self._inputs(),
            manufacturing_decision_reports=[
                self._back_panel_decision_report(
                    decision_status="APPROVED",
                    is_manufacturable=True,
                ),
                self._minifix_decision_report(
                    decision_status="APPROVED",
                    is_manufacturable=True,
                ),
                self._confirmat_decision_report(
                    decision_status="APPROVED",
                    is_manufacturable=True,
                ),
                self._drawer_decision_report(
                    decision_status="APPROVED",
                    is_manufacturable=True,
                ),
            ],
        )

        self.assertEqual(report.decision_status, "APPROVED")

    def test_any_blocked_manufacturing_decision_overrides_approved_factory_decision(self):
        report = self.builder.build(
            *self._inputs(),
            manufacturing_decision_reports=[
                self._back_panel_decision_report(
                    decision_status="APPROVED",
                    is_manufacturable=True,
                ),
                self._minifix_decision_report(
                    decision_status="BLOCKED",
                    is_blocked=True,
                    blocking_reason="Minifix blocked",
                ),
                self._drawer_decision_report(
                    decision_status="APPROVED",
                    is_manufacturable=True,
                ),
            ],
        )

        self.assertEqual(report.decision_status, "BLOCKED")

    def test_blocking_reason_propagates_into_factory_blocking_issues(self):
        report = self.builder.build(
            *self._inputs(),
            manufacturing_decision_reports=[
                self._drawer_decision_report(
                    decision_status="BLOCKED",
                    is_blocked=True,
                    blocking_reason="Drawer clearance too tight",
                )
            ],
        )

        self.assertIn("Drawer clearance too tight", report.blocking_issues)

    def test_warning_reason_propagates_into_factory_warnings(self):
        report = self.builder.build(
            *self._inputs(),
            manufacturing_decision_reports=[
                self._confirmat_decision_report(
                    decision_status="REVIEW_REQUIRED",
                    requires_review=True,
                    warning_reason="Confirmat warning",
                )
            ],
        )

        self.assertIn("Confirmat warning", report.warnings)

    def test_recommended_fix_propagates_into_factory_recommendations(self):
        report = self.builder.build(
            *self._inputs(),
            manufacturing_decision_reports=[
                self._back_panel_decision_report(
                    decision_status="REVIEW_REQUIRED",
                    requires_review=True,
                    recommended_fix="Review back panel manufacturing",
                )
            ],
        )

        self.assertIn("Review back panel manufacturing", report.recommendations)

    def test_inputs_are_not_mutated(self):
        inputs = self._inputs()
        manufacturing_decision_reports = [
            self._drawer_decision_report(
                decision_status="BLOCKED",
                is_blocked=True,
                blocking_reason="Drawer blocked",
                warning_reason="Drawer warning",
                recommended_fix="Drawer fix",
            ),
            self._confirmat_decision_report(
                decision_status="APPROVED",
                is_manufacturable=True,
            ),
        ]

        original_inputs = [self._snapshot(report) for report in inputs]
        original_manufacturing = [
            self._snapshot(report) for report in manufacturing_decision_reports
        ]

        self.builder.build(
            *inputs,
            manufacturing_decision_reports=manufacturing_decision_reports,
        )

        self.assertEqual(
            [self._snapshot(report) for report in inputs],
            original_inputs,
        )
        self.assertEqual(
            [self._snapshot(report) for report in manufacturing_decision_reports],
            original_manufacturing,
        )

    def test_empty_manufacturing_decision_reports_preserves_existing_behavior(self):
        report = self.builder.build(
            *self._inputs(),
            manufacturing_decision_reports=[],
        )

        self.assertEqual(report.decision_status, "APPROVED")
        self.assertEqual(report.blocking_issues, ["Readiness blocker"])
        self.assertEqual(
            report.warnings,
            [
                "Readiness warning",
                "Cost warning",
                "Waste warning",
                "Nesting warning",
            ],
        )
        self.assertEqual(
            report.recommendations,
            [
                "Readiness recommendation",
                "Waste recommendation",
                "Nesting recommendation",
                "Quotation recommendation",
            ],
        )

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }

    @staticmethod
    def _inputs(
        readiness_status="READY",
        manufacturing_ready=True,
        profitability_ok=True,
        cost_risk_level="LOW",
        waste_risk_level="LOW",
        nesting_risk_level="LOW",
        quotation_risk_level="LOW",
        margin_status="HEALTHY_MARGIN",
        waste_recommendation="Waste recommendation",
        nesting_recommendation="Nesting recommendation",
    ):
        from cost_intelligence.manufacturing_cost_summary import (
            ManufacturingCostSummary,
        )
        from cost_intelligence.nesting_intelligence_report import (
            NestingIntelligenceReport,
        )
        from cost_intelligence.production_readiness_report import (
            ProductionReadinessReport,
        )
        from cost_intelligence.quotation_intelligence_report import (
            QuotationIntelligenceReport,
        )
        from cost_intelligence.waste_intelligence_report import (
            WasteIntelligenceReport,
        )

        return (
            ProductionReadinessReport(
                status=readiness_status,
                manufacturing_ready=manufacturing_ready,
                profitability_ok=profitability_ok,
                blocking_issues=["Readiness blocker"],
                warnings=["Readiness warning"],
                recommendations=["Readiness recommendation"],
            ),
            ManufacturingCostSummary(
                risk_level=cost_risk_level,
                warnings=["Cost warning"],
            ),
            WasteIntelligenceReport(
                risk_level=waste_risk_level,
                recommendation=waste_recommendation,
                warnings=["Waste warning"],
            ),
            NestingIntelligenceReport(
                risk_level=nesting_risk_level,
                recommendation=nesting_recommendation,
                warnings=["Nesting warning"],
            ),
            QuotationIntelligenceReport(
                risk_level=quotation_risk_level,
                margin_status=margin_status,
                recommendations=["Quotation recommendation"],
            ),
        )

    @staticmethod
    def _back_panel_decision_report(**kwargs):
        from manufacturing.back_panel_decision_report import (
            BackPanelDecisionReport,
        )

        return BackPanelDecisionReport(**kwargs)

    @staticmethod
    def _minifix_decision_report(**kwargs):
        from manufacturing.minifix_decision_report import MinifixDecisionReport

        return MinifixDecisionReport(**kwargs)

    @staticmethod
    def _confirmat_decision_report(**kwargs):
        from manufacturing.confirmat_decision_report import (
            ConfirmatDecisionReport,
        )

        return ConfirmatDecisionReport(**kwargs)

    @staticmethod
    def _drawer_decision_report(**kwargs):
        from manufacturing.drawer_decision_report import DrawerDecisionReport

        return DrawerDecisionReport(**kwargs)


if __name__ == "__main__":
    unittest.main()
