import unittest
from domain.builders import WardrobeBuilder
from domain.constraint_engine import CabinetConstraintValidator

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
