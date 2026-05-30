import unittest
from domain.builders import SceneNode, Identity
from domain.core_types import NodeRole
from domain.anchors import AnchorCoordinate, MountFace, EdgeRef
from domain.resolvers import CoordinateResolver

class TestCoordinateResolver(unittest.TestCase):
    def setUp(self):
        # لوح قياسي 500x800x18
        self.node = SceneNode(
            identity=Identity("TEST_PANEL"),
            role=NodeRole.SIDE_PANEL,
            width=500.0,
            height=800.0,
            thickness=18.0,
            material="MDF"
        )

    def test_left_bottom_anchor(self):
        anchor = AnchorCoordinate(MountFace.FRONT, EdgeRef.LEFT, offset_x=37.0, offset_y=100.0)
        # Assuming fallback for Y is BOTTOM if EdgeRef is LEFT
        anchor.edge = EdgeRef.BOTTOM # Simplified for test context
        
        resolved = CoordinateResolver.resolve(self.node, anchor, hole_offset_x=0, hole_offset_y=0)
        self.assertEqual(resolved.local_x, 37.0)
        self.assertEqual(resolved.local_y, 100.0)

    def test_right_top_anchor_associativity(self):
        # قياس 50 ملم من اليمين، و 100 ملم من الأعلى
        anchor = AnchorCoordinate(MountFace.FRONT, EdgeRef.RIGHT, offset_x=50.0, offset_y=100.0)
        
        # Testing Right Edge Logic
        resolved_x = CoordinateResolver.resolve(self.node, anchor).local_x
        self.assertEqual(resolved_x, 450.0) # 500 - 50 = 450
        
        # Testing Top Edge Logic
        anchor.edge = EdgeRef.TOP
        resolved_y = CoordinateResolver.resolve(self.node, anchor).local_y
        self.assertEqual(resolved_y, 700.0) # 800 - 100 = 700

    def test_center_anchor(self):
        anchor = AnchorCoordinate(MountFace.FRONT, EdgeRef.CENTER, offset_x=0.0, offset_y=0.0)
        resolved = CoordinateResolver.resolve(self.node, anchor)
        
        self.assertEqual(resolved.local_x, 250.0) # 500 / 2
        self.assertEqual(resolved.local_y, 400.0) # 800 / 2
        
    def test_hinge_cup_offset_math(self):
        """محاكاة حساب ثقوب براغي المفصلة نسبة لمركز الكأس"""
        # الارتساء الدلالي: من الأسفل بـ 100مم، ومن اليسار بـ 22مم
        anchor = AnchorCoordinate(MountFace.BACK, EdgeRef.BOTTOM, offset_x=22.0, offset_y=100.0)
        
        # ثقب الكأس (بدون إزاحة)
        resolved_cup = CoordinateResolver.resolve(self.node, anchor, hole_offset_x=0, hole_offset_y=0)
        self.assertEqual(resolved_cup.local_x, 22.0)
        self.assertEqual(resolved_cup.local_y, 100.0)
        
        # ثقب برغي المفصلة العلوي (إزاحة -9.5 في الـ X و +22.5 في الـ Y بناءً على مواصفات Blum)
        resolved_screw = CoordinateResolver.resolve(self.node, anchor, hole_offset_x=-9.5, hole_offset_y=22.5)
        self.assertEqual(resolved_screw.local_x, 12.5) # 22 - 9.5
        self.assertEqual(resolved_screw.local_y, 122.5) # 100 + 22.5
