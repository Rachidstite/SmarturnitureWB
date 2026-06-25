import inspect
import re
import unittest
from dataclasses import fields, is_dataclass
from pathlib import Path


class TestProjectGeometryBoundsContract(unittest.TestCase):

    def test_adr_002_and_adr_003_define_bounds_as_derived_from_envelope(self):
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
            "Bounds Convention",
            "axis-aligned min/max extents",
            "Relationship to Envelope",
            "Envelope is the canonical occupied shape.",
            "Bounds are the normalized project-space axis-aligned extents of that envelope.",
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
        self.assertIn("bounds", adr_003_text)
        self.assertIn("envelope", adr_003_text)
        self.assertIn("project geometry boundary", adr_003_text.lower())

    def test_furniture_project_and_cabinet_placement_remain_unchanged(self):
        from domain.furniture_project import CabinetPlacement, FurnitureProject

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

        project = FurnitureProject(
            project_id="P-GEO-BOUNDS-1",
            name="Bounds Boundary Project",
            cabinets=["CAB-1"],
            placements=[CabinetPlacement(cabinet_id="CAB-1", x=0.0, y=0.0, z=0.0)],
            metadata={"phase": "draft"},
        )

        self.assertIsInstance(project, FurnitureProject)
        self.assertFalse(hasattr(project, "bounds"))
        self.assertFalse(hasattr(project, "envelope"))
        self.assertFalse(hasattr(project, "footprint"))
        self.assertFalse(hasattr(project, "adjacency"))
        self.assertFalse(hasattr(project, "alignment"))
        self.assertFalse(hasattr(project, "clearance"))
        self.assertFalse(hasattr(project, "collision"))

        project_source = inspect.getsource(
            __import__("domain.furniture_project", fromlist=["FurnitureProject"])
        )
        for token in (
            "bounds",
            "envelope",
            "footprint",
            "adjacency",
            "alignment",
            "clearance",
            "collision",
        ):
            with self.subTest(project_source_token=token):
                self.assertNotIn(token, project_source)

    def test_bounds_are_not_owned_by_layout_scenegraph_manufacturing_or_cost(self):
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

        scene_graph_sources = "\n".join(
            inspect.getsource(module)
            for module in (scene_graph_builder, scene_graph_node, scene_graph_module)
        )
        for token in ("FurnitureProject", "CabinetPlacement"):
            with self.subTest(scene_graph_token=token):
                self.assertNotIn(token, scene_graph_sources)

        ownership_sources = "\n".join(
            inspect.getsource(module)
            for module in (
                topology,
                cabinet_engineering_builder,
                furniture_project_summary_builder,
                manufacturing_release_validator,
                project_manufacturing_readiness_builder,
                factory_decision_builder,
                factory_decision_intelligence_builder,
                furniture_project_business_report_builder,
                furniture_project_executive_report_builder,
                manufacturing_executive_report_builder,
            )
        )

        for token in (
            "class Bounds",
            "class ProjectBounds",
            "compute_bounds",
            "calculate_bounds",
            "derive_bounds",
            "build_bounds",
            "resolve_bounds",
            "from_bounds",
            "to_bounds",
        ):
            with self.subTest(bounds_algorithm_token=token):
                self.assertNotIn(token, ownership_sources)

    def test_bounds_are_documented_as_derived_not_independent_geometry(self):
        adr_002_text = Path(
            "docs/architecture/ADR-002-canonical-project-spatial-conventions.md"
        ).read_text(encoding="utf-8")

        self.assertIn("Bounds are the normalized project-space axis-aligned extents of that envelope.", adr_002_text)
        self.assertIn("Envelope is the canonical occupied shape.", adr_002_text)
        self.assertNotIn("Bounds are canonical geometry", adr_002_text)
        self.assertNotIn("Bounds are independent geometry", adr_002_text)

        production_source = "\n".join(
            inspect.getsource(module)
            for module in (
                __import__("domain.furniture_project", fromlist=["FurnitureProject"]),
                __import__("layout.layout_engine", fromlist=["LayoutEngine"]),
                __import__("layout.layout_result", fromlist=["LayoutResult"]),
                __import__("scene_graph.scene_graph", fromlist=["SceneGraph"]),
                __import__("scene_graph.node", fromlist=["SceneNode"]),
                __import__("manufacturing.cabinet_engineering_builder", fromlist=["CabinetEngineeringBuilder"]),
                __import__("cost_intelligence.factory_decision_builder", fromlist=["FactoryDecisionBuilder"]),
            )
        )
        self.assertNotRegex(production_source, re.compile(r"\bclass\s+Bounds\b"))
        self.assertNotRegex(production_source, re.compile(r"\bdef\s+[A-Za-z_]*bounds[A-Za-z_]*\b"))


if __name__ == "__main__":
    unittest.main()
