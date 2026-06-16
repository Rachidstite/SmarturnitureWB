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

    def test_existing_callers_still_work_without_optional_reports(self):
        report = self.builder.build(*self._inputs())

        self.assertEqual(report.capacity_status, "AVAILABLE")
        self.assertEqual(report.schedule_risk_level, "LOW")
        self.assertEqual(report.workload_status, "AVAILABLE")
        self.assertEqual(report.complexity_level, "LOW")

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

    def test_overloaded_capacity_requires_review(self):
        report = self.builder.build(
            *self._inputs(),
            capacity_report=self._capacity_report(
                capacity_status="OVERLOADED",
                warnings=["Capacity warning"],
            ),
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_high_schedule_risk_requires_review(self):
        report = self.builder.build(
            *self._inputs(),
            production_schedule_report=self._schedule_report(
                schedule_risk_level="HIGH",
                warnings=["Schedule warning"],
            ),
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_overloaded_workload_requires_review(self):
        report = self.builder.build(
            *self._inputs(),
            factory_workload_report=self._workload_report(
                factory_workload_status="OVERLOADED",
                warnings=["Workload warning"],
            ),
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_high_complexity_requires_review(self):
        report = self.builder.build(
            *self._inputs(),
            manufacturing_complexity_report=self._complexity_report(
                complexity_level="HIGH",
                warnings=["Complexity warning"],
                recommendations=["Complexity recommendation"],
            ),
        )

        self.assertEqual(report.decision_status, "REVIEW_REQUIRED")

    def test_builder_aggregates_new_warnings_in_order(self):
        report = self.builder.build(
            *self._inputs(),
            capacity_report=self._capacity_report(
                capacity_status="OVERLOADED",
                warnings=["Capacity warning"],
            ),
            production_schedule_report=self._schedule_report(
                schedule_risk_level="HIGH",
                warnings=["Schedule warning"],
            ),
            factory_workload_report=self._workload_report(
                factory_workload_status="OVERLOADED",
                warnings=["Workload warning"],
            ),
            manufacturing_complexity_report=self._complexity_report(
                complexity_level="HIGH",
                warnings=["Complexity warning"],
                recommendations=["Complexity recommendation"],
            ),
        )

        self.assertEqual(
            report.warnings,
            [
                "Readiness warning",
                "Cost warning",
                "Waste warning",
                "Nesting warning",
                "Capacity warning",
                "Schedule warning",
                "Workload warning",
                "Complexity warning",
            ],
        )

    def test_complexity_recommendations_are_included_without_mutation(self):
        complexity_report = self._complexity_report(
            complexity_level="HIGH",
            warnings=["Complexity warning"],
            recommendations=["Complexity recommendation"],
        )

        report = self.builder.build(
            *self._inputs(),
            manufacturing_complexity_report=complexity_report,
        )

        self.assertEqual(
            report.recommendations,
            [
                "Readiness recommendation",
                "Waste recommendation",
                "Nesting recommendation",
                "Quotation recommendation",
                "Complexity recommendation",
            ],
        )
        self.assertEqual(
            complexity_report.recommendations,
            ["Complexity recommendation"],
        )

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
    def _capacity_report(**values):
        from manufacturing.manufacturing_capacity_report import (
            ManufacturingCapacityReport,
        )

        return ManufacturingCapacityReport(**values)

    @staticmethod
    def _schedule_report(**values):
        from manufacturing.production_schedule_report import (
            ProductionScheduleReport,
        )

        return ProductionScheduleReport(**values)

    @staticmethod
    def _workload_report(**values):
        from manufacturing.factory_workload_report import (
            FactoryWorkloadReport,
        )

        return FactoryWorkloadReport(**values)

    @staticmethod
    def _complexity_report(**values):
        from manufacturing.manufacturing_complexity_report import (
            ManufacturingComplexityReport,
        )

        return ManufacturingComplexityReport(**values)


if __name__ == "__main__":
    unittest.main()
