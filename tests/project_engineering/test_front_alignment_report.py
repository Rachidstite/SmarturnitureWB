import importlib
import inspect
import unittest
from dataclasses import replace

from domain.base_cabinet_engineering_entry import (
    attach_base_cabinet_engineering_models,
)
from domain.base_cabinet_engineering_model import EngineeringDoorPlacement
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
)
from engine.cabinet import Cabinet
from shared.contracts import CabinetParams
from shared.enums import DoorType


class TestFrontAlignmentReport(unittest.TestCase):
    def test_report_contains_facts_decision_violations_tolerance_and_source(self):
        from project_engineering.front_alignment_rule import FrontAlignmentRule

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
        )

        report = FrontAlignmentRule.evaluate(model, tolerance_mm=0.5, source="front-alignment-test")

        self.assertEqual(report.tolerance_mm, 0.5)
        self.assertEqual(report.source, "front-alignment-test")
        self.assertGreaterEqual(len(report.facts), 1)
        self.assertIsNotNone(report.decision)
        self.assertEqual(report.decision.source, "front-alignment-test")
        self.assertIsInstance(report.violations, tuple)

    def test_report_module_has_no_geometry_engine_or_scene_graph_dependency(self):
        module = importlib.import_module("project_engineering.front_alignment_report")
        source = inspect.getsource(module)

        self.assertIn("FrontAlignmentReport", source)
        self.assertNotIn("GeometryEngine", source)
        self.assertNotIn("SceneGraph", source)


if __name__ == "__main__":
    unittest.main()

