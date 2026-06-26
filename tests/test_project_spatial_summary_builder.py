import importlib
import inspect
import re
import unittest

from project_engineering.project_adjacency_fact import ProjectAdjacencyFact
from project_engineering.project_alignment_fact import ProjectAlignmentFact
from project_engineering.project_collision_fact import ProjectCollisionFact
from project_engineering.project_envelope import ProjectEnvelope
from project_engineering.project_footprint import ProjectFootprint
from project_engineering.project_spatial_summary_report import (
    ProjectSpatialSummaryReport,
)


class TestProjectSpatialSummaryBuilder(unittest.TestCase):
    def test_builds_project_spatial_summary_report(self):
        from project_engineering.project_spatial_summary_builder import (
            build_project_spatial_summary_report,
        )

        report = build_project_spatial_summary_report(
            project_id="PROJECT-1",
            envelope=ProjectEnvelope(
                x_min=0.0,
                y_min=0.0,
                z_min=0.0,
                x_max=10.0,
                y_max=20.0,
                z_max=30.0,
                source="envelope-source",
            ),
            footprint=ProjectFootprint(
                x_min=1.0,
                y_min=2.0,
                x_max=11.0,
                y_max=12.0,
                source="footprint-source",
            ),
            adjacency_facts=[
                ProjectAdjacencyFact(
                    first_component_id="A",
                    second_component_id="B",
                )
            ],
            alignment_facts=[
                ProjectAlignmentFact(
                    first_component_id="C",
                    second_component_id="D",
                ),
                ProjectAlignmentFact(
                    first_component_id="E",
                    second_component_id="F",
                ),
            ],
            collision_facts=[],
        )

        self.assertIsInstance(report, ProjectSpatialSummaryReport)

    def test_copies_project_id(self):
        from project_engineering.project_spatial_summary_builder import (
            build_project_spatial_summary_report,
        )

        report = build_project_spatial_summary_report(
            project_id="PROJECT-2",
            envelope=ProjectEnvelope(
                x_min=0.0,
                y_min=0.0,
                z_min=0.0,
                x_max=10.0,
                y_max=10.0,
                z_max=10.0,
                source="envelope-source",
            ),
            footprint=ProjectFootprint(
                x_min=0.0,
                y_min=0.0,
                x_max=10.0,
                y_max=10.0,
                source="footprint-source",
            ),
            adjacency_facts=[],
            alignment_facts=[],
            collision_facts=[],
        )

        self.assertEqual(report.project_id, "PROJECT-2")

    def test_copies_envelope_source_and_footprint_source(self):
        from project_engineering.project_spatial_summary_builder import (
            build_project_spatial_summary_report,
        )

        report = build_project_spatial_summary_report(
            project_id="PROJECT-3",
            envelope=ProjectEnvelope(
                x_min=0.0,
                y_min=0.0,
                z_min=0.0,
                x_max=5.0,
                y_max=5.0,
                z_max=5.0,
                source="source-envelope",
            ),
            footprint=ProjectFootprint(
                x_min=0.0,
                y_min=0.0,
                x_max=5.0,
                y_max=5.0,
                source="source-footprint",
            ),
            adjacency_facts=[],
            alignment_facts=[],
            collision_facts=[],
        )

        self.assertEqual(report.envelope_source, "source-envelope")
        self.assertEqual(report.footprint_source, "source-footprint")

    def test_counts_adjacency_alignment_and_collision_facts(self):
        from project_engineering.project_spatial_summary_builder import (
            build_project_spatial_summary_report,
        )

        report = build_project_spatial_summary_report(
            project_id="PROJECT-4",
            envelope=ProjectEnvelope(
                x_min=0.0,
                y_min=0.0,
                z_min=0.0,
                x_max=1.0,
                y_max=1.0,
                z_max=1.0,
                source="envelope",
            ),
            footprint=ProjectFootprint(
                x_min=0.0,
                y_min=0.0,
                x_max=1.0,
                y_max=1.0,
                source="footprint",
            ),
            adjacency_facts=[
                ProjectAdjacencyFact(
                    first_component_id="A",
                    second_component_id="B",
                ),
                ProjectAdjacencyFact(
                    first_component_id="B",
                    second_component_id="C",
                ),
            ],
            alignment_facts=[
                ProjectAlignmentFact(
                    first_component_id="D",
                    second_component_id="E",
                )
            ],
            collision_facts=[
                ProjectCollisionFact(
                    first_component_id="F",
                    second_component_id="G",
                ),
                ProjectCollisionFact(
                    first_component_id="H",
                    second_component_id="I",
                ),
            ],
        )

        self.assertEqual(report.adjacency_count, 2)
        self.assertEqual(report.alignment_count, 1)
        self.assertEqual(report.collision_count, 2)

    def test_sets_has_collisions_false_when_no_collisions(self):
        from project_engineering.project_spatial_summary_builder import (
            build_project_spatial_summary_report,
        )

        report = build_project_spatial_summary_report(
            project_id="PROJECT-5",
            envelope=ProjectEnvelope(
                x_min=0.0,
                y_min=0.0,
                z_min=0.0,
                x_max=1.0,
                y_max=1.0,
                z_max=1.0,
                source="envelope",
            ),
            footprint=ProjectFootprint(
                x_min=0.0,
                y_min=0.0,
                x_max=1.0,
                y_max=1.0,
                source="footprint",
            ),
            adjacency_facts=[],
            alignment_facts=[],
            collision_facts=[],
        )

        self.assertFalse(report.has_collisions)

    def test_sets_has_collisions_true_when_collisions_exist(self):
        from project_engineering.project_spatial_summary_builder import (
            build_project_spatial_summary_report,
        )

        report = build_project_spatial_summary_report(
            project_id="PROJECT-6",
            envelope=ProjectEnvelope(
                x_min=0.0,
                y_min=0.0,
                z_min=0.0,
                x_max=1.0,
                y_max=1.0,
                z_max=1.0,
                source="envelope",
            ),
            footprint=ProjectFootprint(
                x_min=0.0,
                y_min=0.0,
                x_max=1.0,
                y_max=1.0,
                source="footprint",
            ),
            adjacency_facts=[],
            alignment_facts=[],
            collision_facts=[
                ProjectCollisionFact(
                    first_component_id="X",
                    second_component_id="Y",
                )
            ],
        )

        self.assertTrue(report.has_collisions)

    def test_sets_source_to_project_spatial_summary_builder(self):
        from project_engineering.project_spatial_summary_builder import (
            build_project_spatial_summary_report,
        )

        report = build_project_spatial_summary_report(
            project_id="PROJECT-7",
            envelope=ProjectEnvelope(
                x_min=0.0,
                y_min=0.0,
                z_min=0.0,
                x_max=1.0,
                y_max=1.0,
                z_max=1.0,
                source="envelope",
            ),
            footprint=ProjectFootprint(
                x_min=0.0,
                y_min=0.0,
                x_max=1.0,
                y_max=1.0,
                source="footprint",
            ),
            adjacency_facts=[],
            alignment_facts=[],
            collision_facts=[],
        )

        self.assertEqual(report.source, "project-spatial-summary-builder")

    def test_import_without_freecad(self):
        module = importlib.import_module(
            "project_engineering.project_spatial_summary_builder"
        )
        source = inspect.getsource(module)

        self.assertIn("build_project_spatial_summary_report", source)
        self.assertNotIn("FreeCAD", source)

    def test_no_banned_imports(self):
        module = importlib.import_module(
            "project_engineering.project_spatial_summary_builder"
        )
        source = inspect.getsource(module)

        for token in (
            "geometry",
            "adjacency calculation",
            "alignment calculation",
            "collision calculation",
            "rule",
            "decision",
            "Engine",
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

    def test_function_signature_remains_generic(self):
        from project_engineering.project_spatial_summary_builder import (
            build_project_spatial_summary_report,
        )

        signature = inspect.signature(build_project_spatial_summary_report)
        self.assertEqual(
            list(signature.parameters),
            [
                "project_id",
                "envelope",
                "footprint",
                "adjacency_facts",
                "alignment_facts",
                "collision_facts",
            ],
        )
        self.assertNotIn("self", signature.parameters)
        self.assertNotIn("cls", signature.parameters)

    def test_does_not_contain_engine_terminology(self):
        module = importlib.import_module(
            "project_engineering.project_spatial_summary_builder"
        )
        source = inspect.getsource(module)

        self.assertNotIn("Engine", source)
        self.assertIsNone(re.search(r"\bEngine\b", source))


if __name__ == "__main__":
    unittest.main()
