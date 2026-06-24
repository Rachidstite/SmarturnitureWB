import unittest
from dataclasses import fields, is_dataclass
from types import SimpleNamespace


class TestEngineeringComponentInventoryBuilder(unittest.TestCase):

    def setUp(self):
        from manufacturing.engineering_component_inventory_builder import (
            EngineeringComponentInventoryBuilder,
        )

        self.builder = EngineeringComponentInventoryBuilder()

    def test_builder_exists(self):
        self.assertTrue(callable(self.builder.build))

    def test_cabinet_record_contract_includes_explicit_cabinet_id(self):
        from manufacturing.engineering_component_inventory import CabinetRecord

        self.assertTrue(is_dataclass(CabinetRecord))
        self.assertEqual(
            [field.name for field in fields(CabinetRecord)],
            [
                "cabinet_id",
                "provenance",
                "width",
                "height",
                "depth",
                "thickness",
                "material",
                "warnings",
            ],
        )
        self.assertEqual(CabinetRecord().cabinet_id, "")

    def test_build_supports_furniture_project_and_aggregates_cabinets(self):
        from domain.builders import CabinetProject, Identity, SceneGraph, SceneNode
        from domain.core_types import NodeCategory, NodeRole
        from domain.furniture_project import FurnitureProject

        first_cabinet = self._cabinet_project(
            cabinet_id="CAB-1",
            width=1000.0,
            height=2000.0,
            depth=600.0,
            thickness=18.0,
            nodes=[
                self._node("CAB-1_DOOR", NodeRole.DOOR_PANEL, 700.0, 1900.0, 18.0),
                self._node("CAB-1_SHELF", NodeRole.SHELF, 800.0, 300.0, 18.0),
                self._node("CAB-1_BACK", NodeRole.BACK_PANEL, 980.0, 1980.0, 3.0),
            ],
        )
        second_cabinet = self._cabinet_project(
            cabinet_id="CAB-2",
            width=800.0,
            height=1800.0,
            depth=500.0,
            thickness=16.0,
            nodes=[
                self._node("CAB-2_DOOR_A", NodeRole.DOOR_PANEL, 400.0, 1700.0, 18.0),
                self._node("CAB-2_DOOR_B", NodeRole.DOOR_PANEL, 400.0, 1700.0, 18.0),
                self._node("CAB-2_SHELF", NodeRole.SHELF, 700.0, 250.0, 16.0),
                self._node("CAB-2_BACK", NodeRole.BACK_PANEL, 780.0, 1780.0, 3.0),
            ],
        )
        project = FurnitureProject(
            project_id="FP-1",
            name="Kitchen",
            cabinets=[first_cabinet, second_cabinet],
        )

        result = self.builder.build(project)

        self.assertEqual(len(result.cabinet_records), 2)
        self.assertEqual(
            [record.width for record in result.cabinet_records],
            [1000.0, 800.0],
        )
        self.assertEqual(
            [record.provenance.source_path for record in result.cabinet_records],
            [
                "FurnitureProject.cabinets[0].topology",
                "FurnitureProject.cabinets[1].topology",
            ],
        )
        self.assertEqual(
            [record.provenance.source_object_id for record in result.cabinet_records],
            ["CAB-1", "CAB-2"],
        )
        self.assertEqual(
            [record.cabinet_id for record in result.cabinet_records],
            ["CAB-1", "CAB-2"],
        )

        self.assertEqual(len(result.door_records), 3)
        self.assertEqual(len(result.shelf_records), 2)
        self.assertEqual(len(result.back_panel_records), 2)
        self.assertEqual(
            {
                record.provenance.source_path
                for record in result.door_records
            },
            {"FurnitureProject.cabinets[0].graph.physical_nodes", "FurnitureProject.cabinets[1].graph.physical_nodes"},
        )
        self.assertEqual(
            [
                record.provenance.source_object_id
                for record in result.door_records
            ],
            ["CAB-1_DOOR", "CAB-2_DOOR_A", "CAB-2_DOOR_B"],
        )

    def test_build_preserves_cabinet_project_behavior(self):
        from domain.builders import CabinetProject
        from domain.core_types import NodeRole

        cabinet_project = self._cabinet_project(
            cabinet_id="CABINET-PROJECT",
            width=900.0,
            height=2100.0,
            depth=580.0,
            thickness=18.0,
            nodes=[
                self._node("CABINET-PROJECT_DOOR", NodeRole.DOOR_PANEL, 450.0, 2000.0, 18.0),
                self._node("CABINET-PROJECT_BACK", NodeRole.BACK_PANEL, 880.0, 2080.0, 3.0),
            ],
        )

        result = self.builder.build(cabinet_project)

        self.assertEqual(len(result.cabinet_records), 1)
        self.assertEqual(
            result.cabinet_records[0].provenance.source_path,
            "CabinetProject.topology",
        )
        self.assertEqual(result.cabinet_records[0].cabinet_id, "CABINET-PROJECT")
        self.assertEqual(
            [record.provenance.source_path for record in result.door_records],
            ["CabinetProject.graph.physical_nodes"],
        )
        self.assertEqual(
            [record.provenance.source_path for record in result.back_panel_records],
            ["CabinetProject.graph.physical_nodes"],
        )

    def test_build_preserves_scene_graph_behavior(self):
        from domain.builders import Identity, SceneGraph, SceneNode
        from domain.core_types import NodeCategory, NodeRole

        scene_graph = SceneGraph()
        scene_graph.add_node(
            SceneNode(
                Identity("SCENE-1_DOOR"),
                NodeRole.DOOR_PANEL,
                500.0,
                1900.0,
                18.0,
                "MDF",
                category=NodeCategory.PHYSICAL,
            )
        )

        result = self.builder.build(scene_graph)

        self.assertEqual(len(result.cabinet_records), 1)
        self.assertEqual(
            result.cabinet_records[0].provenance.source_path,
            "SceneGraph.physical_nodes",
        )
        self.assertEqual(result.cabinet_records[0].cabinet_id, "")
        self.assertEqual(
            [record.provenance.source_path for record in result.door_records],
            ["SceneGraph.physical_nodes"],
        )

    def test_build_handles_empty_furniture_project_without_mutation(self):
        from domain.furniture_project import FurnitureProject

        project = FurnitureProject(
            project_id="EMPTY",
            cabinets=[],
            metadata={"keep": "original"},
        )
        original_state = {
            key: list(value) if isinstance(value, list) else dict(value) if isinstance(value, dict) else value
            for key, value in project.__dict__.items()
        }

        result = self.builder.build(project)

        self.assertEqual(result.cabinet_records, [])
        self.assertEqual(result.door_records, [])
        self.assertEqual(result.shelf_records, [])
        self.assertEqual(result.back_panel_records, [])
        self.assertEqual(project.__dict__, original_state)

    @staticmethod
    def _cabinet_project(
        *,
        cabinet_id,
        width,
        height,
        depth,
        thickness,
        nodes,
    ):
        from domain.builders import CabinetProject

        graph = SimpleNamespace(physical_nodes=list(nodes))
        topology = SimpleNamespace(
            w=width,
            h=height,
            d=depth,
            t=thickness,
        )
        cabinet_project = CabinetProject(
            graph=graph,
            joinery=SimpleNamespace(),
            topology=topology,
            placements=[],
        )
        cabinet_project.identity = SimpleNamespace(key=cabinet_id)
        return cabinet_project

    @staticmethod
    def _node(node_id, role, width, height, thickness):
        return SimpleNamespace(
            identity=SimpleNamespace(key=node_id),
            role=role,
            width=width,
            height=height,
            thickness=thickness,
            material="MDF",
            warnings=[],
        )


if __name__ == "__main__":
    unittest.main()
