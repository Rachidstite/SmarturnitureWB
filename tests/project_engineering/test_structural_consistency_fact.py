import importlib
import inspect
import unittest
from dataclasses import replace

from domain.base_cabinet_engineering_entry import (
    attach_base_cabinet_engineering_models,
)
from domain.base_cabinet_engineering_model import (
    EngineeringDrawerBox,
    EngineeringDrawerFace,
    EngineeringDividerPlacement,
    EngineeringDoorPlacement,
    EngineeringShelfPlacement,
)
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
)
from engine.cabinet import Cabinet
from shared.contracts import CabinetParams
from shared.enums import DoorType


class TestStructuralConsistencyFact(unittest.TestCase):
    def _base_model(self):
        cabinet = Cabinet(CabinetParams())
        spec = BaseCabinetSpecificationAdapter.from_cabinet_params(cabinet.params)
        attach_base_cabinet_engineering_models(cabinet, spec)
        return cabinet.engineering_model

    def _door(self, name):
        return EngineeringDoorPlacement(
            name=name,
            section_index=0,
            section_id="SEC-1",
            door_index=0,
            source_rule="resolved_door_projection",
            x_mm=18.0,
            y_mm=12.0,
            z_mm=100.0,
            width_mm=380.0,
            height_mm=600.0,
            thickness_mm=18.0,
            door_type=DoorType.INSET,
            hinge_side="LEFT",
            layer=0,
            material="MDF_18",
        )

    def _drawer_face(self, name):
        return EngineeringDrawerFace(
            name=name,
            section_index=0,
            section_id="SEC-1",
            drawer_index=0,
            source_rule="resolved_drawer_face_projection",
            face_x_mm=18.0,
            face_y_mm=12.0,
            face_z_mm=100.0,
            face_w_mm=380.0,
            face_h_mm=200.0,
            thickness_mm=18.0,
            layer=0,
            material="MDF_18",
        )

    def _drawer_box(self, name):
        return EngineeringDrawerBox(
            name=name,
            section_index=0,
            section_id="SEC-1",
            drawer_index=0,
            source_rule="resolved_drawer_projection",
            box_x_mm=120.0,
            box_y_mm=120.0,
            box_z_mm=120.0,
            box_w_mm=300.0,
            box_h_mm=180.0,
            box_d_mm=300.0,
            bottom_thickness_mm=18.0,
            side_thickness_mm=18.0,
            layer=0,
            material="MDF_18",
        )

    def _shelf(self, name):
        return EngineeringShelfPlacement(
            name=name,
            section_index=0,
            section_id="SEC-1",
            source_rule="bridge",
            width_mm=200.0,
            depth_mm=200.0,
            thickness_mm=18.0,
            position_mm=(120.0, 120.0, 200.0),
        )

    def _divider(self, name):
        return EngineeringDividerPlacement(
            name=name,
            section_index=0,
            section_id="SEC-1",
            source_rule="bridge",
            width_mm=18.0,
            depth_mm=200.0,
            height_mm=500.0,
            position_mm=(300.0, 120.0, 100.0),
        )

    def test_extracts_facts_from_engineering_model_only(self):
        from project_engineering.structural_consistency_rule import (
            StructuralConsistencyRule,
        )

        model = replace(
            self._base_model(),
            doors=(self._door("SEC-1_Door_1"),),
            drawer_faces=(self._drawer_face("SEC-1_DrawerFace_1"),),
            drawer_boxes=(self._drawer_box("SEC-1_DrawerBox_1"),),
            shelves=(self._shelf("SEC-1_Shelf_1"),),
            dividers=(self._divider("SEC-1_Divider_1"),),
        )

        facts = StructuralConsistencyRule.extract_facts(model)
        component_types = {fact.component_type for fact in facts}

        self.assertIn("LEFT_SIDE_PANEL", component_types)
        self.assertIn("RIGHT_SIDE_PANEL", component_types)
        self.assertIn("TOP_PANEL", component_types)
        self.assertIn("BOTTOM_PANEL", component_types)
        self.assertIn("BACK_PANEL", component_types)
        self.assertIn("DOOR_PANEL", component_types)
        self.assertIn("DRAWER_FACE", component_types)
        self.assertIn("DRAWER_BOX", component_types)
        self.assertIn("SHELF", component_types)
        self.assertIn("DIVIDER", component_types)

    def test_fact_module_has_expected_schema(self):
        module = importlib.import_module("project_engineering.structural_consistency_fact")
        source = inspect.getsource(module)

        self.assertIn("StructuralConsistencyFact", source)
        self.assertIn("thickness_mm", source)
        self.assertNotIn("GeometryEngine", source)
        self.assertNotIn("SceneGraph", source)
        self.assertNotIn("Manufacturing", source)
        self.assertNotIn("Cost", source)


if __name__ == "__main__":
    unittest.main()
