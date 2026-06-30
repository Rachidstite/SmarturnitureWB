import importlib
import inspect
import unittest
from dataclasses import replace

from core.material_manager import MaterialManager
from domain.base_cabinet_engineering_entry import (
    attach_base_cabinet_engineering_models,
)
from domain.base_cabinet_engineering_model import (
    EngineeringDrawerFace,
    EngineeringDoorPlacement,
)
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
)
from engine.cabinet import Cabinet
from shared.contracts import CabinetParams
from shared.enums import DoorType


class TestFrontAlignmentFact(unittest.TestCase):
    def _engineering_model(self):
        cabinet = Cabinet(CabinetParams())
        spec = BaseCabinetSpecificationAdapter.from_cabinet_params(cabinet.params)
        attach_base_cabinet_engineering_models(cabinet, spec)
        model = cabinet.engineering_model

        door = EngineeringDoorPlacement(
            name="SEC-1_Door_1",
            section_index=0,
            section_id="SEC-1",
            door_index=0,
            source_rule="resolved_door_projection",
            x_mm=18.0,
            y_mm=10.0,
            z_mm=100.0,
            width_mm=400.0,
            height_mm=600.0,
            thickness_mm=18.0,
            door_type=DoorType.INSET,
            hinge_side="LEFT",
            layer=0,
            material=model.left_side_panel.material,
        )
        face = EngineeringDrawerFace(
            name="SEC-1_DrawerFace_1",
            section_index=0,
            section_id="SEC-1",
            drawer_index=0,
            source_rule="resolved_drawer_face_projection",
            face_x_mm=18.0,
            face_y_mm=10.0,
            face_z_mm=100.0,
            face_w_mm=400.0,
            face_h_mm=200.0,
            thickness_mm=18.0,
            layer=0,
            material=model.left_side_panel.material,
        )
        return replace(model, doors=(door,), drawer_faces=(face,))

    def test_extracts_facts_from_doors_and_drawer_faces(self):
        from project_engineering.front_alignment_rule import FrontAlignmentRule

        model = self._engineering_model()
        facts = FrontAlignmentRule.extract_facts(model)

        self.assertEqual(len(facts), 2)
        self.assertEqual({fact.component_type for fact in facts}, {"DOOR_PANEL", "DRAWER_FACE"})
        self.assertTrue(all(fact.source.startswith("resolved_") for fact in facts))
        self.assertTrue(all(fact.front_plane_mm == fact.y_mm for fact in facts))

    def test_fact_module_has_no_geometry_engine_or_scene_graph_dependency(self):
        module = importlib.import_module("project_engineering.front_alignment_fact")
        source = inspect.getsource(module)

        self.assertIn("FrontAlignmentFact", source)
        self.assertNotIn("GeometryEngine", source)
        self.assertNotIn("SceneGraph", source)


if __name__ == "__main__":
    unittest.main()

