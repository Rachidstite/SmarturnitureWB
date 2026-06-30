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
from shared.resolved_types import ResolvedDrawer, ResolvedSection
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


class TestEngineeringDrawerBoxProjectionContract(unittest.TestCase):
    def _build_cabinet(self):
        cabinet = Cabinet(
            CabinetParams(
                width=1800.0,
                height=2200.0,
                depth=600.0,
                base_height=80.0,
                sec_count=1,
                sec_data={
                    0: SectionConfig(drawers=1, shelves=0, doors="Inset", door_count=1, drawer_type="Inset"),
                },
            )
        )
        spec = BaseCabinetSpecificationAdapter.from_cabinet_params(cabinet.params)
        attach_base_cabinet_engineering_models(cabinet, spec)
        return cabinet

    def test_transitional_bridge_projects_resolved_drawer_boxes_into_engineering_model(self):
        cabinet = self._build_cabinet()
        builder_module = _import_cabinet_builder_module()
        builder = builder_module.CabinetBuilder()
        builder._cabinet = cabinet
        builder.mat = MaterialManager()
        builder.geo = GeometryEngine(cabinet, builder.mat)
        builder.geo.resolve_all()

        self.assertEqual(len(builder.geo.resolved_sections[0].drawers), 1)
        resolved_drawer = builder.geo.resolved_sections[0].drawers[0]

        with patch.object(
            builder_module.DrawerBuilder,
            "build",
            side_effect=AssertionError("DrawerBuilder must not be used as drawer-box source of truth"),
        ):
            builder._attach_section_engineering_components()

        self.assertEqual(len(cabinet.engineering_model.drawer_boxes), 1)
        drawer_box = cabinet.engineering_model.drawer_boxes[0]
        self.assertEqual(drawer_box.section_index, 0)
        self.assertEqual(drawer_box.drawer_index, 0)
        self.assertEqual(drawer_box.source_rule, "resolved_drawer_projection")
        self.assertEqual(drawer_box.box_x_mm, resolved_drawer.box_x)
        self.assertEqual(drawer_box.box_y_mm, resolved_drawer.box_y)
        self.assertEqual(drawer_box.box_z_mm, resolved_drawer.box_z)
        self.assertEqual(drawer_box.box_w_mm, resolved_drawer.box_w)
        self.assertEqual(drawer_box.box_h_mm, resolved_drawer.box_h)
        self.assertEqual(drawer_box.box_d_mm, resolved_drawer.box_d)
        self.assertEqual(drawer_box.bottom_thickness_mm, resolved_drawer.bottom_thickness)
        self.assertEqual(drawer_box.side_thickness_mm, builder.mat.mdf_thickness)
        self.assertEqual(drawer_box.material, cabinet.engineering_model.left_side_panel.material)

    def test_engineering_branch_emits_drawer_box_nodes_without_fronts(self):
        cabinet = self._build_cabinet()
        builder_module = _import_cabinet_builder_module()
        builder = builder_module.CabinetBuilder()
        builder._cabinet = cabinet
        builder.mat = MaterialManager()
        builder.geo = GeometryEngine(cabinet, builder.mat)
        builder.geo.resolve_all()
        builder._attach_section_engineering_components()

        graph = SceneGraphBuilder(cabinet, builder.mat, cabinet_id="ENG-DBX-CAB").build(builder.geo)

        roles = [node.role for node in graph.all_nodes()]
        self.assertEqual(roles.count(NodeRole.DRAWER_BOX_SIDE), 2)
        self.assertEqual(roles.count(NodeRole.DRAWER_BOX_BACK), 1)
        self.assertEqual(roles.count(NodeRole.DRAWER_BOX_BOTTOM), 1)
        self.assertEqual(roles.count(NodeRole.DRAWER_FACE), 1)

    def test_legacy_scene_graph_fallback_still_emits_drawer_faces_without_engineering_model(self):
        cabinet = Cabinet(
            CabinetParams(
                width=1800.0,
                height=2200.0,
                depth=600.0,
                base_height=80.0,
                sec_count=1,
                sec_data={
                    0: SectionConfig(drawers=1, shelves=0, doors="Inset", door_count=1, drawer_type="Inset"),
                },
            )
        )
        mat = MaterialManager()
        geo = GeometryEngine(cabinet, mat)
        geo.resolve_all()

        graph = SceneGraphBuilder(cabinet, mat, cabinet_id="LEG-DBX-CAB").build(geo)

        roles = [node.role for node in graph.all_nodes()]
        self.assertEqual(roles.count(NodeRole.DRAWER_FACE), 1)
        self.assertEqual(roles.count(NodeRole.DRAWER_BOX_SIDE), 0)
        self.assertEqual(roles.count(NodeRole.DRAWER_BOX_BACK), 0)
        self.assertEqual(roles.count(NodeRole.DRAWER_BOX_BOTTOM), 0)


if __name__ == "__main__":
    unittest.main()
