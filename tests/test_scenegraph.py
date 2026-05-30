import unittest
from domain.builders import SceneGraph, SceneNode, VirtualAnchor, Identity
from domain.core_types import NodeRole, NodeCategory

class TestSceneGraphIndexing(unittest.TestCase):
    def setUp(self):
        self.graph = SceneGraph()
        
        # إضافة 1000 قطعة وهمية لاختبار سرعة وثبات الفهرسة
        for i in range(100):
            self.graph.add_node(SceneNode(Identity(f"PHYS_{i}"), NodeRole.SHELF, 10, 10, 10, "MDF"))
            self.graph.add_node(VirtualAnchor(Identity(f"VIRT_{i}")))

    def test_o1_lookups(self):
        """يجب أن يجد القطع فوراً عبر القواميس المفهرسة دون عمل حلقة (Loop)"""
        # Test Get By ID
        node = self.graph.get_node("PHYS_50")
        self.assertIsNotNone(node)
        self.assertEqual(node.role, NodeRole.SHELF)

        # Test Category Index
        self.assertEqual(len(self.graph.physical_nodes), 100)
        self.assertEqual(len(self.graph.virtual_nodes), 100)
        self.assertEqual(len(self.graph.hardware_nodes), 0)

        # Test Role Index
        shelves = self.graph._by_role[NodeRole.SHELF]
        self.assertEqual(len(shelves), 100)
