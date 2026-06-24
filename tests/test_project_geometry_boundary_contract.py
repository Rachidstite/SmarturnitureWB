import inspect
import unittest
from dataclasses import fields, is_dataclass
from pathlib import Path


class TestProjectGeometryBoundaryContract(unittest.TestCase):

    def test_adr_003_exists_and_defines_project_geometry_boundary(self):
        adr_path = Path(
            "docs/architecture/ADR-003-project-geometry-ownership-boundary.md"
        )
        self.assertTrue(adr_path.is_file())

        adr_text = adr_path.read_text(encoding="utf-8")
        for token in (
            "Project Geometry",
            "envelope",
            "bounds",
            "footprint",
            "Project Engineering",
            "adjacency",
            "alignment",
            "clearance",
            "collision",
        ):
            with self.subTest(token=token):
                self.assertIn(token, adr_text)

    def test_project_geometry_boundary_keeps_project_and_cabinet_owners_separate(self):
        from domain.furniture_project import CabinetPlacement, FurnitureProject
        from domain.furniture_project_builder import FurnitureProjectBuilder

        project = FurnitureProjectBuilder(
            project_id="P-GEO-1",
            name="Project Geometry Boundary",
            cabinets=["CAB-1"],
            placements=[CabinetPlacement(cabinet_id="CAB-1", x=0.0, y=0.0, z=0.0)],
            metadata={"phase": "draft"},
        ).build()

        self.assertIsInstance(project, FurnitureProject)
        self.assertEqual(
            [field.name for field in fields(FurnitureProject)],
            ["project_id", "name", "cabinets", "placements", "metadata"],
        )
        self.assertTrue(is_dataclass(CabinetPlacement))
        self.assertEqual(
            [field.name for field in fields(CabinetPlacement)],
            ["cabinet_id", "x", "y", "z", "rotation_z"],
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
            with self.subTest(project_token=token):
                self.assertFalse(hasattr(project, token))

        project_source = inspect.getsource(
            __import__("domain.furniture_project", fromlist=["FurnitureProject"])
        )
        builder_source = inspect.getsource(
            __import__("domain.furniture_project_builder", fromlist=["FurnitureProjectBuilder"])
        )
        combined_source = project_source + "\n" + builder_source

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
                self.assertNotIn(token, combined_source)

    def test_layout_scenegraph_and_downstream_layers_do_not_own_project_geometry(self):
        from domain import topology
        from layout import equal_layout, layout_engine, layout_result, manual_layout
        from manufacturing import (
            drawer_validation_builder,
            manufacturing_release_validator,
            project_manufacturing_readiness_builder,
            furniture_project_summary_builder,
        )
        from cost_intelligence import (
            factory_decision_builder,
            factory_decision_intelligence_builder,
            furniture_project_business_report_builder,
            furniture_project_executive_report_builder,
            manufacturing_executive_report_builder,
        )
        from scene_graph import builder as scene_graph_builder
        from scene_graph import node as scene_graph_node
        from scene_graph import scene_graph as scene_graph_module

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

        downstream_sources = "\n".join(
            inspect.getsource(module)
            for module in (
                topology,
                drawer_validation_builder,
                manufacturing_release_validator,
                project_manufacturing_readiness_builder,
                furniture_project_summary_builder,
                factory_decision_builder,
                factory_decision_intelligence_builder,
                manufacturing_executive_report_builder,
                furniture_project_business_report_builder,
                furniture_project_executive_report_builder,
            )
        )
        for token in ("Project Geometry", "envelope", "bounds", "footprint"):
            with self.subTest(downstream_token=token):
                self.assertNotIn(token, downstream_sources)


if __name__ == "__main__":
    unittest.main()
