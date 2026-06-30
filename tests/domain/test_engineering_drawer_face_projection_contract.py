import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

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
from scene_graph.metadata import EngineeringDrawerFaceMetadata
from scene_graph.node import SceneNode as RenderSceneNode
from scene_graph.renderer import _drawer_strategy
from shared.contracts import CabinetParams, SectionConfig
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


def _import_drawer_builder_module():
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
        return importlib.import_module("builders.drawer_builder")


class TestEngineeringDrawerFaceProjectionContract(unittest.TestCase):
    def _build_cabinet(self):
        cabinet = Cabinet(
            CabinetParams(
                width=1800.0,
                height=2200.0,
                depth=600.0,
                base_height=80.0,
                sec_count=1,
                sec_data={
                    0: SectionConfig(
                        drawers=1,
                        shelves=0,
                        doors="None",
                        door_count=1,
                        drawer_type="Inset",
                    ),
                },
            )
        )
        spec = BaseCabinetSpecificationAdapter.from_cabinet_params(cabinet.params)
        attach_base_cabinet_engineering_models(cabinet, spec)
        return cabinet

    def test_transitional_bridge_projects_resolved_drawer_faces_into_engineering_model(self):
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
            side_effect=AssertionError(
                "DrawerBuilder must not be used as drawer-face source of truth"
            ),
        ):
            builder._attach_section_engineering_components()

        self.assertEqual(len(cabinet.engineering_model.drawer_faces), 1)
        drawer_face = cabinet.engineering_model.drawer_faces[0]
        self.assertEqual(drawer_face.section_index, 0)
        self.assertEqual(drawer_face.drawer_index, 0)
        self.assertEqual(drawer_face.source_rule, "resolved_drawer_face_projection")
        self.assertEqual(drawer_face.face_x_mm, resolved_drawer.face_x)
        self.assertEqual(drawer_face.face_y_mm, resolved_drawer.face_y)
        self.assertEqual(drawer_face.face_z_mm, resolved_drawer.face_z)
        self.assertEqual(drawer_face.face_w_mm, resolved_drawer.face_w)
        self.assertEqual(drawer_face.face_h_mm, resolved_drawer.face_h)
        self.assertEqual(drawer_face.thickness_mm, builder.mat.mdf_thickness)
        self.assertEqual(
            drawer_face.material,
            cabinet.engineering_model.left_side_panel.material,
        )

    def test_engineering_branch_emits_drawer_face_nodes(self):
        cabinet = self._build_cabinet()
        builder_module = _import_cabinet_builder_module()
        builder = builder_module.CabinetBuilder()
        builder._cabinet = cabinet
        builder.mat = MaterialManager()
        builder.geo = GeometryEngine(cabinet, builder.mat)
        builder.geo.resolve_all()
        builder._attach_section_engineering_components()

        graph = SceneGraphBuilder(
            cabinet,
            builder.mat,
            cabinet_id="ENG-DFACE-CAB",
        ).build(builder.geo)

        face_nodes = [
            node for node in graph.all_nodes()
            if getattr(getattr(node, "role", None), "name", "") == "DRAWER_FACE"
        ]
        self.assertEqual(len(face_nodes), 1)
        node = face_nodes[0]
        projected_face = cabinet.engineering_model.drawer_faces[0]
        self.assertEqual(node.width, projected_face.face_w_mm)
        self.assertEqual(node.depth, projected_face.thickness_mm)
        self.assertEqual(node.height, projected_face.face_h_mm)
        self.assertEqual(node.x, projected_face.face_x_mm)
        self.assertEqual(node.y, projected_face.face_y_mm)
        self.assertEqual(node.z, projected_face.face_z_mm)
        self.assertEqual(node.material, projected_face.material)
        self.assertEqual(node.metadata.source_rule, "resolved_drawer_face_projection")

    def test_engineering_drawer_face_renderer_does_not_use_drawer_builder(self):
        drawer_builder_module = _import_drawer_builder_module()
        node = RenderSceneNode(
            identity=SimpleNamespace(key="ENG_DRAWER_FACE_1"),
            width=400.0,
            depth=18.0,
            height=200.0,
            x=12.0,
            y=34.0,
            z=56.0,
            thickness=18.0,
            material="MDF_18_WHITE",
            group="Drawers",
            role=NodeRole.DRAWER_FACE,
            metadata=EngineeringDrawerFaceMetadata(
                source_rule="resolved_drawer_face_projection",
                section_index=0,
                drawer_index=0,
            ),
        )
        fake_renderer = SimpleNamespace(
            _ensure_group=Mock(),
            _render_simple_panel=Mock(),
        )

        with patch.object(
            drawer_builder_module.DrawerBuilder,
            "build",
            side_effect=AssertionError(
                "DrawerBuilder must not render engineering drawer faces"
            ),
        ):
            _drawer_strategy(node, fake_renderer)

        fake_renderer._render_simple_panel.assert_called_once_with(node)

    def test_legacy_scene_graph_fallback_still_emits_drawer_faces_without_engineering_model(self):
        cabinet = Cabinet(
            CabinetParams(
                width=1800.0,
                height=2200.0,
                depth=600.0,
                base_height=80.0,
                sec_count=1,
                sec_data={
                    0: SectionConfig(
                        drawers=1,
                        shelves=0,
                        doors="None",
                        door_count=1,
                        drawer_type="Inset",
                    ),
                },
            )
        )
        mat = MaterialManager()
        geo = GeometryEngine(cabinet, mat)
        geo.resolve_all()

        graph = SceneGraphBuilder(cabinet, mat, cabinet_id="LEG-DFACE-CAB").build(geo)

        roles = [node.role for node in graph.all_nodes()]
        self.assertEqual(roles.count(NodeRole.DRAWER_FACE), 1)
        self.assertEqual(roles.count(NodeRole.DRAWER_BOX_SIDE), 0)
        self.assertEqual(roles.count(NodeRole.DRAWER_BOX_BACK), 0)
        self.assertEqual(roles.count(NodeRole.DRAWER_BOX_BOTTOM), 0)


if __name__ == "__main__":
    unittest.main()
