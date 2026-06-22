import unittest


class TestFactoryDecisionBuilder(unittest.TestCase):

    def setUp(self):
        from cost_intelligence.factory_decision_builder import (
            FactoryDecisionBuilder,
        )

        self.builder = FactoryDecisionBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_builder_returns_factory_decision_report(self):
        from cost_intelligence.factory_decision_report import FactoryDecisionReport

        report = self.builder.build(*self._inputs())

        self.assertIsInstance(report, FactoryDecisionReport)

    def test_blocked_readiness_has_highest_precedence(self):
        inputs = self._inputs(
            readiness_status="BLOCKED",
            quotation_risk_level="HIGH",
        )

        report = self.builder.build(*inputs)

        self.assertEqual(report.decision_status, "BLOCKED")

    def test_any_high_risk_requires_review(self):
        risk_overrides = [
            {"cost_risk_level": "HIGH"},
            {"waste_risk_level": "HIGH"},
            {"nesting_risk_level": "HIGH"},
            {"quotation_risk_level": "HIGH"},
        ]

        for overrides in risk_overrides:
            with self.subTest(overrides=overrides):
                report = self.builder.build(*self._inputs(**overrides))
                self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_ready_with_warnings_requires_review(self):
        report = self.builder.build(
            *self._inputs(readiness_status="READY_WITH_WARNINGS")
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_ready_without_high_risk_is_approved(self):
        report = self.builder.build(*self._inputs())

        self.assertEqual(report.decision_status, "APPROVED")

    def test_builder_maps_decision_fields(self):
        report = self.builder.build(
            *self._inputs(
                manufacturing_ready=True,
                profitability_ok=True,
                cost_risk_level="MEDIUM",
                waste_risk_level="LOW",
                nesting_risk_level="MEDIUM",
                quotation_risk_level="LOW",
                margin_status="HEALTHY_MARGIN",
            )
        )

        self.assertTrue(report.manufacturing_ready)
        self.assertTrue(report.profitability_ok)
        self.assertEqual(report.cost_risk_level, "MEDIUM")
        self.assertEqual(report.waste_risk_level, "LOW")
        self.assertEqual(report.nesting_risk_level, "MEDIUM")
        self.assertEqual(report.quotation_risk_level, "LOW")
        self.assertEqual(report.margin_status, "HEALTHY_MARGIN")

    def test_builder_aggregates_lists_in_order_into_new_lists(self):
        (
            readiness,
            cost_summary,
            waste,
            nesting,
            quotation,
        ) = self._inputs()

        report = self.builder.build(
            readiness,
            cost_summary,
            waste,
            nesting,
            quotation,
        )

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
        self.assertIsNot(report.blocking_issues, readiness.blocking_issues)
        for warnings in (
            readiness.warnings,
            cost_summary.warnings,
            waste.warnings,
            nesting.warnings,
        ):
            self.assertIsNot(report.warnings, warnings)
        for recommendations in (
            readiness.recommendations,
            quotation.recommendations,
        ):
            self.assertIsNot(report.recommendations, recommendations)

    def test_builder_skips_empty_single_recommendations(self):
        inputs = self._inputs(
            waste_recommendation="",
            nesting_recommendation="",
        )

        report = self.builder.build(*inputs)

        self.assertEqual(
            report.recommendations,
            [
                "Readiness recommendation",
                "Quotation recommendation",
            ],
        )

    def test_builder_does_not_mutate_inputs(self):
        inputs = self._inputs()
        original_values = [
            self._snapshot(report)
            for report in inputs
        ]

        self.builder.build(*inputs)

        self.assertEqual(
            [self._snapshot(report) for report in inputs],
            original_values,
        )

    def test_existing_behavior_remains_unchanged_without_manufacturing_decision_reports(self):
        report = self.builder.build(*self._inputs())

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

    def test_blocked_manufacturing_decision_forces_blocked_status(self):
        report = self.builder.build(
            *self._inputs(),
            manufacturing_decision_reports=[
                self._manufacturing_decision_report(
                    decision_status="BLOCKED",
                    is_blocked=True,
                    blocking_reason="Back panel is blocked",
                    warning_reason="Back panel warning",
                    recommended_fix="Fix the back panel",
                )
            ],
        )

        self.assertEqual(report.decision_status, "BLOCKED")

    def test_review_required_manufacturing_decision_forces_review_when_base_is_approved(self):
        report = self.builder.build(
            *self._inputs(),
            manufacturing_decision_reports=[
                self._manufacturing_decision_report(
                    decision_status="REVIEW_REQUIRED",
                    requires_review=True,
                    blocking_reason="Minifix needs review",
                    warning_reason="Minifix warning",
                    recommended_fix="Review the minifix placement",
                )
            ],
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_blocked_base_decision_remains_blocked(self):
        report = self.builder.build(
            *self._inputs(readiness_status="BLOCKED"),
            manufacturing_decision_reports=[
                self._manufacturing_decision_report(
                    decision_status="REVIEW_REQUIRED",
                    requires_review=True,
                    warning_reason="Confirmat warning",
                    recommended_fix="Review the confirmat decision",
                )
            ],
        )

        self.assertEqual(report.decision_status, "BLOCKED")

    def test_manufacturing_decision_reasons_are_propagated(self):
        report = self.builder.build(
            *self._inputs(),
            manufacturing_decision_reports=[
                self._manufacturing_decision_report(
                    blocking_reason="Back panel blocked",
                    warning_reason="Back panel warning",
                    recommended_fix="Back panel fix",
                ),
                self._manufacturing_decision_report(
                    blocking_reason="Minifix blocked",
                    warning_reason="Minifix warning",
                    recommended_fix="Minifix fix",
                ),
            ],
        )

        self.assertEqual(
            report.blocking_issues,
            [
                "Readiness blocker",
                "Back panel blocked",
                "Minifix blocked",
            ],
        )
        self.assertEqual(
            report.warnings,
            [
                "Readiness warning",
                "Cost warning",
                "Waste warning",
                "Nesting warning",
                "Back panel warning",
                "Minifix warning",
            ],
        )
        self.assertEqual(
            report.recommendations,
            [
                "Readiness recommendation",
                "Waste recommendation",
                "Nesting recommendation",
                "Quotation recommendation",
                "Back panel fix",
                "Minifix fix",
            ],
        )

    def test_builder_does_not_mutate_manufacturing_decision_inputs(self):
        inputs = self._inputs()
        manufacturing_decision_reports = [
            self._manufacturing_decision_report(
                decision_status="BLOCKED",
                is_blocked=True,
                blocking_reason="Back panel blocked",
                warning_reason="Back panel warning",
                recommended_fix="Back panel fix",
            ),
            self._manufacturing_decision_report(
                decision_status="REVIEW_REQUIRED",
                requires_review=True,
                blocking_reason="Minifix blocked",
                warning_reason="Minifix warning",
                recommended_fix="Minifix fix",
            ),
        ]
        original_values = [
            self._snapshot(report)
            for report in manufacturing_decision_reports
        ]

        self.builder.build(
            *inputs,
            manufacturing_decision_reports=manufacturing_decision_reports,
        )

        self.assertEqual(
            [self._snapshot(report) for report in manufacturing_decision_reports],
            original_values,
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
    def _manufacturing_decision_report(
        decision_status="APPROVED",
        is_manufacturable=True,
        is_blocked=False,
        requires_review=False,
        blocking_reason="",
        warning_reason="",
        recommended_fix="",
        factory_visibility_message="",
    ):
        from manufacturing.back_panel_decision_report import (
            BackPanelDecisionReport,
        )

        return BackPanelDecisionReport(
            decision_status=decision_status,
            is_manufacturable=is_manufacturable,
            is_blocked=is_blocked,
            requires_review=requires_review,
            blocking_reason=blocking_reason,
            warning_reason=warning_reason,
            recommended_fix=recommended_fix,
            factory_visibility_message=factory_visibility_message,
        )

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


if __name__ == "__main__":
    unittest.main()
