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


class TestStaticDoorDrawerCollisionReport(unittest.TestCase):
    def test_report_contains_facts_decision_violations_tolerance_and_source(self):
        from project_engineering.static_door_drawer_collision_rule import (
            StaticDoorDrawerCollisionRule,
        )

        cabinet = Cabinet(CabinetParams())
        spec = BaseCabinetSpecificationAdapter.from_cabinet_params(cabinet.params)
        attach_base_cabinet_engineering_models(cabinet, spec)
        model = cabinet.engineering_model
        model = replace(
            model,
            doors=(
                EngineeringDoorPlacement(
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
                ),
            ),
            drawer_faces=(
                EngineeringDrawerFace(
                    name="SEC-1_DrawerFace_1",
                    section_index=0,
                    section_id="SEC-1",
                    drawer_index=0,
                    source_rule="resolved_drawer_face_projection",
                    face_x_mm=520.0,
                    face_y_mm=10.0,
                    face_z_mm=100.0,
                    face_w_mm=400.0,
                    face_h_mm=200.0,
                    thickness_mm=18.0,
                    layer=0,
                    material=model.left_side_panel.material,
                ),
            ),
        )

        report = StaticDoorDrawerCollisionRule.evaluate(
            model,
            tolerance_mm=0.5,
            source="static-door-drawer-collision-test",
        )

        self.assertEqual(report.tolerance_mm, 0.5)
        self.assertEqual(report.source, "static-door-drawer-collision-test")
        self.assertGreaterEqual(len(report.facts), 2)
        self.assertIsNotNone(report.decision)
        self.assertEqual(report.decision.source, "static-door-drawer-collision-test")
        self.assertIsInstance(report.violations, tuple)

    def test_report_module_has_no_geometry_engine_scene_graph_manufacturing_or_cost_dependency(self):
        module = importlib.import_module(
            "project_engineering.static_door_drawer_collision_report"
        )
        source = inspect.getsource(module)

        self.assertIn("StaticDoorDrawerCollisionReport", source)
        self.assertNotIn("GeometryEngine", source)
        self.assertNotIn("SceneGraph", source)
        self.assertNotIn("Manufacturing", source)
        self.assertNotIn("Cost", source)


if __name__ == "__main__":
    unittest.main()
