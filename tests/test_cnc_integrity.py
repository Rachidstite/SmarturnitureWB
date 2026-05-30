import unittest
from domain.builders import WardrobeBuilder
from domain.rules_engine import HardwarePlacementEngine, RuleContext
from domain.manufacturing_compiler import ManufacturingCompiler

class TestCNCIntegrity(unittest.TestCase):
    def setUp(self):
        cabinet = WardrobeBuilder(uid="TEST_CNC", width=800, height=800, depth=400)
        self.project = cabinet.build()
        context = RuleContext()
        HardwarePlacementEngine(context).process(self.project)
        ManufacturingCompiler().compile(self.project, context)

    def test_no_duplicate_operations(self):
        """يضمن عدم وجود عمليات حفر مكررة تحرق البنطة"""
        for node in self.project.graph.physical_nodes:
            ops = getattr(node, 'machining_ops', [])
            seen_ops = set()
            for op in ops:
                op_key = f"{op.face}_{op.local_x}_{op.local_y}_{op.diameter}"
                self.assertNotIn(op_key, seen_ops, f"Duplicate MachiningOp found: {op_key} in node {node.identity.key}")
                seen_ops.add(op_key)

    def test_no_edge_boring_on_zero_x(self):
        """يضمن أن ثقوب الحواف (Edge Boring) تقع في منتصف سمك اللوح وليس على الحافة (X=0)"""
        for node in self.project.graph.physical_nodes:
            for op in getattr(node, 'machining_ops', []):
                # إذا كان الثقب الجانبي قطره 8مم (مثل المينيفكس)، يجب أن لا يكون X=0 أبداً
                if op.axis in ['X', 'Y'] and op.diameter >= 8:
                    safe_margin = op.diameter / 2.0
                    self.assertTrue(op.local_x >= safe_margin, 
                        f"CRITICAL: Edge Boring hole center ({op.local_x}) is outside or exactly on the edge of panel {node.identity.key}!")
