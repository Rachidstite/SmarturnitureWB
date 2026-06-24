import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestProjectCabinetCollisionContract(unittest.TestCase):

    def test_project_collision_needs_project_pose_and_cabinet_geometry(self):
        from domain.furniture_project import CabinetPlacement, FurnitureProject
        from domain.furniture_project_builder import FurnitureProjectBuilder

        project = FurnitureProjectBuilder(
            project_id="P-COLL-1",
            name="Collision Project",
            cabinets=[self._cabinet("CAB-1"), self._cabinet("CAB-2")],
            placements=[
                CabinetPlacement(cabinet_id="CAB-1", x=0.0, y=0.0, z=0.0),
                CabinetPlacement(cabinet_id="CAB-2", x=1200.0, y=0.0, z=0.0),
            ],
            metadata={"phase": "draft"},
        ).build()

        self.assertIsInstance(project, FurnitureProject)
        self.assertEqual(len(project.cabinets), 2)
        self.assertEqual(len(project.placements), 2)
        self.assertTrue(is_dataclass(CabinetPlacement))
        self.assertEqual(
            [field.name for field in fields(CabinetPlacement)],
            [
                "cabinet_id",
                "x",
                "y",
                "z",
                "rotation_z",
            ],
        )
        self.assertFalse(hasattr(project, "collision"))
        self.assertFalse(hasattr(project, "bounds"))
        self.assertFalse(hasattr(project, "envelope"))

        for cabinet in project.cabinets:
            self.assertTrue(hasattr(cabinet, "graph"))
            self.assertTrue(hasattr(cabinet, "topology"))
            self.assertTrue(hasattr(cabinet.graph, "physical_nodes"))
            self.assertTrue(cabinet.graph.physical_nodes)
            self.assertTrue(
                any(
                    hasattr(node, "width")
                    and hasattr(node, "height")
                    and hasattr(node, "transform")
                    for node in cabinet.graph.physical_nodes
                )
            )
            self.assertTrue(getattr(cabinet.topology, "sections", {}))
            self.assertTrue(
                any(
                    hasattr(section, "width")
                    and hasattr(section, "height")
                    and hasattr(section, "depth")
                    for section in cabinet.topology.sections.values()
                )
            )

        self.assertTrue(
            all(
                hasattr(placement, "cabinet_id")
                and hasattr(placement, "x")
                and hasattr(placement, "y")
                and hasattr(placement, "z")
                and hasattr(placement, "rotation_z")
                for placement in project.placements
            )
        )
        self.assertTrue(
            all(
                not hasattr(placement, "width")
                and not hasattr(placement, "depth")
                and not hasattr(placement, "height")
                for placement in project.placements
            )
        )

    def test_collision_is_not_owned_by_layout_scenegraph_manufacturing_or_cost_layers(self):
        from domain import furniture_project, furniture_project_builder
        from layout import equal_layout, layout_engine, layout_result, manual_layout
        from manufacturing import manufacturing_production_package_builder
        from manufacturing import project_manufacturing_readiness_builder
        from scene_graph import builder as scene_graph_builder
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
            for module in (layout_engine, manual_layout, equal_layout, layout_result)
        )
        for token in ("FurnitureProject", "CabinetPlacement", "project_collision"):
            with self.subTest(layout_token=token):
                self.assertNotIn(token, layout_sources)

        scene_graph_sources = "\n".join(
            inspect.getsource(module)
            for module in (scene_graph_builder, scene_graph_module)
        )
        for token in ("FurnitureProject", "CabinetPlacement", "project_collision"):
            with self.subTest(scene_graph_token=token):
                self.assertNotIn(token, scene_graph_sources)

        manufacturing_sources = "\n".join(
            inspect.getsource(module)
            for module in (
                manufacturing_production_package_builder,
                project_manufacturing_readiness_builder,
            )
        )
        for token in ("project_collision", "CabinetPlacement"):
            with self.subTest(manufacturing_token=token):
                self.assertNotIn(token, manufacturing_sources)

        cost_sources = "\n".join(
            inspect.getsource(module)
            for module in (
                factory_decision_builder,
                factory_decision_intelligence_builder,
                manufacturing_executive_report_builder,
                furniture_project_business_report_builder,
                furniture_project_executive_report_builder,
            )
        )
        for token in ("project_collision", "CabinetPlacement"):
            with self.subTest(cost_token=token):
                self.assertNotIn(token, cost_sources)

        project_sources = "\n".join(
            inspect.getsource(module)
            for module in (furniture_project, furniture_project_builder)
        )
        self.assertIn("CabinetPlacement", project_sources)
        self.assertIn("FurnitureProject", project_sources)

        from domain.spatial_queries import SpatialQueryEngine

        spatial_source = inspect.getsource(SpatialQueryEngine)
        self.assertIn("find_collisions", spatial_source)
        self.assertNotIn("FurnitureProject", spatial_source)
        self.assertNotIn("CabinetPlacement", spatial_source)

    def test_collision_inputs_remain_immutable_and_separate_from_other_project_decisions(self):
        from domain.furniture_project import CabinetPlacement
        from domain.furniture_project_builder import FurnitureProjectBuilder

        cabinets = [self._cabinet("CAB-1"), self._cabinet("CAB-2")]
        placements = [
            CabinetPlacement(cabinet_id="CAB-1", x=0.0, y=0.0, z=0.0),
            CabinetPlacement(cabinet_id="CAB-2", x=1200.0, y=0.0, z=0.0),
        ]
        metadata = {"phase": "draft"}

        project = FurnitureProjectBuilder(
            project_id="P-COLL-2",
            name="Immutable Collision Project",
            cabinets=cabinets,
            placements=placements,
            metadata=metadata,
        ).build()

        self.assertIsNot(project.cabinets, cabinets)
        self.assertIsNot(project.placements, placements)
        self.assertIsNot(project.metadata, metadata)
        self.assertEqual(len(cabinets), 2)
        self.assertEqual(
            placements,
            [
                CabinetPlacement(cabinet_id="CAB-1", x=0.0, y=0.0, z=0.0),
                CabinetPlacement(cabinet_id="CAB-2", x=1200.0, y=0.0, z=0.0),
            ],
        )
        self.assertEqual(metadata, {"phase": "draft"})

        original_cabinet_graph_sizes = [
            len(getattr(cabinet.graph, "physical_nodes", []) or []) for cabinet in cabinets
        ]

        project.cabinets.append(self._cabinet("CAB-3"))
        project.placements.append(
            CabinetPlacement(cabinet_id="CAB-3", x=2400.0, y=0.0, z=0.0)
        )

        self.assertEqual(len(cabinets), 2)
        self.assertEqual(
            placements,
            [
                CabinetPlacement(cabinet_id="CAB-1", x=0.0, y=0.0, z=0.0),
                CabinetPlacement(cabinet_id="CAB-2", x=1200.0, y=0.0, z=0.0),
            ],
        )
        self.assertEqual(
            [len(getattr(cabinet.graph, "physical_nodes", []) or []) for cabinet in cabinets],
            original_cabinet_graph_sizes,
        )

    @staticmethod
    def _cabinet(uid):
        from domain.builders import WardrobeBuilder

        return WardrobeBuilder(
            uid=uid,
            width=1000,
            height=2000,
            depth=600,
        ).build()


if __name__ == "__main__":
    unittest.main()
