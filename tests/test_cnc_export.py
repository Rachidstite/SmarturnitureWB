import unittest
import os
import csv
import tempfile
from types import SimpleNamespace

from domain.builders import Identity, WardrobeBuilder
from domain.core_types import NodeCategory, NodeRole
from domain.rules_engine import HardwarePlacementEngine, RuleContext
from domain.manufacturing_compiler import ManufacturingCompiler
from exports.cnc_exporter import CNCExporter

class TestCNCExport(unittest.TestCase):
    def test_neutral_format_and_axis_inclusion(self):
        """يتحقق من وجود صيغة محايدة وعدم ضياع بيانات المحور (Axis)"""
        cabinet = WardrobeBuilder(uid="TEST_CNC", width=800, height=800, depth=400)
        project = cabinet.build()
        
        context = RuleContext()
        HardwarePlacementEngine(context).process(project)
        ManufacturingCompiler().compile(project, context)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "drilling_map.csv")
            CNCExporter.export_master_drilling_map(project, csv_path)
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                
                # التأكد من وجود عمود Axis
                self.assertIn("Axis", headers)
                
                rows = list(reader)
                
                # التأكد من وجود ثقوب أفقية (Axis=X أو Y) للمينيفكس
                has_horizontal_boring = any(row["Axis"] in ["X", "Y"] for row in rows)
                self.assertTrue(has_horizontal_boring, "Failed to export Edge Boring (Axis X/Y) operations!")

    def test_export_includes_drawer_slide_drilling_ops(self):
        project = self._project_with_one_drawer_face()
        context = RuleContext()

        HardwarePlacementEngine(context).process(project)
        ManufacturingCompiler().compile(project, context)

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "drilling_map.csv")
            CNCExporter.export_master_drilling_map(project, csv_path)

            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

        drawer_slide_rows = [
            row
            for row in rows
            if float(row["Diameter"]) == 3.0 and float(row["Depth"]) == 12.0
        ]

        self.assertEqual(len(drawer_slide_rows), 2)
        self.assertTrue(all(row["Axis"] == "Z" for row in drawer_slide_rows))

    def test_export_includes_handle_drilling_ops(self):
        project = self._project_with_handle_panels()
        context = RuleContext()

        HardwarePlacementEngine(context).process(project)
        ManufacturingCompiler().compile(project, context)

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "drilling_map.csv")
            CNCExporter.export_master_drilling_map(project, csv_path)

            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

        handle_rows = [
            row
            for row in rows
            if float(row["Diameter"]) == 5.0 and float(row["Depth"]) == 18.0
        ]

        self.assertEqual(len(handle_rows), 4)
        self.assertTrue(all(row["Face"] == "FRONT" for row in handle_rows))

    @staticmethod
    def _project_with_one_drawer_face():
        from domain.builders import CabinetProject, SceneGraph, SceneNode

        graph = SceneGraph()
        project = CabinetProject(
            graph=graph,
            joinery=SimpleNamespace(edges=[]),
            topology=SimpleNamespace(),
            placements=[],
        )

        drawer_face = SceneNode(
            Identity("DRAWER_FACE_1"),
            NodeRole.UNKNOWN,
            400.0,
            200.0,
            18.0,
            "MDF_18_WHITE",
        )
        graph.nodes.append(drawer_face)
        graph._by_id[drawer_face.identity.key] = drawer_face
        graph._by_category[NodeCategory.PHYSICAL].append(drawer_face)

        drawer_role = type(
            "DrawerFaceRole",
            (),
            {
                "name": "DRAWER_FACE",
                "value": "DRAWER_FACE",
                "__hash__": object.__hash__,
            },
        )()
        graph._by_role[drawer_role] = [drawer_face]
        return project

    @staticmethod
    def _project_with_handle_panels():
        from domain.builders import CabinetProject, SceneGraph, SceneNode

        graph = SceneGraph()
        project = CabinetProject(
            graph=graph,
            joinery=SimpleNamespace(edges=[]),
            topology=SimpleNamespace(),
            placements=[],
        )

        door = SceneNode(
            Identity("DOOR_1"),
            NodeRole.DOOR_PANEL,
            500.0,
            700.0,
            18.0,
            "MDF_18_WHITE",
        )
        drawer_front = SceneNode(
            Identity("DRAWER_FRONT_1"),
            NodeRole.DRAWER_FRONT,
            500.0,
            180.0,
            18.0,
            "MDF_18_WHITE",
        )
        graph.add_node(door)
        graph.add_node(drawer_front)
        return project
