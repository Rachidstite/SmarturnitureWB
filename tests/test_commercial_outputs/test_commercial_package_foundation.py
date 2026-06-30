import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestCommercialPackageReportContract(unittest.TestCase):
    """CommercialPackageReport is a passive dataclass — no logic, stable fields."""

    def test_report_is_dataclass(self):
        from commercial_outputs.commercial_package_report import CommercialPackageReport

        self.assertTrue(is_dataclass(CommercialPackageReport))

    def test_report_field_inventory_is_stable(self):
        from commercial_outputs.commercial_package_report import CommercialPackageReport

        self.assertEqual(
            [field.name for field in fields(CommercialPackageReport)],
            [
                "cost_report",
                "estimated_price",
                "margin_amount",
                "margin_percent",
                "warnings",
                "source",
            ],
        )

    def test_report_safe_defaults(self):
        from commercial_outputs.commercial_package_report import CommercialPackageReport

        report = CommercialPackageReport()

        self.assertIsNone(report.cost_report)
        self.assertEqual(report.estimated_price, 0.0)
        self.assertEqual(report.margin_amount, 0.0)
        self.assertEqual(report.margin_percent, 0.0)
        self.assertEqual(report.warnings, [])
        self.assertEqual(report.source, "")

    def test_warning_defaults_are_independent(self):
        from commercial_outputs.commercial_package_report import CommercialPackageReport

        r1 = CommercialPackageReport()
        r2 = CommercialPackageReport()
        self.assertIsNot(r1.warnings, r2.warnings)


class TestCommercialPackageBuilderFoundation(unittest.TestCase):
    """CommercialPackageBuilder reads CostPackageReport only — no pricing policy."""

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _cost_report(total_cost=0.0, warnings=None):
        from cost_intelligence.cost_package_report import CostPackageReport

        return CostPackageReport(
            material_cost_total=0.0,
            hardware_cost_total=0.0,
            machining_cost_total=0.0,
            assembly_cost_total=0.0,
            total_cost=total_cost,
            warnings=warnings or [],
            source="CostPackageBuilder",
        )

    def _build(self, cost_report):
        from commercial_outputs.commercial_package_builder import CommercialPackageBuilder

        return CommercialPackageBuilder().build(cost_report)

    # -- 2  Empty cost report -----------------------------------------------

    def test_empty_cost_report_produces_zero_price_and_margin(self):
        cost_report = self._cost_report(total_cost=0.0)
        commercial = self._build(cost_report)

        self.assertIs(commercial.cost_report, cost_report)
        self.assertEqual(commercial.estimated_price, 0.0)
        self.assertEqual(commercial.margin_amount, 0.0)
        self.assertEqual(commercial.margin_percent, 0.0)

    # -- 3  Missing pricing policy ------------------------------------------

    def test_no_pricing_policy_produces_warning(self):
        from commercial_outputs.commercial_package_builder import CommercialPackageBuilder

        cost_report = self._cost_report(total_cost=120.0)
        commercial = self._build(cost_report)

        self.assertIn(
            CommercialPackageBuilder.NO_PRICING_POLICY,
            commercial.warnings,
            msg=f"Expected NO_PRICING_POLICY warning, got: {commercial.warnings}",
        )

    # -- 4  Estimated price equals cost (no pricing policy) -----------------

    def test_estimated_price_equals_cost_when_no_pricing_policy(self):
        cost_report = self._cost_report(total_cost=350.75)
        commercial = self._build(cost_report)

        self.assertEqual(commercial.estimated_price, 350.75)

    def test_estimated_price_tracks_nonzero_total_cost(self):
        cost_report = self._cost_report(total_cost=1500.0)
        commercial = self._build(cost_report)

        self.assertEqual(commercial.estimated_price, 1500.0)

    # -- 5  Margin defaults to zero -----------------------------------------

    def test_margin_defaults_to_zero(self):
        cost_report = self._cost_report(total_cost=500.0)
        commercial = self._build(cost_report)

        self.assertEqual(commercial.margin_amount, 0.0)
        self.assertEqual(commercial.margin_percent, 0.0)

    # -- 6  Builder depends only on CostPackageReport -----------------------

    def test_builder_accepts_cost_package_report(self):
        from commercial_outputs.commercial_package_builder import CommercialPackageBuilder
        from cost_intelligence.cost_package_report import CostPackageReport

        commercial = CommercialPackageBuilder().build(CostPackageReport())
        self.assertIsNotNone(commercial)
        self.assertIsInstance(commercial, object)

    def test_builder_returns_commercial_package_report(self):
        from commercial_outputs.commercial_package_report import CommercialPackageReport

        commercial = self._build(self._cost_report())
        self.assertIsInstance(commercial, CommercialPackageReport)

    def test_builder_imports_only_cost_report(self):
        from commercial_outputs import commercial_package_builder as module

        with open(module.__file__) as f:
            lines = f.readlines()
        import_lines = [
            l
            for l in lines
            if l.strip().startswith("import") or l.strip().startswith("from")
        ]

        forbidden = [
            "FactoryReleasePackage",
            "ManufacturingDecision",
            "GeometryEngine",
            "SceneGraph",
            "HardwareCostBuilder",
            "HardwareBomReport",
            "ManufacturingProductionPackage",
        ]
        for line in import_lines:
            for token in forbidden:
                self.assertNotIn(
                    token,
                    line,
                    msg=f"Builder must not import '{token}' (found in: {line.strip()})",
                )

    def test_builder_has_no_manufacturing_or_engine_references(self):
        from commercial_outputs import commercial_package_builder as module

        with open(module.__file__) as f:
            lines = f.readlines()

        import_lines = [
            l
            for l in lines
            if l.strip().startswith("import") or l.strip().startswith("from")
        ]
        # Should only import CostPackageReport and CommercialPackageReport
        allowed_imports = {
            "commercial_outputs.commercial_package_report",
            "cost_intelligence.cost_package_report",
        }
        for line in import_lines:
            parts = line.strip().split()
            if len(parts) >= 2 and parts[0] in ("import", "from"):
                module_name = parts[1] if parts[0] == "import" else parts[1]
                # Allow relative imports within package
                if not module_name.startswith("commercial_outputs."):
                    self.assertIn(
                        module_name,
                        allowed_imports,
                        msg=f"Unexpected import: {line.strip()}",
                    )

    # -- Additional: source field is set ------------------------------------

    def test_source_field_is_set(self):
        commercial = self._build(self._cost_report())
        self.assertEqual(commercial.source, "CommercialPackageBuilder")

    # -- Additional: cost_report reference is preserved ---------------------

    def test_cost_report_reference_is_preserved(self):
        cost_report = self._cost_report(total_cost=200.0)
        commercial = self._build(cost_report)
        self.assertIs(commercial.cost_report, cost_report)

    # -- Additional: warnings propagate from cost report --------------------

    def test_warnings_inherit_no_pricing_policy(self):
        cost_report = self._cost_report(total_cost=100.0)
        commercial = self._build(cost_report)
        self.assertIn(
            "No commercial pricing policy configured.",
            commercial.warnings,
        )


if __name__ == "__main__":
    unittest.main()
