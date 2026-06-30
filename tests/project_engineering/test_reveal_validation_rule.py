import importlib
import inspect
import unittest
from dataclasses import replace

from domain.base_cabinet_engineering_entry import (
    attach_base_cabinet_engineering_models,
)
from domain.base_cabinet_engineering_model import EngineeringDrawerFace, EngineeringDoorPlacement
from domain.base_cabinet_specification_adapter import (
    BaseCabinetSpecificationAdapter,
)
from engine.cabinet import Cabinet
from shared.contracts import CabinetParams
from shared.enums import DoorType


class TestRevealValidationRule(unittest.TestCase):
    def _base_model(self):
        cabinet = Cabinet(CabinetParams())
        spec = BaseCabinetSpecificationAdapter.from_cabinet_params(cabinet.params)
        attach_base_cabinet_engineering_models(cabinet, spec)
        return cabinet.engineering_model

    def _door(self, name, x_mm, z_mm=100.0, width_mm=400.0, height_mm=600.0):
        return EngineeringDoorPlacement(
            name=name,
            section_index=0,
            section_id="SEC-1",
            door_index=0,
            source_rule="resolved_door_projection",
            x_mm=x_mm,
            y_mm=10.0,
            z_mm=z_mm,
            width_mm=width_mm,
            height_mm=height_mm,
            thickness_mm=18.0,
            door_type=DoorType.INSET,
            hinge_side="LEFT",
            layer=0,
            material="MDF_18",
        )

    def _drawer_face(self, name, x_mm, z_mm=100.0, width_mm=400.0, height_mm=200.0):
        return EngineeringDrawerFace(
            name=name,
            section_index=0,
            section_id="SEC-1",
            drawer_index=0,
            source_rule="resolved_drawer_face_projection",
            face_x_mm=x_mm,
            face_y_mm=10.0,
            face_z_mm=z_mm,
            face_w_mm=width_mm,
            face_h_mm=height_mm,
            thickness_mm=18.0,
            layer=0,
            material="MDF_18",
        )

    def test_passes_when_gap_matches_target_within_tolerance(self):
        from project_engineering.reveal_validation_rule import RevealValidationRule

        model = replace(
            self._base_model(),
            doors=(
                self._door("SEC-1_Door_1", 18.0),
                self._door("SEC-1_Door_2", 420.0),
            ),
            drawer_faces=(),
        )

        report = RevealValidationRule.evaluate(
            model,
            target_reveal_mm=2.0,
            tolerance_mm=0.5,
        )

        self.assertEqual(report.decision.status, "PASS")
        self.assertGreaterEqual(report.decision.checked_gap_count, 1)
        self.assertEqual(report.decision.warning_count, 0)
        self.assertEqual(report.decision.violation_count, 0)
        self.assertEqual(len(report.violations), 0)

    def test_warns_when_gap_deviates_slightly(self):
        from project_engineering.reveal_validation_rule import RevealValidationRule

        model = replace(
            self._base_model(),
            doors=(
                self._door("SEC-1_Door_1", 18.0),
                self._door("SEC-1_Door_2", 421.0),
            ),
            drawer_faces=(),
        )

        report = RevealValidationRule.evaluate(
            model,
            target_reveal_mm=2.0,
            tolerance_mm=0.5,
        )

        self.assertEqual(report.decision.status, "WARNING")
        self.assertGreater(report.decision.warning_count, 0)
        self.assertEqual(report.decision.violation_count, 0)
        self.assertGreater(len(report.violations), 0)

    def test_fails_when_gap_deviates_strongly(self):
        from project_engineering.reveal_validation_rule import RevealValidationRule

        model = replace(
            self._base_model(),
            doors=(
                self._door("SEC-1_Door_1", 18.0),
                self._door("SEC-1_Door_2", 430.0),
            ),
            drawer_faces=(),
        )

        report = RevealValidationRule.evaluate(
            model,
            target_reveal_mm=2.0,
            tolerance_mm=0.5,
        )

        self.assertEqual(report.decision.status, "FAIL")
        self.assertGreater(report.decision.violation_count, 0)
        self.assertGreater(len(report.violations), 0)

    def test_rule_module_has_no_banned_dependencies(self):
        module = importlib.import_module("project_engineering.reveal_validation_rule")
        source = inspect.getsource(module)

        self.assertIn("RevealValidationRule", source)
        self.assertNotIn("GeometryEngine", source)
        self.assertNotIn("SceneGraph", source)
        self.assertNotIn("Manufacturing", source)
        self.assertNotIn("Cost", source)
        self.assertNotIn("FrontAlignmentRule", source)
        self.assertNotIn("StaticDoorDrawerCollisionRule", source)
        self.assertNotIn("FrontAccessibilityStaticRule", source)


if __name__ == "__main__":
    unittest.main()
