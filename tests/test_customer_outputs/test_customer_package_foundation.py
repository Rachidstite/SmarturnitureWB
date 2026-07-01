import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestCustomerPackageReportContract(unittest.TestCase):
    def test_report_is_dataclass(self):
        from customer_outputs.customer_package_report import CustomerPackageReport

        self.assertTrue(is_dataclass(CustomerPackageReport))

    def test_report_field_inventory_is_stable(self):
        from customer_outputs.customer_package_report import CustomerPackageReport

        self.assertEqual(
            [field.name for field in fields(CustomerPackageReport)],
            [
                "commercial_report",
                "customer_summary",
                "estimated_price",
                "warnings",
                "source",
            ],
        )

    def test_report_safe_defaults(self):
        from customer_outputs.customer_package_report import CustomerPackageReport

        report = CustomerPackageReport()

        self.assertIsNone(report.commercial_report)
        self.assertEqual(report.customer_summary, "")
        self.assertEqual(report.estimated_price, 0.0)
        self.assertEqual(report.warnings, [])
        self.assertEqual(report.source, "")

    def test_warning_defaults_are_independent(self):
        from customer_outputs.customer_package_report import CustomerPackageReport

        r1 = CustomerPackageReport()
        r2 = CustomerPackageReport()
        self.assertIsNot(r1.warnings, r2.warnings)


class TestCustomerPackageBuilderFoundation(unittest.TestCase):
    @staticmethod
    def _commercial_report(estimated_price=0.0, warnings=None):
        from commercial_outputs.commercial_package_report import CommercialPackageReport

        return CommercialPackageReport(
            cost_report=object(),
            estimated_price=estimated_price,
            margin_amount=0.0,
            margin_percent=0.0,
            warnings=warnings or [],
            source="CommercialPackageBuilder",
        )

    def _build(self, commercial_report):
        from customer_outputs.customer_package_builder import CustomerPackageBuilder

        return CustomerPackageBuilder().build(commercial_report)

    def test_builder_accepts_commercial_package_report_only(self):
        from commercial_outputs.commercial_package_report import CommercialPackageReport
        from customer_outputs.customer_package_builder import CustomerPackageBuilder

        result = CustomerPackageBuilder().build(CommercialPackageReport())
        self.assertIsNotNone(result)

    def test_builder_returns_customer_package_report(self):
        from customer_outputs.customer_package_report import CustomerPackageReport

        result = self._build(self._commercial_report())
        self.assertIsInstance(result, CustomerPackageReport)

    def test_estimated_price_is_copied_from_commercial_package_report(self):
        result = self._build(self._commercial_report(estimated_price=1499.5))

        self.assertEqual(result.estimated_price, 1499.5)

    def test_commercial_warnings_are_preserved(self):
        warnings = ["No commercial pricing policy configured."]

        result = self._build(self._commercial_report(estimated_price=100.0, warnings=warnings))

        self.assertEqual(result.warnings, warnings)
        self.assertIsNot(result.warnings, warnings)
        self.assertIn("Commercial warnings:", result.customer_summary)
        self.assertIn(warnings[0], result.customer_summary)

    def test_customer_summary_contains_product_ready_and_estimated_price(self):
        result = self._build(self._commercial_report(estimated_price=250.0))

        self.assertIn("Product ready", result.customer_summary)
        self.assertIn("Estimated price: 250.0", result.customer_summary)

    def test_builder_signature_takes_commercial_package_report(self):
        from customer_outputs.customer_package_builder import CustomerPackageBuilder

        self.assertEqual(
            list(inspect.signature(CustomerPackageBuilder.build).parameters),
            ["self", "commercial_report"],
        )

    def test_builder_imports_no_manufacturing_or_cost_dependencies(self):
        from customer_outputs import customer_package_builder as module

        with open(module.__file__) as f:
            import_lines = [
                line.strip()
                for line in f.readlines()
                if line.strip().startswith("import") or line.strip().startswith("from")
            ]

        forbidden = [
            "FactoryReleasePackage",
            "CostPackageReport",
            "CostPackageBuilder",
            "ManufacturingApplicationService",
            "GeometryEngine",
            "SceneGraph",
            "manufacturing",
            "cost_intelligence",
        ]
        for line in import_lines:
            for token in forbidden:
                self.assertNotIn(
                    token,
                    line,
                    msg=f"Builder must not import '{token}' (found in: {line})",
                )

    def test_builder_uses_only_commercial_report_and_customer_report_imports(self):
        from customer_outputs import customer_package_builder as module

        with open(module.__file__) as f:
            import_lines = [
                line.strip()
                for line in f.readlines()
                if line.strip().startswith("import") or line.strip().startswith("from")
            ]

        allowed_imports = {
            "commercial_outputs.commercial_package_report",
            "customer_outputs.customer_package_report",
        }
        for line in import_lines:
            parts = line.split()
            if len(parts) >= 2 and parts[0] in ("import", "from"):
                module_name = parts[1]
                if not module_name.startswith("customer_outputs."):
                    self.assertIn(
                        module_name,
                        allowed_imports,
                        msg=f"Unexpected import: {line}",
                    )


if __name__ == "__main__":
    unittest.main()
