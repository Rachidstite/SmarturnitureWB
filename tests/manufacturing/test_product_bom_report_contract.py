import inspect
import unittest
from dataclasses import FrozenInstanceError, fields, is_dataclass
from typing import get_args, get_origin, get_type_hints


class TestProductBomReportContract(unittest.TestCase):
    def test_product_bom_row_contract_exists_and_is_dataclass(self):
        from manufacturing.product_bom_report import ProductBomRow

        self.assertTrue(is_dataclass(ProductBomRow))

    def test_product_bom_row_is_immutable(self):
        from manufacturing.product_bom_report import ProductBomRow

        row = ProductBomRow(
            bom_category="PANEL",
            identity="PANEL-1",
            description="SIDE_PANEL",
            quantity=1,
            unit="pcs",
            component_reference=("PANEL-1",),
            cabinet_reference=("CAB-1",),
            source_reference=("PANEL-1",),
        )

        with self.assertRaises(FrozenInstanceError):
            row.identity = "MUTATED"

    def test_product_bom_row_field_inventory_is_stable(self):
        from manufacturing.product_bom_report import ProductBomRow

        self.assertEqual(
            [field.name for field in fields(ProductBomRow)],
            [
                "bom_category",
                "identity",
                "description",
                "quantity",
                "unit",
                "component_reference",
                "cabinet_reference",
                "source_reference",
                "material",
                "width_mm",
                "height_mm",
                "thickness_mm",
                "component_role",
                "group",
            ],
        )

    def test_product_bom_row_panel_only_fields_use_explicit_optional_semantics(self):
        from manufacturing.product_bom_report import ProductBomRow

        type_hints = get_type_hints(ProductBomRow)
        for field_name in (
            "material",
            "width_mm",
            "height_mm",
            "thickness_mm",
            "component_role",
            "group",
        ):
            hint = type_hints[field_name]
            self.assertIsNotNone(
                get_origin(hint),
                f"{field_name} must be optional",
            )
            self.assertIn(
                type(None),
                get_args(hint),
                f"{field_name} must allow None",
            )

    def test_product_bom_row_safe_defaults_do_not_use_false_dimension_sentinels(self):
        from manufacturing.product_bom_report import ProductBomRow

        row = ProductBomRow(
            bom_category="HARDWARE",
            identity="HINGE_BLUM_110_V1",
            description="Blum 110 degree hinge",
            quantity=4,
            unit="pcs",
            component_reference=("door-01",),
            cabinet_reference=("cabinet-01",),
            source_reference=("op-1",),
        )

        self.assertIsNone(row.material)
        self.assertIsNone(row.width_mm)
        self.assertIsNone(row.height_mm)
        self.assertIsNone(row.thickness_mm)
        self.assertIsNone(row.component_role)
        self.assertIsNone(row.group)

    def test_product_bom_report_contract_exists_and_is_dataclass(self):
        from manufacturing.product_bom_report import ProductBomReport

        self.assertTrue(is_dataclass(ProductBomReport))

    def test_product_bom_report_is_immutable(self):
        from manufacturing.product_bom_report import ProductBomReport

        report = ProductBomReport(rows=(), warnings=(), source="ProductBomBuilder")

        with self.assertRaises(FrozenInstanceError):
            report.source = "MUTATED"

    def test_product_bom_report_field_inventory_is_stable(self):
        from manufacturing.product_bom_report import ProductBomReport

        self.assertEqual(
            [field.name for field in fields(ProductBomReport)],
            ["rows", "warnings", "source"],
        )

    def test_product_bom_report_has_no_schema_version_without_existing_convention(self):
        from manufacturing.product_bom_report import ProductBomReport

        field_names = [field.name for field in fields(ProductBomReport)]
        self.assertNotIn("schema_version", field_names)

    def test_product_bom_contract_has_no_banned_payload_fields(self):
        from manufacturing.product_bom_report import ProductBomReport, ProductBomRow

        report_field_names = {field.name for field in fields(ProductBomReport)}
        row_field_names = {field.name for field in fields(ProductBomRow)}

        banned_fields = {
            "cnc_report",
            "machining_report",
            "machining_operations",
            "cost_report",
            "cost_summary",
            "quotation_report",
            "quotation_document",
            "release_ready",
            "manufacturing_decision",
            "assembly_report",
            "assembly_instructions",
        }
        self.assertFalse(report_field_names & banned_fields)
        self.assertFalse(row_field_names & banned_fields)

    def test_product_bom_contract_module_does_not_own_runtime_or_commercial_logic(self):
        import manufacturing.product_bom_report as module

        source = inspect.getsource(module)

        for token in (
            "SceneGraph",
            "ManufacturingRuntimePipelineBuilder",
            "CommercialPackageBuilder",
            "CostPackageBuilder",
            "GeometryEngine",
            "Quotation",
            "CNC",
        ):
            self.assertNotIn(token, source)


if __name__ == "__main__":
    unittest.main()
