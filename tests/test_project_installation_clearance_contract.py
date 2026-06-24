import inspect
import unittest
from dataclasses import fields, is_dataclass


class TestProjectInstallationClearanceContract(unittest.TestCase):

    def test_project_clearance_is_pose_based_project_ownership(self):
        from domain.furniture_project import CabinetPlacement, FurnitureProject
        from domain.furniture_project_builder import FurnitureProjectBuilder

        project = FurnitureProjectBuilder(
            project_id="P-CLR-1",
            name="Clearance Project",
            cabinets=["CAB-1", "CAB-2"],
            placements=[
                CabinetPlacement(cabinet_id="CAB-1", x=0.0, y=0.0, z=0.0),
                CabinetPlacement(cabinet_id="CAB-2", x=1200.0, y=0.0, z=0.0),
            ],
            metadata={"phase": "draft"},
        ).build()

        self.assertIsInstance(project, FurnitureProject)
        self.assertEqual(project.cabinets, ["CAB-1", "CAB-2"])
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
        self.assertFalse(hasattr(project, "clearance"))
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
                not hasattr(placement, "clearance")
                and not hasattr(placement, "tolerance")
                and not hasattr(placement, "distance")
                for placement in project.placements
            )
        )

    def test_clearance_is_not_layout_scenegraph_manufacturing_or_cost_responsibility(self):
        from domain import furniture_project, furniture_project_builder
        from layout import equal_layout, layout_engine, layout_result, manual_layout
        from manufacturing import project_manufacturing_readiness_builder
        from manufacturing import manufacturing_production_package_builder
        from scene_graph import builder as scene_graph_builder
        from scene_graph import scene_graph as scene_graph_module
        from cost_intelligence import (
            factory_decision_builder,
            manufacturing_executive_report_builder,
            furniture_project_business_report_builder,
            furniture_project_executive_report_builder,
            factory_decision_intelligence_builder,
        )

        layout_sources = "\n".join(
            inspect.getsource(module)
            for module in (layout_engine, manual_layout, equal_layout, layout_result)
        )
        for token in ("FurnitureProject", "CabinetPlacement", "installation_clearance"):
            with self.subTest(layout_token=token):
                self.assertNotIn(token, layout_sources)

        scene_graph_sources = "\n".join(
            inspect.getsource(module)
            for module in (scene_graph_builder, scene_graph_module)
        )
        for token in ("FurnitureProject", "CabinetPlacement", "installation_clearance"):
            with self.subTest(scene_graph_token=token):
                self.assertNotIn(token, scene_graph_sources)

        manufacturing_sources = "\n".join(
            inspect.getsource(module)
            for module in (
                project_manufacturing_readiness_builder,
                manufacturing_production_package_builder,
            )
        )
        for token in ("installation_clearance", "CabinetPlacement"):
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
        for token in ("installation_clearance", "CabinetPlacement"):
            with self.subTest(cost_token=token):
                self.assertNotIn(token, cost_sources)

        project_sources = "\n".join(
            inspect.getsource(module)
            for module in (furniture_project, furniture_project_builder)
        )
        self.assertIn("CabinetPlacement", project_sources)
        self.assertIn("FurnitureProject", project_sources)

    def test_clearance_inputs_remain_immutable_and_separate_from_other_project_decisions(self):
        from domain.furniture_project import CabinetPlacement
        from domain.furniture_project_builder import FurnitureProjectBuilder

        cabinets = ["CAB-1", "CAB-2"]
        placements = [
            CabinetPlacement(cabinet_id="CAB-1", x=0.0, y=0.0, z=0.0),
            CabinetPlacement(cabinet_id="CAB-2", x=1200.0, y=0.0, z=0.0),
        ]
        metadata = {"phase": "draft"}

        project = FurnitureProjectBuilder(
            project_id="P-CLR-2",
            name="Immutable Clearance Project",
            cabinets=cabinets,
            placements=placements,
            metadata=metadata,
        ).build()

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
