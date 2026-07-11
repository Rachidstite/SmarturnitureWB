import inspect
import unittest
from unittest.mock import patch

import domain.base_cabinet_engineering_entry as engineering_entry_module
from application.manufacturing_application_service import (
    ManufacturingApplicationService,
)
from core.material_manager import MaterialManager
from domain.base_cabinet_product_workflow import (
    build_base_cabinet_product_workflow,
)
from domain.base_cabinet_specification import BaseCabinetSpecification
from engine.geometry_engine import GeometryEngine
from manufacturing.hardware_bom_report import HardwareBomReport, HardwareBomRow
from manufacturing.manufacturing_package import ManufacturingPackage
from manufacturing.manufacturing_production_package_builder import (
    ManufacturingProductionPackageBuilder,
)
from manufacturing.panel_spec import PanelSpec
from scene_graph.builder import SceneGraphBuilder
from shared.roles import NodeRole


class _IntegrationCabinetBuilder:
    def __init__(self):
        self.scene_graph = None

    def build(self, cabinet):
        material_manager = MaterialManager()
        geometry_engine = GeometryEngine(cabinet, material_manager)
        geometry_engine.resolve_all()
        self.scene_graph = SceneGraphBuilder(
            cabinet,
            material_manager,
        ).build(geometry_engine)
        cabinet.graph = self.scene_graph
        cabinet.scene_graph = self.scene_graph


