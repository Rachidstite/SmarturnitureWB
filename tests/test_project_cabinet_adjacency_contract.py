import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestProjectCabinetAdjacencyContract(unittest.TestCase):

    def test_project_owns_cabinets_and_placements(self):
        from domain.furniture_project import CabinetPlacement, FurnitureProject
        from domain.furniture_project_builder import FurnitureProjectBuilder

        project = FurnitureProjectBuilder(
            project_id="P-1",
            name="Adjacency Project",
            cabinets=["CAB-1"],
            placements=[CabinetPlacement(cabinet_id="CAB-1", x=0.0, y=0.0, z=0.0)],
            metadata={"phase": "draft"},
        ).build()

        self.assertTrue(hasattr(project, "cabinets"))
        self.assertTrue(hasattr(project, "placements"))
        self.assertIsInstance(project, FurnitureProject)
        self.assertEqual(project.cabinets, ["CAB-1"])
        self.assertEqual(len(project.placements), 1)
        self.assertTrue(is_dataclass(CabinetPlacement))
        self.assertEqual(
            [field.name for field in fields(CabinetPlacement)],
            ["cabinet_id", "x", "y", "z", "rotation_z"],
        )

    def test_adjacency_is_project_level_not_layout_or_scenegraph_level(self):
        from domain import furniture_project, furniture_project_builder
        from layout import equal_layout, layout_engine, layout_result, manual_layout
        from scene_graph import builder as scene_graph_builder
        from scene_graph import scene_graph as scene_graph_module

        layout_sources = "\n".join(
            inspect.getsource(module)
            for module in (layout_engine, manual_layout, equal_layout, layout_result)
        )
        for token in (
            "FurnitureProject",
            "CabinetPlacement",
            "adjacency",
        ):
            with self.subTest(layout_token=token):
                self.assertNotIn(token, layout_sources)

        scene_graph_sources = "\n".join(
            inspect.getsource(module)
            for module in (scene_graph_builder, scene_graph_module)
        )
        for token in (
            "FurnitureProject",
            "CabinetPlacement",
            "adjacency",
        ):
            with self.subTest(scene_graph_token=token):
                self.assertNotIn(token, scene_graph_sources)

        furniture_project_sources = "\n".join(
            inspect.getsource(module)
            for module in (furniture_project, furniture_project_builder)
        )
        self.assertIn("CabinetPlacement", furniture_project_sources)
        self.assertIn("FurnitureProject", furniture_project_sources)

    def test_project_and_placement_objects_remain_separate_and_immutable(self):
        from domain.furniture_project import CabinetPlacement
        from domain.furniture_project_builder import FurnitureProjectBuilder

        cabinets = ["CAB-1", "CAB-2"]
        placements = [
            CabinetPlacement(cabinet_id="CAB-1", x=0.0, y=0.0, z=0.0),
            CabinetPlacement(cabinet_id="CAB-2", x=1200.0, y=0.0, z=0.0),
        ]
        metadata = {"phase": "draft"}

        builder = FurnitureProjectBuilder(
            project_id="P-2",
            name="Immutable Project",
            cabinets=cabinets,
            placements=placements,
            metadata=metadata,
        )
        project = builder.build()

        self.assertIsNot(project.cabinets, cabinets)
        self.assertIsNot(project.placements, placements)
        self.assertIsNot(project.metadata, metadata)
        self.assertEqual(cabinets, ["CAB-1", "CAB-2"])
        self.assertEqual(
            placements,
            [
                CabinetPlacement(cabinet_id="CAB-1", x=0.0, y=0.0, z=0.0),
                CabinetPlacement(cabinet_id="CAB-2", x=1200.0, y=0.0, z=0.0),
            ],
        )
        self.assertEqual(metadata, {"phase": "draft"})

        project.cabinets.append("CAB-3")
        project.placements.append(
            CabinetPlacement(cabinet_id="CAB-3", x=2400.0, y=0.0, z=0.0)
        )

        self.assertEqual(cabinets, ["CAB-1", "CAB-2"])
        self.assertEqual(
            placements,
            [
                CabinetPlacement(cabinet_id="CAB-1", x=0.0, y=0.0, z=0.0),
                CabinetPlacement(cabinet_id="CAB-2", x=1200.0, y=0.0, z=0.0),
            ],
        )


if __name__ == "__main__":
    unittest.main()
