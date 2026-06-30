import importlib
import inspect
import unittest
from dataclasses import replace

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


class TestRevealValidationFact(unittest.TestCase):
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
            face_x_mm=420.0,
            face_y_mm=10.0,
            face_z_mm=100.0,
            face_w_mm=400.0,
            face_h_mm=200.0,
            thickness_mm=18.0,
            layer=0,
            material=model.left_side_panel.material,
        )
        return replace(model, doors=(door,), drawer_faces=(face,))

    def test_extracts_facts_from_engineering_model_only(self):
        from project_engineering.reveal_validation_rule import RevealValidationRule

        model = self._engineering_model()
        facts = RevealValidationRule.extract_facts(model)

        self.assertEqual(len(facts), 2)
        self.assertEqual({fact.component_type for fact in facts}, {"DOOR_PANEL", "DRAWER_FACE"})
        self.assertTrue(all(fact.source.startswith("resolved_") for fact in facts))
        self.assertTrue(all(fact.section_id == "SEC-1" for fact in facts))

    def test_fact_module_has_no_banned_dependencies(self):
        module = importlib.import_module("project_engineering.reveal_validation_fact")
        source = inspect.getsource(module)

        self.assertIn("RevealValidationFact", source)
        self.assertNotIn("GeometryEngine", source)
        self.assertNotIn("SceneGraph", source)
        self.assertNotIn("Manufacturing", source)
        self.assertNotIn("Cost", source)


if __name__ == "__main__":
    unittest.main()