class TestProductBomFoundation(unittest.TestCase):
    def test_panel_row_preserves_authoritative_cutlist_and_panelspec_fields(self):
        from manufacturing.product_bom_report import ProductBomRow

        row = ProductBomRow(
            bom_category="PANEL",
            identity="side-left",
            description="SIDE_PANEL",
            quantity=2,
            unit="pcs",
            component_reference=("side-left",),
            cabinet_reference=("cabinet-01",),
            source_reference=("side-left",),
            material="MDF_18MM",
            width_mm=600.0,
            height_mm=720.0,
            thickness_mm=18.0,
            component_role="SIDE_PANEL",
            group="CARCASS",
        )

        self.assertEqual(row.identity, "side-left")
        self.assertEqual(row.quantity, 2)
        self.assertEqual(row.material, "MDF_18MM")
        self.assertEqual(row.width_mm, 600.0)
        self.assertEqual(row.height_mm, 720.0)
        self.assertEqual(row.thickness_mm, 18.0)
        self.assertEqual(row.component_role, "SIDE_PANEL")
        self.assertEqual(row.group, "CARCASS")
        self.assertEqual(row.cabinet_reference, ("cabinet-01",))

    def test_hardware_row_preserves_authoritative_hardware_bom_fields(self):
        from manufacturing.product_bom_report import ProductBomRow

        row = ProductBomRow(
            bom_category="HARDWARE",
            identity="HINGE_BLUM_110_V1",
            description="Blum 110 degree hinge",
            quantity=4,
            unit="pcs",
            component_reference=("door-01",),
            cabinet_reference=("cabinet-01",),
            source_reference=("op-1", "op-2"),
        )

        self.assertEqual(row.identity, "HINGE_BLUM_110_V1")
        self.assertEqual(row.description, "Blum 110 degree hinge")
        self.assertEqual(row.quantity, 4)
        self.assertEqual(row.unit, "pcs")
        self.assertEqual(row.component_reference, ("door-01",))
        self.assertEqual(row.cabinet_reference, ("cabinet-01",))
        self.assertEqual(row.source_reference, ("op-1", "op-2"))
        self.assertIsNone(row.width_mm)
        self.assertIsNone(row.height_mm)
        self.assertIsNone(row.thickness_mm)

    def test_hardware_row_description_must_come_from_authoritative_hardware_bom(self):
        row = HardwareBomRow(
            sku="HINGE_BLUM_110_V1",
            description="Blum 110 degree hinge",
            quantity=4,
            unit="pcs",
            component_reference=("door-01",),
            cabinet_reference=("cabinet-01",),
            source_operation_references=("op-1",),
        )

        self.assertEqual(row.description, "Blum 110 degree hinge")
        self.assertEqual(row.hardware_sku, "HINGE_BLUM_110_V1")

    def test_product_bom_builder_path_populates_existing_production_package_slot(self):
        panel = PanelSpec(
            identity="side-left",
            role=NodeRole.SIDE_PANEL,
            width=600.0,
            height=720.0,
            thickness=18.0,
            material="MDF_18MM",
            group="CARCASS",
            quantity=1,
        )
        package = ManufacturingPackage(panels=[panel])

        production_package = ManufacturingProductionPackageBuilder().build(package)

        self.assertIsNotNone(
            production_package.product_bom_report,
            "ManufacturingProductionPackage.product_bom_report must be populated",
        )

    def test_product_bom_foundation_does_not_reextract_scene_graph(self):
        import manufacturing.manufacturing_production_package_builder as module

        source = inspect.getsource(module)
        self.assertNotIn("ManufacturingExtractor.extract", source)
        self.assertNotIn("scene_graph", source.lower())

    def test_existing_production_package_behavior_remains_backward_compatible(self):
        panel = PanelSpec(
            identity="side-left",
            role=NodeRole.SIDE_PANEL,
            width=600.0,
            height=720.0,
            thickness=18.0,
            material="MDF_18MM",
            quantity=1,
        )
        package = ManufacturingPackage(panels=[panel], warnings=["existing-warning"])

        production_package = ManufacturingProductionPackageBuilder().build(package)

        self.assertIsNotNone(production_package.cutlist_report)
        self.assertIsNotNone(production_package.hardware_report)
        self.assertEqual(production_package.cutlist_report.warnings, ["existing-warning"])

    def test_product_bom_row_quantities_must_match_authoritative_upstream_reports(self):
        panel = PanelSpec(
            identity="side-left",
            role=NodeRole.SIDE_PANEL,
            width=600.0,
            height=720.0,
            thickness=18.0,
            material="MDF_18MM",
            quantity=2,
        )
        hardware_report = HardwareBomReport(
            bom_rows=[
                HardwareBomRow(
                    sku="HINGE_BLUM_110_V1",
                    description="Blum 110 degree hinge",
                    quantity=4,
                    unit="pcs",
                    component_reference=("door-01",),
                    cabinet_reference=("cabinet-01",),
                    source_operation_references=("op-1",),
                )
            ]
        )

        self.assertEqual(panel.quantity, 2)
        self.assertEqual(hardware_report.bom_rows[0].quantity, 4)

    def test_reference_cabinet_product_bom_row_counts_follow_authoritative_current_cutlist_semantics(self):
        specification = BaseCabinetSpecification(
            width_mm=600.0,
            height_mm=720.0,
            depth_mm=580.0,
            door_count=2,
            shelf_count=1,
            has_back_panel=True,
            edge_banding_required=True,
            toe_kick_required=True,
            hinge_family="STANDARD_110",
            drawer_family="NONE",
        )

        with patch.object(
            engineering_entry_module,
            "CabinetBuilder",
            new=_IntegrationCabinetBuilder,
        ):
            build_base_cabinet_product_workflow(specification)
            manufacturing_result = ManufacturingApplicationService().execute(
                specification=specification
            )

        production_package = manufacturing_result.data["manufacturing_production_package"]
        cutlist = manufacturing_result.data["cut_list"]
        product_bom = production_package.product_bom_report
        hardware_rows = getattr(production_package.hardware_report, "bom_rows", []) or []

        self.assertIsNotNone(
            product_bom,
            "Reference cabinet must produce a Product BOM report",
        )

        panel_rows = [
            row for row in getattr(product_bom, "rows", ())
            if getattr(row, "bom_category", "") == "PANEL"
        ]
        bom_hardware_rows = [
            row for row in getattr(product_bom, "rows", ())
            if getattr(row, "bom_category", "") == "HARDWARE"
        ]

        self.assertEqual(
            len(panel_rows),
            len(getattr(cutlist, "items", []) or []),
            "Panel BOM rows must match current authoritative cutlist semantics",
        )
        self.assertEqual(
            len(panel_rows),
            10,
            "Reference cabinet currently produces 10 cutlist panel rows",
        )
        self.assertEqual(
            len(bom_hardware_rows),
            len(hardware_rows),
            "Hardware BOM rows must be carried without duplication",
        )

        self.assertTrue(
            all(getattr(row, "cabinet_reference", ()) == () for row in panel_rows),
            "Panel cabinet_reference must remain empty when no authoritative reference exists",
        )
        self.assertEqual(
            [
                (
                    getattr(row, "identity", ""),
                    getattr(row, "description", ""),
                    getattr(row, "quantity", 0),
                )
                for row in bom_hardware_rows
            ],
            [
                (
                    getattr(row, "hardware_sku", ""),
                    getattr(row, "description", ""),
                    getattr(row, "quantity", 0),
                )
                for row in hardware_rows
            ],
            "Hardware Product BOM rows must preserve HardwareBomReport ordering and values",
        )
