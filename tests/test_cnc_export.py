import unittest
import os
import csv
import tempfile
from domain.builders import WardrobeBuilder
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
