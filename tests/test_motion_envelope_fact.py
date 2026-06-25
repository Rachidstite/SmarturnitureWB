import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestMotionEnvelopeFact(unittest.TestCase):
    def test_stores_component_id(self):
        from project_engineering.motion_envelope_fact import MotionEnvelopeFact

        fact = MotionEnvelopeFact(component_id="COMP-1")

        self.assertEqual(fact.component_id, "COMP-1")

    def test_defaults_motion_type_direction_and_source_to_empty_strings(self):
        from project_engineering.motion_envelope_fact import MotionEnvelopeFact

        fact = MotionEnvelopeFact(component_id="COMP-2")

        self.assertEqual(fact.motion_type, "")
        self.assertEqual(fact.direction, "")
        self.assertEqual(fact.source, "")

    def test_defaults_all_bounds_to_zero(self):
        from project_engineering.motion_envelope_fact import MotionEnvelopeFact

        fact = MotionEnvelopeFact(component_id="COMP-3")

        self.assertEqual(fact.x_min, 0.0)
        self.assertEqual(fact.y_min, 0.0)
        self.assertEqual(fact.z_min, 0.0)
        self.assertEqual(fact.x_max, 0.0)
        self.assertEqual(fact.y_max, 0.0)
        self.assertEqual(fact.z_max, 0.0)

    def test_can_store_all_bounds_and_metadata(self):
        from project_engineering.motion_envelope_fact import MotionEnvelopeFact

        fact = MotionEnvelopeFact(
            component_id="COMP-4",
            motion_type="swing",
            x_min=1.0,
            y_min=2.0,
            z_min=3.0,
            x_max=4.0,
            y_max=5.0,
            z_max=6.0,
            direction="front",
            source="motion-analysis",
        )

        self.assertEqual(fact.motion_type, "swing")
        self.assertEqual((fact.x_min, fact.y_min, fact.z_min), (1.0, 2.0, 3.0))
        self.assertEqual((fact.x_max, fact.y_max, fact.z_max), (4.0, 5.0, 6.0))
        self.assertEqual(fact.direction, "front")
        self.assertEqual(fact.source, "motion-analysis")

    def test_dataclass_fields_are_exact(self):
        from project_engineering.motion_envelope_fact import MotionEnvelopeFact

        self.assertTrue(is_dataclass(MotionEnvelopeFact))
        self.assertEqual(
            [field.name for field in fields(MotionEnvelopeFact)],
            [
                "component_id",
                "motion_type",
                "x_min",
                "y_min",
                "z_min",
                "x_max",
                "y_max",
                "z_max",
                "direction",
                "source",
            ],
        )

    def test_import_without_freecad(self):
        module = importlib.import_module("project_engineering.motion_envelope_fact")
        source = inspect.getsource(module)

        self.assertIn("MotionEnvelopeFact", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("project_engineering.motion_envelope_fact")
        source = inspect.getsource(module)

        for token in (
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "FreeCAD",
            "project_geometry",
            "scene_graph",
            "OperationalRuleResult",
            "OperationalDecisionReport",
            "readiness",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_contract_is_generic_and_component_agnostic(self):
        from project_engineering.motion_envelope_fact import MotionEnvelopeFact

        signature = inspect.signature(MotionEnvelopeFact)
        self.assertEqual(
            list(signature.parameters),
            [
                "component_id",
                "motion_type",
                "x_min",
                "y_min",
                "z_min",
                "x_max",
                "y_max",
                "z_max",
                "direction",
                "source",
            ],
        )
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)


if __name__ == "__main__":
    unittest.main()
