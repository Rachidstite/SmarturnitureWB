import inspect
import unittest
from dataclasses import fields, is_dataclass
from pathlib import Path


class TestProjectGeometryEnvelopeContract(unittest.TestCase):

    def test_adr_002_and_adr_003_define_envelope_as_project_geometry_fact(self):
        adr_002 = Path(
            "docs/architecture/ADR-002-canonical-project-spatial-conventions.md"
        )
        adr_003 = Path(
            "docs/architecture/ADR-003-project-geometry-ownership-boundary.md"
        )

        self.assertTrue(adr_002.is_file())
        self.assertTrue(adr_003.is_file())

        adr_002_text = adr_002.read_text(encoding="utf-8")
        adr_003_text = adr_003.read_text(encoding="utf-8")

        for token in (
            "Envelope Convention",
            "canonical occupied 3D extent",
            "Bounds are the normalized project-space axis-aligned extents of that envelope.",
            "Footprint is the project-floor projection of that extent.",
            "Envelope is the canonical occupied shape.",
        ):
            with self.subTest(adr_002_token=token):
                self.assertIn(token, adr_002_text)

        for token in (
            "Project Geometry boundary",
            "envelope",
            "bounds",
            "footprint",
            "FurnitureProject",
            "SceneGraph",
            "Topology",
            "Layout",
        ):
            with self.subTest(adr_003_token=token):
                self.assertIn(token, adr_003_text)

        self.assertIn("project geometry facts", adr_003_text.lower())
        self.assertIn("envelope", adr_003_text)
        self.assertIn("bounds", adr_003_text)
        self.assertIn("footprint", adr_003_text)

    def test_envelope_does_not_belong_to_furniture_project_or_cabinet_placement(self):
        from domain.furniture_project import CabinetPlacement, FurnitureProject
        from domain.furniture_project_builder import FurnitureProjectBuilder

        self.assertTrue(is_dataclass(FurnitureProject))
        self.assertTrue(is_dataclass(CabinetPlacement))
        self.assertEqual(
            [field.name for field in fields(FurnitureProject)],
            ["project_id", "name", "cabinets", "placements", "metadata"],
        )
        self.assertEqual(
            [field.name for field in fields(CabinetPlacement)],
            ["cabinet_id", "x", "y", "z", "rotation_z"],
        )

        project = FurnitureProjectBuilder(
            project_id="P-GEO-ENV-1",
            name="Envelope Boundary Project",
            cabinets=["CAB-1"],
            placements=[CabinetPlacement(cabinet_id="CAB-1", x=0.0, y=0.0, z=0.0)],
            metadata={"phase": "draft"},
        ).build()

        self.assertIsInstance(project, FurnitureProject)
        self.assertFalse(hasattr(project, "envelope"))
        self.assertFalse(hasattr(project, "bounds"))
        self.assertFalse(hasattr(project, "footprint"))
        self.assertFalse(hasattr(project, "adjacency"))
        self.assertFalse(hasattr(project, "alignment"))
        self.assertFalse(hasattr(project, "clearance"))
        self.assertFalse(hasattr(project, "collision"))

        project_sources = "\n".join(
            inspect.getsource(module)
            for module in (
                __import__("domain.furniture_project", fromlist=["FurnitureProject"]),
                __import__("domain.furniture_project_builder", fromlist=["FurnitureProjectBuilder"]),
            )
        )
        for token in (
            "envelope",
            "bounds",
            "footprint",
            "adjacency",
            "alignment",
            "clearance",
            "collision",
        ):
            with self.subTest(project_source_token=token):
                self.assertNotIn(token, project_sources)

    def test_envelope_remains_outside_layout_scenegraph_manufacturing_and_cost_layers(self):
        from domain import topology
        from layout import equal_layout, layout_engine, layout_result, manual_layout
        from manufacturing import (
            cabinet_engineering_builder,
            furniture_project_summary_builder,
            manufacturing_release_validator,
            project_manufacturing_readiness_builder,
        )
        from scene_graph import builder as scene_graph_builder
        from scene_graph import node as scene_graph_node
        from scene_graph import scene_graph as scene_graph_module
        from cost_intelligence import (
            factory_decision_builder,
            factory_decision_intelligence_builder,
            furniture_project_business_report_builder,
            furniture_project_executive_report_builder,
            manufacturing_executive_report_builder,
        )

        layout_sources = "\n".join(
            inspect.getsource(module)
            for module in (
                layout_engine,
                layout_result,
                manual_layout,
                equal_layout,
            )
        )
        for token in ("FurnitureProject", "CabinetPlacement"):
            with self.subTest(layout_token=token):
                self.assertNotIn(token, layout_sources)
        for token in ("envelope", "bounds", "footprint"):
            with self.subTest(layout_geometry_token=token):
                self.assertNotIn(token, layout_sources)

        scene_graph_sources = "\n".join(
            inspect.getsource(module)
            for module in (scene_graph_builder, scene_graph_node, scene_graph_module)
        )
        for token in ("FurnitureProject", "CabinetPlacement"):
            with self.subTest(scene_graph_token=token):
                self.assertNotIn(token, scene_graph_sources)
        for token in ("envelope", "bounds", "footprint"):
            with self.subTest(scene_graph_geometry_token=token):
                self.assertNotIn(token, scene_graph_sources)

        manufacturing_sources = "\n".join(
            inspect.getsource(module)
            for module in (
                topology,
                cabinet_engineering_builder,
                furniture_project_summary_builder,
                manufacturing_release_validator,
                project_manufacturing_readiness_builder,
            )
        )
        for token in ("envelope", "bounds", "footprint"):
            with self.subTest(manufacturing_geometry_token=token):
                self.assertNotIn(token, manufacturing_sources)

        cost_sources = "\n".join(
            inspect.getsource(module)
            for module in (
                factory_decision_builder,
                factory_decision_intelligence_builder,
                furniture_project_business_report_builder,
                furniture_project_executive_report_builder,
                manufacturing_executive_report_builder,
            )
        )
        for token in ("envelope", "bounds", "footprint"):
            with self.subTest(cost_geometry_token=token):
                self.assertNotIn(token, cost_sources)

    def test_envelope_is_documented_as_upstream_of_bounds_and_footprint_but_not_equal_to_them(self):
        adr_002_text = Path(
            "docs/architecture/ADR-002-canonical-project-spatial-conventions.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Envelope is the canonical occupied shape.", adr_002_text)
        self.assertIn("Bounds are the normalized project-space axis-aligned extents of that envelope.", adr_002_text)
        self.assertIn("Footprint is the project-floor projection of that extent.", adr_002_text)
        self.assertNotIn("Envelope is the same as bounds", adr_002_text)
        self.assertNotIn("Envelope is the same as footprint", adr_002_text)


if __name__ == "__main__":
    unittest.main()
