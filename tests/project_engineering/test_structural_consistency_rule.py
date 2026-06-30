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


class TestStructuralConsistencyRule(unittest.TestCase):
    def _base_model(self):
        cabinet = Cabinet(CabinetParams())
        spec = BaseCabinetSpecificationAdapter.from_cabinet_params(cabinet.params)
        attach_base_cabinet_engineering_models(cabinet, spec)
        return cabinet.engineering_model

    def _door(self, name, section_id="SEC-1", x_mm=60.0, y_mm=12.0, z_mm=100.0):
        return EngineeringDoorPlacement(
            name=name,
            section_index=0,
            section_id=section_id,
            door_index=0,
            source_rule="resolved_door_projection",
            x_mm=x_mm,
            y_mm=y_mm,
            z_mm=z_mm,
            width_mm=380.0,
            height_mm=600.0,
            thickness_mm=18.0,
            door_type=DoorType.INSET,
            hinge_side="LEFT",
            layer=0,
            material="MDF_18",
        )

    def _drawer_face(self, name, section_id="SEC-1", x_mm=60.0, y_mm=12.0, z_mm=100.0):
        return EngineeringDrawerFace(
            name=name,
            section_index=0,
            section_id=section_id,
            drawer_index=0,
            source_rule="resolved_drawer_face_projection",
            face_x_mm=x_mm,
            face_y_mm=y_mm,
            face_z_mm=z_mm,
            face_w_mm=380.0,
            face_h_mm=200.0,
            thickness_mm=18.0,
            layer=0,
            material="MDF_18",
        )

    def _drawer_box(
        self,
        name,
        section_id="SEC-1",
        x_mm=120.0,
        y_mm=120.0,
        z_mm=120.0,
        width_mm=300.0,
        height_mm=180.0,
        depth_mm=300.0,
    ):
        return EngineeringDrawerBox(
            name=name,
            section_index=0,
            section_id=section_id,
            drawer_index=0,
            source_rule="resolved_drawer_projection",
            box_x_mm=x_mm,
            box_y_mm=y_mm,
            box_z_mm=z_mm,
            box_w_mm=width_mm,
            box_h_mm=height_mm,
            box_d_mm=depth_mm,
            bottom_thickness_mm=18.0,
            side_thickness_mm=18.0,
            layer=0,
            material="MDF_18",
        )

    def _shelf(self, name, x_mm=120.0, y_mm=120.0, z_mm=200.0, width_mm=200.0, depth_mm=200.0):
        return EngineeringShelfPlacement(
            name=name,
            section_index=0,
            section_id="SEC-1",
            source_rule="bridge",
            width_mm=width_mm,
            depth_mm=depth_mm,
            thickness_mm=18.0,
            position_mm=(x_mm, y_mm, z_mm),
        )

    def _divider(self, name, x_mm=300.0, y_mm=120.0, z_mm=100.0, width_mm=18.0, depth_mm=200.0, height_mm=500.0):
        return EngineeringDividerPlacement(
            name=name,
            section_index=0,
            section_id="SEC-1",
            source_rule="bridge",
            width_mm=width_mm,
            depth_mm=depth_mm,
            height_mm=height_mm,
            position_mm=(x_mm, y_mm, z_mm),
        )

    def test_passes_for_plausible_structural_configuration(self):
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

        report = StructuralConsistencyRule.evaluate(model)

        self.assertEqual(report.decision.status, "PASS")
        self.assertEqual(report.decision.warning_count, 0)
        self.assertEqual(report.decision.violation_count, 0)
        self.assertGreater(report.decision.checked_component_count, 0)
        self.assertEqual(len(report.violations), 0)

    def test_warns_when_component_is_tight_to_bounds(self):
        from project_engineering.structural_consistency_rule import (
            StructuralConsistencyRule,
        )

        model = replace(
            self._base_model(),
            doors=(self._door("SEC-1_Door_1"),),
            drawer_faces=(self._drawer_face("SEC-1_DrawerFace_1"),),
            drawer_boxes=(self._drawer_box("SEC-1_DrawerBox_1", x_mm=18.0, y_mm=18.0, z_mm=18.0, width_mm=764.0, height_mm=200.0, depth_mm=300.0),),
            shelves=(self._shelf("SEC-1_Shelf_1", x_mm=18.0, y_mm=18.0, z_mm=200.0, width_mm=764.0, depth_mm=200.0),),
            dividers=(),
        )

        report = StructuralConsistencyRule.evaluate(model)

        self.assertIn(report.decision.status, {"WARNING", "FAIL"})
        self.assertGreater(len(report.violations), 0)
        self.assertGreater(report.decision.warning_count + report.decision.violation_count, 0)

    def test_fails_when_section_scoped_component_has_no_section_id(self):
        from project_engineering.structural_consistency_rule import (
            StructuralConsistencyRule,
        )

        model = replace(
            self._base_model(),
            doors=(self._door("UNSCOPED_Door", section_id=""),),
            drawer_faces=(),
            drawer_boxes=(),
            shelves=(),
            dividers=(),
        )

        report = StructuralConsistencyRule.evaluate(model)

        self.assertEqual(report.decision.status, "FAIL")
        self.assertGreater(report.decision.violation_count, 0)
        self.assertGreater(len(report.violations), 0)

    def test_rule_module_has_no_banned_dependencies(self):
        module = importlib.import_module(
            "project_engineering.structural_consistency_rule"
        )
        source = inspect.getsource(module)

        self.assertIn("StructuralConsistencyRule", source)
        self.assertNotIn("GeometryEngine", source)
        self.assertNotIn("SceneGraph", source)
        self.assertNotIn("Manufacturing", source)
        self.assertNotIn("Cost", source)
        self.assertNotIn("ConstraintEngine", source)


if __name__ == "__main__":
    unittest.main()
