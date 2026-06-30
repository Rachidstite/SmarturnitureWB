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


class TestStaticDoorDrawerCollisionRule(unittest.TestCase):
    def _base_model(self):
        cabinet = Cabinet(CabinetParams())
        spec = BaseCabinetSpecificationAdapter.from_cabinet_params(cabinet.params)
        attach_base_cabinet_engineering_models(cabinet, spec)
        return cabinet.engineering_model

    def _door(self, name, x_mm, y_mm=10.0, z_mm=100.0, width_mm=400.0, height_mm=600.0):
        return EngineeringDoorPlacement(
            name=name,
            section_index=0,
            section_id="SEC-1",
            door_index=0,
            source_rule="resolved_door_projection",
            x_mm=x_mm,
            y_mm=y_mm,
            z_mm=z_mm,
            width_mm=width_mm,
            height_mm=height_mm,
            thickness_mm=18.0,
            door_type=DoorType.INSET,
            hinge_side="LEFT",
            layer=0,
            material="MDF_18",
        )

    def _drawer_face(
        self,
        name,
        x_mm,
        y_mm=10.0,
        z_mm=100.0,
        width_mm=400.0,
        height_mm=200.0,
    ):
        return EngineeringDrawerFace(
            name=name,
            section_index=0,
            section_id="SEC-1",
            drawer_index=0,
            source_rule="resolved_drawer_face_projection",
            face_x_mm=x_mm,
            face_y_mm=y_mm,
            face_z_mm=z_mm,
            face_w_mm=width_mm,
            face_h_mm=height_mm,
            thickness_mm=18.0,
            layer=0,
            material="MDF_18",
        )

    def test_passes_when_door_and_drawer_face_do_not_overlap(self):
        from project_engineering.static_door_drawer_collision_rule import (
            StaticDoorDrawerCollisionRule,
        )

        model = replace(
            self._base_model(),
            doors=(self._door("SEC-1_Door_1", 18.0),),
            drawer_faces=(self._drawer_face("SEC-1_DrawerFace_1", 520.0),),
        )

        report = StaticDoorDrawerCollisionRule.evaluate(model, tolerance_mm=0.5)

        self.assertEqual(report.decision.status, "PASS")
        self.assertEqual(report.decision.checked_pair_count, 1)
        self.assertEqual(report.decision.warning_count, 0)
        self.assertEqual(report.decision.violation_count, 0)
        self.assertEqual(len(report.violations), 0)

    def test_warns_when_overlap_is_within_tolerance(self):
        from project_engineering.static_door_drawer_collision_rule import (
            StaticDoorDrawerCollisionRule,
        )

        model = replace(
            self._base_model(),
            doors=(self._door("SEC-1_Door_1", 18.0),),
            drawer_faces=(self._drawer_face("SEC-1_DrawerFace_1", 417.7),),
        )

        report = StaticDoorDrawerCollisionRule.evaluate(model, tolerance_mm=0.5)

        self.assertEqual(report.decision.status, "WARNING")
        self.assertEqual(report.decision.checked_pair_count, 1)
        self.assertGreater(report.decision.warning_count, 0)
        self.assertEqual(report.decision.violation_count, 0)
        self.assertGreater(len(report.violations), 0)
        self.assertTrue(all(v.severity.name == "WARNING" for v in report.violations))

    def test_fails_when_overlap_exceeds_tolerance(self):
        from project_engineering.static_door_drawer_collision_rule import (
            StaticDoorDrawerCollisionRule,
        )

        model = replace(
            self._base_model(),
            doors=(self._door("SEC-1_Door_1", 18.0),),
            drawer_faces=(self._drawer_face("SEC-1_DrawerFace_1", 417.0),),
        )

        report = StaticDoorDrawerCollisionRule.evaluate(model, tolerance_mm=0.5)

        self.assertEqual(report.decision.status, "FAIL")
        self.assertEqual(report.decision.checked_pair_count, 1)
        self.assertEqual(report.decision.warning_count, 0)
        self.assertGreater(report.decision.violation_count, 0)
        self.assertGreater(len(report.violations), 0)
        self.assertTrue(any(v.severity.name == "ERROR" for v in report.violations))

    def test_rule_module_has_no_geometry_engine_scene_graph_manufacturing_or_cost_dependency(self):
        module = importlib.import_module(
            "project_engineering.static_door_drawer_collision_rule"
        )
        source = inspect.getsource(module)

        self.assertIn("StaticDoorDrawerCollisionRule", source)
        self.assertNotIn("GeometryEngine", source)
        self.assertNotIn("SceneGraph", source)
        self.assertNotIn("Manufacturing", source)
        self.assertNotIn("Cost", source)

    def test_ignores_facts_without_section_id(self):
        from project_engineering.static_door_drawer_collision_rule import (
            StaticDoorDrawerCollisionRule,
        )

        model = replace(
            self._base_model(),
            doors=(),
            drawer_faces=(),
        )
        model = replace(
            model,
            doors=(
                EngineeringDoorPlacement(
                    name="UNSCOPED_DOOR",
                    section_index=0,
                    section_id="",
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
                    material="MDF_18",
                ),
            ),
        )

        report = StaticDoorDrawerCollisionRule.evaluate(model, tolerance_mm=0.5)

        self.assertEqual(report.decision.checked_pair_count, 0)
        self.assertEqual(len(report.violations), 0)
        self.assertEqual(report.decision.status, "PASS")


if __name__ == "__main__":
    unittest.main()
