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
from manufacturing.assembly_package_builder import AssemblyPackageBuilder
from manufacturing.assembly_package_report import AssemblyPackageRow
from manufacturing.hardware_bom_report import HardwareBomReport, HardwareBomRow
from manufacturing.manufacturing_production_package import (
    ManufacturingProductionPackage,
)
from manufacturing.manufacturing_production_package_builder import (
    ManufacturingProductionPackageBuilder,
)
from manufacturing.product_bom_report import ProductBomReport, ProductBomRow
from scene_graph.builder import SceneGraphBuilder


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


class TestAssemblyPanelInventoryFoundation(unittest.TestCase):
    def test_panel_inventory_contains_only_product_bom_panel_rows(self):
        production_package = ManufacturingProductionPackage(
            product_bom_report=ProductBomReport(
                rows=(
                    ProductBomRow(
                        bom_category="PANEL",
                        identity="side-left",
                        description="SIDE_PANEL",
                        quantity=1,
                        unit="pcs",
                        component_reference=("side-left",),
                        cabinet_reference=(),
                        source_reference=("side-left",),
                        material="MDF_18MM",
                        width_mm=600.0,
                        height_mm=720.0,
                        thickness_mm=18.0,
                        component_role="SIDE_PANEL",
                        group="CARCASS",
                    ),
                    ProductBomRow(
                        bom_category="HARDWARE",
                        identity="HINGE_BLUM_110_V1",
                        description="Blum 110 degree hinge",
                        quantity=4,
                        unit="pcs",
                        component_reference=("door-01",),
                        cabinet_reference=("cabinet-01",),
                        source_reference=("hinge-op-1",),
                    ),
                ),
            ),
            hardware_report=HardwareBomReport(
                bom_rows=[
                    HardwareBomRow(
                        sku="HINGE_BLUM_110_V1",
                        description="Blum 110 degree hinge",
                        quantity=4,
                        unit="pcs",
                        component_reference=("door-01",),
                        cabinet_reference=("cabinet-01",),
                        source_operation_references=("hinge-op-1",),
                    )
                ]
            ),
        )

        report = AssemblyPackageBuilder().build(
            ManufacturingProductionPackage(
                product_bom_report=production_package.product_bom_report,
                hardware_report=production_package.hardware_report,
            )
        )

        self.assertEqual(len(report.panel_inventory), 1)
        self.assertEqual(report.panel_inventory[0].panel_identity, "side-left")

    def test_panel_inventory_copies_product_bom_panel_row_fields_exactly(self):
        product_bom_report = ProductBomReport(
            rows=(
                ProductBomRow(
                    bom_category="PANEL",
                    identity="side-left",
                    description="SIDE_PANEL",
                    quantity=2,
                    unit="pcs",
                    component_reference=("side-left",),
                    cabinet_reference=(),
                    source_reference=("side-left",),
                    material="MDF_18MM",
                    width_mm=600.0,
                    height_mm=720.0,
                    thickness_mm=18.0,
                    component_role="SIDE_PANEL",
                    group="CARCASS",
                ),
            ),
        )
        production_package = ManufacturingProductionPackage(
            product_bom_report=product_bom_report
        )

        report = AssemblyPackageBuilder().build(production_package)
        row = report.panel_inventory[0]

        self.assertEqual(row.panel_identity, "side-left")
        self.assertEqual(row.description, "SIDE_PANEL")
        self.assertEqual(row.quantity, 2)
        self.assertEqual(row.unit, "pcs")
        self.assertEqual(row.material, "MDF_18MM")
        self.assertEqual(row.width_mm, 600.0)
        self.assertEqual(row.height_mm, 720.0)
        self.assertEqual(row.thickness_mm, 18.0)
        self.assertEqual(row.component_role, "SIDE_PANEL")
        self.assertEqual(row.group, "CARCASS")
        self.assertEqual(row.component_reference, ("side-left",))
        self.assertEqual(row.cabinet_reference, ())

    def test_panel_inventory_does_not_infer_cabinet_reference(self):
        product_bom_report = ProductBomReport(
            rows=(
                ProductBomRow(
                    bom_category="PANEL",
                    identity="CAB-600X720X580-S1_SEC-LEFT_LEFT_SIDE-0",
                    description="SIDE_PANEL",
                    quantity=1,
                    unit="pcs",
                    component_reference=(
                        "CAB-600X720X580-S1_SEC-LEFT_LEFT_SIDE-0",
                    ),
                    cabinet_reference=(),
                    source_reference=(
                        "CAB-600X720X580-S1_SEC-LEFT_LEFT_SIDE-0",
                    ),
                    material="MDF_18MM",
                    width_mm=580.0,
                    height_mm=720.0,
                    thickness_mm=18.0,
                    component_role="SIDE_PANEL",
                    group="CARCASS",
                ),
            ),
        )

        report = AssemblyPackageBuilder().build(
            ManufacturingProductionPackage(product_bom_report=product_bom_report)
        )

        self.assertEqual(report.panel_inventory[0].cabinet_reference, ())

    def test_panel_inventory_preserves_product_bom_panel_row_order(self):
        product_bom_report = ProductBomReport(
            rows=(
                ProductBomRow(
                    bom_category="PANEL",
                    identity="panel-2",
                    description="PANEL_2",
                    quantity=1,
                    unit="pcs",
                    component_reference=("panel-2",),
                    cabinet_reference=(),
                    source_reference=("panel-2",),
                    material="MDF_18MM",
                    width_mm=200.0,
                    height_mm=300.0,
                    thickness_mm=18.0,
                    component_role="SHELF",
                    group="INTERNAL",
                ),
                ProductBomRow(
                    bom_category="HARDWARE",
                    identity="MINIFIX_15_V1",
                    description="Minifix 15",
                    quantity=4,
                    unit="pcs",
                    component_reference=("panel-2",),
                    cabinet_reference=("cabinet-01",),
                    source_reference=("op-1",),
                ),
                ProductBomRow(
                    bom_category="PANEL",
                    identity="panel-1",
                    description="PANEL_1",
                    quantity=1,
                    unit="pcs",
                    component_reference=("panel-1",),
                    cabinet_reference=(),
                    source_reference=("panel-1",),
                    material="MDF_18MM",
                    width_mm=100.0,
                    height_mm=300.0,
                    thickness_mm=18.0,
                    component_role="SIDE_PANEL",
                    group="CARCASS",
                ),
            ),
        )

        report = AssemblyPackageBuilder().build(
            ManufacturingProductionPackage(product_bom_report=product_bom_report)
        )

        self.assertEqual(
            [row.panel_identity for row in report.panel_inventory],
            ["panel-2", "panel-1"],
        )

    def test_existing_assembly_package_row_hardware_install_semantics_remain_unchanged(self):
        production_package = ManufacturingProductionPackage(
            hardware_report=HardwareBomReport(
                bom_rows=[
                    HardwareBomRow(
                        sku="HINGE_BLUM_110_V1",
                        description="Blum 110 degree hinge",
                        quantity=2,
                        unit="pcs",
                        component_reference=("door-01",),
                        cabinet_reference=("cabinet-01",),
                        hardware_category="HINGE",
                        source_operation_references=("hinge-op-1",),
                    )
                ]
            ),
            cnc_report=type(
                "CncReport",
                (),
                {
                    "rows": [
                        type(
                            "CncRow",
                            (),
                            {
                                "source_operation_reference": "hinge-op-1",
                                "operation_type": "DRILL",
                                "face": "BACK",
                            },
                        )(),
                    ],
                    "warnings": [],
                },
            )(),
            product_bom_report=ProductBomReport(rows=()),
        )

        report = AssemblyPackageBuilder().build(production_package)

        self.assertEqual(len(report.rows), 1)
        self.assertIsInstance(report.rows[0], AssemblyPackageRow)
        self.assertEqual(report.rows[0].hardware_required, "HINGE_BLUM_110_V1")
        self.assertEqual(report.rows[0].hardware_quantity, 2)
        self.assertEqual(report.rows[0].source_operation_references, ("hinge-op-1",))
        self.assertEqual(
            tuple(
                row.source_operation_reference
                for row in report.rows[0].required_machining
            ),
            ("hinge-op-1",),
        )

    def test_assembly_builder_uses_product_bom_not_scene_graph_or_engineering_for_panel_inventory(self):
        import manufacturing.assembly_package_builder as module

        source = inspect.getsource(module)

        self.assertIn("product_bom_report", source)
        self.assertNotIn("SceneGraph", source)
        self.assertNotIn("scene_graph", source.lower())
        self.assertNotIn("Engineering", source)
        self.assertNotIn("PanelSpec", source)
        self.assertNotIn("ManufacturingExtractor.extract", source)

    def test_existing_build_path_populates_enriched_assembly_report(self):
        specification = BaseCabinetSpecification()

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

        self.assertIsNotNone(production_package.assembly_report)
        self.assertEqual(
            len(getattr(production_package.assembly_report, "panel_inventory", ())),
            10,
        )

    def test_reference_cabinet_panel_inventory_matches_authoritative_product_bom(self):
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
        product_bom = production_package.product_bom_report
        assembly_report = production_package.assembly_report
        panel_bom_rows = [
            row for row in getattr(product_bom, "rows", ())
            if getattr(row, "bom_category", "") == "PANEL"
        ]

        self.assertEqual(len(panel_bom_rows), 10)
        self.assertEqual(len(assembly_report.panel_inventory), 10)
        self.assertEqual(
            [
                (
                    row.identity,
                    row.quantity,
                    row.width_mm,
                    row.height_mm,
                    row.thickness_mm,
                    row.cabinet_reference,
                )
                for row in panel_bom_rows
            ],
            [
                (
                    row.panel_identity,
                    row.quantity,
                    row.width_mm,
                    row.height_mm,
                    row.thickness_mm,
                    row.cabinet_reference,
                )
                for row in assembly_report.panel_inventory
            ],
        )
        self.assertEqual(
            len(assembly_report.rows),
            len(getattr(production_package.hardware_report, "bom_rows", ()) or ()),
        )
