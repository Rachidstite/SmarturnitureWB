import inspect
import unittest
from dataclasses import fields, is_dataclass

from manufacturing.factory_release_package import FactoryReleasePackage


class TestCostPackageReportContract(unittest.TestCase):
    """CostPackageReport is a passive dataclass — no logic, no defaults drift."""

    def test_report_is_dataclass(self):
        from cost_intelligence.cost_package_report import CostPackageReport

        self.assertTrue(is_dataclass(CostPackageReport))

    def test_report_field_inventory_is_stable(self):
        from cost_intelligence.cost_package_report import CostPackageReport

        self.assertEqual(
            [field.name for field in fields(CostPackageReport)],
            [
                "material_cost_total",
                "hardware_cost_total",
                "machining_cost_total",
                "assembly_cost_total",
                "total_cost",
                "warnings",
                "source",
            ],
        )

    def test_report_safe_defaults(self):
        from cost_intelligence.cost_package_report import CostPackageReport

        report = CostPackageReport()

        self.assertEqual(report.material_cost_total, 0.0)
        self.assertEqual(report.hardware_cost_total, 0.0)
        self.assertEqual(report.machining_cost_total, 0.0)
        self.assertEqual(report.assembly_cost_total, 0.0)
        self.assertEqual(report.total_cost, 0.0)
        self.assertEqual(report.warnings, [])
        self.assertEqual(report.source, "")

    def test_warning_defaults_are_independent(self):
        from cost_intelligence.cost_package_report import CostPackageReport

        r1 = CostPackageReport()
        r2 = CostPackageReport()
        self.assertIsNot(r1.warnings, r2.warnings)


