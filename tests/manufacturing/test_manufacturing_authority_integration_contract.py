import unittest
from dataclasses import is_dataclass


class TestManufacturingAuthorityIntegrationContract(unittest.TestCase):

    def test_factory_governance_authority_report_can_flow_through_manufacturing_authority_result(self):
        from cost_intelligence.factory_governance_authority_resolver import (
            FactoryGovernanceAuthorityResolver,
        )
        from cost_intelligence.factory_governance_policy_context import (
            FactoryGovernancePolicyContext,
        )
        from manufacturing.manufacturing_authority_result import (
            ManufacturingAuthorityResult,
        )

        context = FactoryGovernancePolicyContext(
            readiness_status="BLOCKED",
            profitability_status="LOW",
            capacity_status="OVERLOADED",
            load_status="HIGH",
            risk_status="HIGH",
        )
        context_snapshot = self._snapshot(context)

        report = FactoryGovernanceAuthorityResolver().resolve(context)
        report_snapshot = self._snapshot(report)

        result = ManufacturingAuthorityResult(
            factory_governance_authority_report=report,
        )

        self.assertTrue(is_dataclass(result))
        self.assertIs(result.factory_governance_authority_report, report)
        self.assertEqual(
            result.factory_governance_authority_report.authority_owner,
            "ProductionReadinessBuilder",
        )
        self.assertEqual(
            result.factory_governance_authority_report.authority_rank,
            1,
        )
        self.assertEqual(
            result.factory_governance_authority_report.winning_signal,
            "READINESS_BLOCKED",
        )
        self.assertIn(
            "LOW_MARGIN",
            result.factory_governance_authority_report.losing_signals,
        )
        self.assertEqual(
            result.factory_governance_authority_report.explanation,
            "ProductionReadinessBuilder wins because it has the highest authority rank.",
        )

        self.assertEqual(self._snapshot(context), context_snapshot)
        self.assertEqual(self._snapshot(report), report_snapshot)
        self.assertFalse(hasattr(ManufacturingAuthorityResult, "build"))
        self.assertFalse(hasattr(ManufacturingAuthorityResult, "calculate"))
        self.assertFalse(hasattr(ManufacturingAuthorityResult, "compute"))
        self.assertFalse(hasattr(ManufacturingAuthorityResult, "manufacture"))

    @staticmethod
    def _snapshot(item):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in item.__dict__.items()
        }


if __name__ == "__main__":
    unittest.main()
