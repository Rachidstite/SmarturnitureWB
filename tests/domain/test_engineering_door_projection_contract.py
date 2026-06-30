import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.material_manager import MaterialManager
from domain.base_cabinet_engineering_entry import (
    attach_base_cabinet_engineering_models,
)
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
)
from engine.cabinet import Cabinet
from engine.geometry_engine import GeometryEngine
from scene_graph.builder import SceneGraphBuilder
from shared.contracts import CabinetParams, SectionConfig
from shared.enums import DoorType
from shared.resolved_types import ResolvedDoor, ResolvedSection
from shared.roles import NodeRole


def _import_cabinet_builder_module():
    fake_freecad = types.ModuleType("FreeCAD")
    fake_part = types.ModuleType("Part")
    fake_part.makeBox = lambda *args, **kwargs: object()
    fake_freecad_gui = types.ModuleType("FreeCADGui")
    fake_freecad_gui.listCommands = lambda: []
    fake_freecad_gui.addCommand = lambda *args, **kwargs: None
    fake_freecad_gui.addWorkbench = lambda *args, **kwargs: None
    with patch.dict(
        sys.modules,
        {
            "FreeCAD": fake_freecad,
            "Part": fake_part,
            "FreeCADGui": fake_freecad_gui,
        },
    ):
        return importlib.import_module("engine.cabinet_builder")