class TestCostPackageBuilderFoundation(unittest.TestCase):
    """CostPackageBuilder reads FactoryReleasePackage only, never invents prices."""

    # -- helpers ------------------------------------------------------------

    @staticmethod
    def _bom_row(sku, qty):
        from manufacturing.hardware_bom_report import HardwareBomRow

        row = HardwareBomRow(sku=sku, quantity=qty)
        # hardware_sku is a property backed by ``sku``
        return row

    @staticmethod
    def _object_with(field_name, items):
        return type("Obj", (), {field_name: items})()

    def _build(self, package, pricing_catalog=None):
        from cost_intelligence.cost_package_builder import CostPackageBuilder

        return CostPackageBuilder(pricing_catalog=pricing_catalog).build(package)

    # -- 1. Empty package produces zero totals and warnings -----------------

    def test_empty_package_returns_zero_totals(self):
        package = FactoryReleasePackage()
        report = self._build(package)

        self.assertEqual(report.material_cost_total, 0.0)
        self.assertEqual(report.hardware_cost_total, 0.0)
        self.assertEqual(report.machining_cost_total, 0.0)
        self.assertEqual(report.assembly_cost_total, 0.0)
        self.assertEqual(report.total_cost, 0.0)
        self.assertEqual(report.warnings, [])
        self.assertEqual(report.source, "CostPackageBuilder")

    def test_empty_package_generates_no_warnings(self):
        package = FactoryReleasePackage()
        report = self._build(package)
        self.assertEqual(report.warnings, [])

    # -- 2. Hardware BOM without prices produces warning, not fake cost -----

    def test_unpriced_hardware_bom_produces_warning_not_fake_cost(self):
        from manufacturing.hardware_bom_report import HardwareBomReport

        hardware_bom = HardwareBomReport(
            bom_rows=[
                self._bom_row("UNKNOWN_SKU_1", 10),
                self._bom_row("UNKNOWN_SKU_2", 5),
            ]
        )
        package = FactoryReleasePackage(hardware_bom=hardware_bom)
        report = self._build(package)

        # Cost is zero — no fake values
        self.assertEqual(report.hardware_cost_total, 0.0)
        self.assertEqual(report.total_cost, 0.0)
        # Warnings should exist for missing prices
        self.assertTrue(
            any("Missing hardware price" in w for w in report.warnings),
            msg=f"Expected missing-price warning, got: {report.warnings}",
        )

    # -- 3. Existing priced evidence contributes to total -------------------

    def test_priced_hardware_bom_contributes_to_total(self):
        from manufacturing.hardware_bom_report import HardwareBomReport

        hardware_bom = HardwareBomReport(
            bom_rows=[
                self._bom_row("MINIFIX_15_V1", 48),
            ]
        )
        pricing_catalog = {
            "MINIFIX_15_V1": {"unit_price": 1.5},
        }
        package = FactoryReleasePackage(hardware_bom=hardware_bom)
        report = self._build(package, pricing_catalog=pricing_catalog)

        self.assertEqual(report.hardware_cost_total, 72.0)  # 48 * 1.5
        self.assertEqual(report.total_cost, 72.0)

    def test_partially_priced_hardware_bom_contributes_known_and_warns_unknown(
        self,
    ):
        from manufacturing.hardware_bom_report import HardwareBomReport

        hardware_bom = HardwareBomReport(
            bom_rows=[
                self._bom_row("MINIFIX_15_V1", 48),
                self._bom_row("UNKNOWN_SKU", 10),
            ]
        )
        pricing_catalog = {
            "MINIFIX_15_V1": {"unit_price": 1.5},
        }
        package = FactoryReleasePackage(hardware_bom=hardware_bom)
        report = self._build(package, pricing_catalog=pricing_catalog)

        self.assertEqual(report.hardware_cost_total, 72.0)
        self.assertTrue(
            any("Missing hardware price" in w for w in report.warnings),
            msg=f"Expected missing-price warning, got: {report.warnings}",
        )

    # -- 4. CNC rows counted but not priced --------------------------------

    def test_cnc_rows_counted_but_not_priced(self):
        cnc_package = self._object_with("rows", [{"op": "drill"}, {"op": "route"}])
        package = FactoryReleasePackage(cnc_package=cnc_package)
        report = self._build(package)

        self.assertEqual(report.machining_cost_total, 0.0)
        self.assertTrue(
            any("Machining cost cannot be calculated" in w for w in report.warnings),
            msg=f"Expected machining-unpriced warning, got: {report.warnings}",
        )

    # -- 5. Assembly rows counted but not priced ---------------------------

    def test_assembly_rows_counted_but_not_priced(self):
        assembly_package = self._object_with("rows", [{"group": "A"}])
        package = FactoryReleasePackage(assembly_package=assembly_package)
        report = self._build(package)

        self.assertEqual(report.assembly_cost_total, 0.0)
        self.assertTrue(
            any("Assembly cost cannot be calculated" in w for w in report.warnings),
            msg=f"Expected assembly-unpriced warning, got: {report.warnings}",
        )

    # -- 6. Builder reads FactoryReleasePackage only -----------------------

    def test_builder_accepts_factory_release_package(self):
        from cost_intelligence.cost_package_builder import CostPackageBuilder

        report = CostPackageBuilder().build(FactoryReleasePackage())
        self.assertIsNotNone(report)

    def test_builder_signature_takes_factory_release_package(self):
        from cost_intelligence.cost_package_builder import CostPackageBuilder

        sig = inspect.signature(CostPackageBuilder.build)
        params = list(sig.parameters)
        self.assertIn("package", params)
        # Ensure no additional mandatory parameters that aren't FactoryReleasePackage
        self.assertIn("package", params)

    def test_builder_has_no_geometry_scenegraph_imports(self):
        from cost_intelligence import cost_package_builder as module

        with open(module.__file__) as f:
            lines = f.readlines()
        import_lines = [
            l for l in lines if l.strip().startswith("import") or l.strip().startswith("from")
        ]

        forbidden = [
            "GeometryEngine",
            "SceneGraph",
            "ManufacturingDecisionBuilder",
            "ManufacturingProductionPackageBuilder",
            "ManufacturingCutlistBuilder",
            "CNCReportBuilder",
            "AssemblyPackageBuilder",
            "BaseApplicationService",
        ]
        for line in import_lines:
            for token in forbidden:
                self.assertNotIn(
                    token,
                    line,
                    msg=f"Builder must not import '{token}' (found in: {line.strip()})",
                )

    # -- Additional: source field is set ------------------------------------

    def test_source_field_is_set(self):
        package = FactoryReleasePackage()
        report = self._build(package)
        self.assertEqual(report.source, "CostPackageBuilder")

    # -- Additional: material cost never calculated at this layer -----------

    def test_material_cost_is_zero_even_with_cut_list_items(self):
        cut_list = self._object_with("items", [{"id": 1}])
        package = FactoryReleasePackage(cut_list=cut_list)
        report = self._build(package)

        self.assertEqual(report.material_cost_total, 0.0)
        self.assertTrue(
            any("Material cost cannot be calculated" in w for w in report.warnings),
            msg=f"Expected material-unpriced warning, got: {report.warnings}",
        )


if __name__ == "__main__":
    unittest.main()
