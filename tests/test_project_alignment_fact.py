import importlib
import inspect
import re
import unittest
from dataclasses import fields, is_dataclass


class TestProjectAlignmentFact(unittest.TestCase):
    def test_stores_first_and_second_component_ids(self):
        from project_engineering.project_alignment_fact import ProjectAlignmentFact

        fact = ProjectAlignmentFact(
            first_component_id="COMP-1",
            second_component_id="COMP-2",
        )

        self.assertEqual(fact.first_component_id, "COMP-1")
        self.assertEqual(fact.second_component_id, "COMP-2")

    def test_defaults_alignment_type_axis_and_source_to_empty_strings(self):
        from project_engineering.project_alignment_fact import ProjectAlignmentFact

        fact = ProjectAlignmentFact(
            first_component_id="COMP-3",
            second_component_id="COMP-4",
        )

        self.assertEqual(fact.alignment_type, "")
        self.assertEqual(fact.axis, "")
        self.assertEqual(fact.source, "")

    def test_defaults_offset_mm_and_tolerance_mm_to_zero(self):
        from project_engineering.project_alignment_fact import ProjectAlignmentFact

        fact = ProjectAlignmentFact(
            first_component_id="COMP-5",
            second_component_id="COMP-6",
        )

        self.assertEqual(fact.offset_mm, 0.0)
        self.assertEqual(fact.tolerance_mm, 0.0)

    def test_can_store_alignment_type_axis_offset_tolerance_and_source(self):
        from project_engineering.project_alignment_fact import ProjectAlignmentFact

        fact = ProjectAlignmentFact(
            first_component_id="COMP-7",
            second_component_id="COMP-8",
            alignment_type="flush",
            axis="x",
            offset_mm=1.5,
            tolerance_mm=0.25,
            source="alignment-analysis",
        )

        self.assertEqual(fact.alignment_type, "flush")
        self.assertEqual(fact.axis, "x")
        self.assertEqual(fact.offset_mm, 1.5)
        self.assertEqual(fact.tolerance_mm, 0.25)
        self.assertEqual(fact.source, "alignment-analysis")

    def test_dataclass_fields_are_exact(self):
        from project_engineering.project_alignment_fact import ProjectAlignmentFact

        self.assertTrue(is_dataclass(ProjectAlignmentFact))
        self.assertEqual(
            [field.name for field in fields(ProjectAlignmentFact)],
            [
                "first_component_id",
                "second_component_id",
                "alignment_type",
                "axis",
                "offset_mm",
                "tolerance_mm",
                "source",
            ],
        )

    def test_import_without_freecad(self):
        module = importlib.import_module("project_engineering.project_alignment_fact")
        source = inspect.getsource(module)

        self.assertIn("ProjectAlignmentFact", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module("project_engineering.project_alignment_fact")
        source = inspect.getsource(module)

        for token in (
            "extractor",
            "rule",
            "decision",
            "collision",
            "layout",
            "FurnitureProject",
            "CabinetPlacement",
            "SceneGraph",
            "manufacturing",
            "cost",
            "exports",
            "UI",
            "CNC",
            "FreeCAD",
        ):
            with self.subTest(token=token):
                self.assertNotIn(token, source)

        self.assertIsNone(re.search(r"\bui\b", source, flags=re.IGNORECASE))

    def test_does_not_require_component_specific_fields(self):
        from project_engineering.project_alignment_fact import ProjectAlignmentFact

        signature = inspect.signature(ProjectAlignmentFact)
        self.assertEqual(
            list(signature.parameters),
            [
                "first_component_id",
                "second_component_id",
                "alignment_type",
                "axis",
                "offset_mm",
                "tolerance_mm",
                "source",
            ],
        )
        for field_name in ("door", "drawer", "hinge", "slide", "shelf", "panel"):
            self.assertNotIn(field_name, signature.parameters)


if __name__ == "__main__":
    unittest.main()