class TestEngineeringDoorProjectionContract(unittest.TestCase):
    def _build_cabinet(self):
        cabinet = Cabinet(
            CabinetParams(
                width=1800.0,
                height=2200.0,
                depth=600.0,
                base_height=80.0,
                sec_count=3,
                section_widths=[450.0, 900.0, 450.0],
                sec_data={
                    0: SectionConfig(shelves=1, doors="Inset", door_count=1),
                    1: SectionConfig(shelves=1, doors="Inset", door_count=1),
                    2: SectionConfig(shelves=1, doors="Inset", door_count=1),
                },
            )
        )
        spec = BaseCabinetSpecificationAdapter.from_cabinet_params(cabinet.params)
        attach_base_cabinet_engineering_models(cabinet, spec)
        return cabinet

    def test_transitional_bridge_projects_resolved_doors_into_engineering_model(self):
        cabinet = self._build_cabinet()
        builder_module = _import_cabinet_builder_module()
        builder = builder_module.CabinetBuilder()
        builder._cabinet = cabinet
        builder.mat = MaterialManager()
        builder.geo = GeometryEngine(cabinet, builder.mat)
        builder.geo.resolve_all()

        self.assertEqual(len(builder.geo.resolved_sections[0].doors), 1)

        builder._attach_section_engineering_components()

        self.assertEqual(len(cabinet.engineering_model.doors), 3)
        first_door = cabinet.engineering_model.doors[0]
        self.assertEqual(first_door.section_index, 0)
        self.assertEqual(first_door.door_index, 0)
        self.assertEqual(first_door.source_rule, "resolved_door_projection")
        self.assertIs(first_door.door_type, DoorType.INSET)
        self.assertEqual(
            first_door.material,
            cabinet.engineering_model.left_side_panel.material,
        )
        self.assertAlmostEqual(first_door.width_mm, builder.geo.resolved_sections[0].doors[0].width)
        self.assertAlmostEqual(first_door.height_mm, builder.geo.resolved_sections[0].doors[0].height)
        self.assertAlmostEqual(first_door.x_mm, builder.geo.resolved_sections[0].doors[0].x)
        self.assertAlmostEqual(first_door.y_mm, builder.geo.resolved_sections[0].doors[0].y)
        self.assertAlmostEqual(first_door.z_mm, builder.geo.resolved_sections[0].doors[0].z)
        self.assertEqual(first_door.hinge_side, builder.geo.resolved_sections[0].doors[0].hinge_side)
        self.assertEqual(first_door.layer, builder.geo.resolved_sections[0].doors[0].layer)

    def test_engineering_branch_emits_door_nodes(self):
        cabinet = self._build_cabinet()
        builder_module = _import_cabinet_builder_module()
        builder = builder_module.CabinetBuilder()
        builder._cabinet = cabinet
        builder.mat = MaterialManager()
        builder.geo = GeometryEngine(cabinet, builder.mat)
        builder.geo.resolve_all()
        builder._attach_section_engineering_components()

        graph = SceneGraphBuilder(cabinet, builder.mat, cabinet_id="ENG-DOOR-CAB").build(builder.geo)

        door_nodes = [
            node
            for node in graph.all_nodes()
            if getattr(getattr(node, "role", None), "name", "") == "DOOR_PANEL"
        ]
        self.assertEqual(len(door_nodes), 3)
        self.assertTrue(all(node.metadata.door_type for node in door_nodes))
        self.assertTrue(all(node.metadata.hinge_side in ("LEFT", "RIGHT") for node in door_nodes))

    def test_engineering_door_nodes_flow_into_manufacturing_cutlist_and_production_package(self):
        cabinet = Cabinet(
            CabinetParams(
                width=900.0,
                height=720.0,
                depth=580.0,
                base_height=0.0,
                sec_count=1,
                sec_data={
                    0: SectionConfig(shelves=1, doors="Inset", door_count=2),
                },
            )
        )
        spec = BaseCabinetSpecificationAdapter.from_cabinet_params(cabinet.params)
        attach_base_cabinet_engineering_models(cabinet, spec)

        builder_module = _import_cabinet_builder_module()
        builder = builder_module.CabinetBuilder()
        builder._cabinet = cabinet
        builder.mat = MaterialManager()
        builder.geo = GeometryEngine(cabinet, builder.mat)
        builder.geo.resolve_all()
        builder._attach_section_engineering_components()

        self.assertEqual(len(cabinet.engineering_model.doors), 2)

        graph = SceneGraphBuilder(cabinet, builder.mat, cabinet_id="V1-DOOR-CAB").build(builder.geo)

        from manufacturing.manufacturing_runtime_pipeline_builder import (
            ManufacturingRuntimePipelineBuilder,
        )

        runtime_result = ManufacturingRuntimePipelineBuilder().build(graph)

        door_panel_specs = [
            panel
            for panel in runtime_result.manufacturing_package.panels
            if panel.role == NodeRole.DOOR_PANEL
        ]
        self.assertEqual(len(door_panel_specs), 2)
        self.assertTrue(
            all("_DOOR-" in panel.identity for panel in door_panel_specs)
        )

        production_package = runtime_result.manufacturing_production_package
        door_cutlist_items = [
            item
            for item in production_package.cutlist_report.items
            if "_DOOR-" in item["identity"]
        ]
        self.assertEqual(len(door_cutlist_items), 2)
        self.assertEqual(
            [item["identity"] for item in door_cutlist_items],
            [panel.identity for panel in door_panel_specs],
        )

    def test_legacy_scene_graph_fallback_still_emits_doors_without_engineering_model(self):
        cabinet = Cabinet()
        cabinet.params.width = 1800.0
        cabinet.params.height = 2200.0
        cabinet.params.depth = 600.0
        cabinet.params.base_height = 80.0
        cabinet.params.sec_count = 1
        cabinet.params.back_panel_type = "REAR"

        geo = SimpleNamespace(
            resolved_top=SimpleNamespace(
                width=1800.0,
                depth=600.0,
                thickness=18.0,
                x=0.0,
                y=0.0,
                z=2182.0,
            ),
            resolved_sections=[
                ResolvedSection(
                    inner_x=18.0,
                    inner_width=1764.0,
                    shelf_width=1764.0,
                    drawer_box_width=1764.0,
                    left_overlay=0.0,
                    right_overlay=0.0,
                    door_x=18.0,
                    door_width=1764.0,
                    drawer_face_x=18.0,
                    drawer_face_width=1764.0,
                    divider_x=1782.0,
                    has_sliding_system=False,
                    shelves=(),
                    drawers=(),
                    doors=(
                        ResolvedDoor(
                            x=18.0,
                            y=18.0,
                            z=98.0,
                            width=1764.0,
                            height=2020.0,
                            door_type=DoorType.INSET,
                            hinge_side="LEFT",
                            layer=0,
                        ),
                    ),
                    divider=None,
                )
            ],
            is_buildable=True,
        )
        mat = SimpleNamespace(mdf_thickness=18.0, back_thickness=3.0)

        graph = SceneGraphBuilder(cabinet, mat, cabinet_id="LEGACY-DOOR-CAB").build(geo)

        door_nodes = [
            node
            for node in graph.all_nodes()
            if getattr(getattr(node, "role", None), "name", "") == "DOOR_PANEL"
        ]
        self.assertEqual(len(door_nodes), 1)
        self.assertEqual(door_nodes[0].role, NodeRole.DOOR_PANEL)


if __name__ == "__main__":
    unittest.main()
