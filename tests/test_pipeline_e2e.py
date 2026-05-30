import unittest
import os
import tempfile
from domain.builders import WardrobeBuilder
from domain.rules_engine import HardwarePlacementEngine, RuleContext
from domain.manufacturing_compiler import ManufacturingCompiler
from domain.constraint_engine import CabinetConstraintValidator
from exports.cnc_exporter import CNCExporter
from exports.bom_exporter import BOMExporter

class TestEndToEndPipeline(unittest.TestCase):
    def test_golden_master_kitchen_corner(self):
        """اختبار E2E: يبني خزانة، يطبق القواعد، يولد الثقوب، يفحصها، ويستخرج CNC"""
        
        # 1. Build Geometry & Topology
        cabinet = WardrobeBuilder(uid="E2E_TEST", width=1000, height=2000, depth=600)
        left_id, right_id = cabinet.add_divider(500)
        cabinet.add_shelves(count=2, section_id=left_id)
        project = cabinet.build()

        # 2. Hardware Rules Engine
        context = RuleContext()
        placement_engine = HardwarePlacementEngine(context)
        placement_engine.process(project)

        # 3. Manufacturing Compiler
        compiler = ManufacturingCompiler()
        compiler.compile(project, context)

        # 4. Validation Shield
        validator = CabinetConstraintValidator(project)
        report = validator.validate_all()

        # 🔍 DIAGNOSTIC DUMP
        if report.has_fatals:
            print("\n" + "🔥"*25)
            print("🔍 FATAL VALIDATION REPORT DUMP:")
            for v in getattr(report, 'violations', []):
                if hasattr(v, 'severity') and v.severity.name == 'FATAL':
                    print(f"[FATAL] Code: {v.code} | Node: {getattr(v, 'node_id', 'N/A')}")
                    print(f"        Message: {getattr(v, 'message', '')}")
                    print(f"        Current: {getattr(v, 'current_value', 'N/A')} | Required: {getattr(v, 'required_value', 'N/A')}")
            print("🔥"*25 + "\n")

        self.assertFalse(report.has_fatals, "Pipeline blocked by fatal math errors.")

        # 5. CNC Export
        with tempfile.TemporaryDirectory() as tmpdirname:
            cnc_path = os.path.join(tmpdirname, "cnc_drilling_map.csv")
            CNCExporter.export_master_drilling_map(project, cnc_path)
            self.assertTrue(os.path.exists(cnc_path))
            
            with open(cnc_path, 'r') as f:
                lines = f.readlines()
                self.assertTrue(len(lines) > 1, "CNC export yielded no operations!")
        # 6. BOM Export
        bom_path = os.path.join(tmpdirname, "hardware_bom.csv")
        BOMExporter.export_hardware_bom(project, context, bom_path)
        self.assertTrue(os.path.exists(bom_path))
        with open(bom_path, 'r') as f:
            lines = f.readlines()
            self.assertTrue(len(lines) > 1, "BOM export yielded no hardware!")

