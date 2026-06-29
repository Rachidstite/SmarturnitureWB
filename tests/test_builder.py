import unittest
from domain.builders import CabinetProject, SceneGraph, SceneNode, package_cabinet_project, WardrobeBuilder
from domain.constraint_engine import CabinetConstraintValidator
from domain.core_types import NodeRole

class TestWardrobeBuilder(unittest.TestCase):
    def test_basic_carcass(self):
        """التأكد من أن الهيكل الأساسي يحتوي على 4 قطع (جانبين، سقف، قاعدة)"""
        cabinet = WardrobeBuilder(uid="TEST1", width=1000, height=1000, depth=500)
        project = cabinet.build()
        # ⚡ تم التحديث: نعد الألواح الفيزيائية فقط (نتجاهل VirtualAnchors)
        self.assertEqual(len(project.graph.physical_nodes), 5)
        
    def test_divider_and_shelves(self):
        """التأكد من توليد الرفوف وارتباطها بالتجميع"""
        cabinet = WardrobeBuilder(uid="TEST2", width=1200, height=2000, depth=600)
        left_id, right_id = cabinet.add_divider(600)
        cabinet.add_shelves(count=3, section_id=left_id)
        
        project = cabinet.build()
        # 4 carcass + 1 divider + 3 shelves = 8 physical nodes
        self.assertEqual(len(project.graph.physical_nodes), 9)
        
        # التأكد من عدم ضياع Joinery
        edges = project.joinery.edges
        self.assertTrue(len(edges) > 4)

    def test_math_validation(self):
        """التأكد من أن الخزانة تمر من الفحص الهندسي بنجاح"""
        cabinet = WardrobeBuilder(uid="TEST3", width=1200, height=2000, depth=600)
        project = cabinet.build()
        
        validator = CabinetConstraintValidator(project)
        report = validator.validate_all()
        self.assertFalse(report.has_fatals)

    def test_divider_shelves_doors_back_panel_counts_remain_stable(self):
        cabinet = WardrobeBuilder(uid="TEST3B", width=1200, height=2000, depth=600)
        left_id, _right_id = cabinet.add_divider(600)
        cabinet.add_shelves(count=3, section_id=left_id)
        cabinet.add_doors(count=2)

        project = cabinet.build()
        by_role = project.graph._by_role

        self.assertEqual(len(project.graph.physical_nodes), 11)
        self.assertEqual(len(by_role[NodeRole.SIDE_PANEL]), 2)
        self.assertEqual(len(by_role[NodeRole.TOP_PANEL]), 1)
        self.assertEqual(len(by_role[NodeRole.BOTTOM_PANEL]), 1)
        self.assertEqual(len(by_role[NodeRole.BACK_PANEL]), 1)
        self.assertEqual(len(by_role[NodeRole.DIVIDER]), 1)
        self.assertEqual(len(by_role[NodeRole.SHELF]), 3)
        self.assertEqual(len(by_role[NodeRole.DOOR_PANEL]), 2)

    def test_wardrobe_builder_shelves_clear_the_back_panel_zone(self):
        cabinet = WardrobeBuilder(uid="TEST3C", width=1200, height=2000, depth=600)
        left_id, _right_id = cabinet.add_divider(600)
        cabinet.add_shelves(count=1, section_id=left_id)

        project = cabinet.build()
        shelf = project.graph._by_role[NodeRole.SHELF][0]
        back = project.graph._by_role[NodeRole.BACK_PANEL][0]

        self.assertEqual(shelf.transform.y, cabinet.t)
        self.assertGreater(shelf.transform.y, back.transform.y)
        self.assertEqual(len(project.graph._by_role[NodeRole.SHELF]), 1)
        self.assertEqual(len(project.graph._by_role[NodeRole.BACK_PANEL]), 1)

    def test_packaging_helper_preserves_project_shape(self):
        graph = SceneGraph()
        joinery = object()
        topology = object()
        placements = [{"intent": "shelf"}]

        project = package_cabinet_project(graph, joinery, topology, placements)

        self.assertIsInstance(project, CabinetProject)
        self.assertIs(project.graph, graph)
        self.assertIs(project.joinery, joinery)
        self.assertIs(project.topology, topology)
        self.assertEqual(project.placements, placements)
        self.assertIsNot(project.placements, placements)

    def test_wardrobe_builder_build_still_returns_same_project_shape(self):
        cabinet = WardrobeBuilder(uid="TEST4", width=1200, height=2000, depth=600)
        project = cabinet.build()

        self.assertIsInstance(project, CabinetProject)
        self.assertIs(project.graph, cabinet.graph)
        self.assertIs(project.joinery, cabinet.joinery)
        self.assertIs(project.topology, cabinet.topology)
        self.assertEqual(project.placements, [])

        self.assertGreaterEqual(len(project.graph.physical_nodes), 5)
        self.assertTrue(any(node.identity.key.endswith("_BACK") for node in project.graph.physical_nodes))
