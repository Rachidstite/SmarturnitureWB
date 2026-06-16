import unittest
from types import SimpleNamespace

from domain.anchors import HardwarePlacement
from domain.rules_engine import DrawerSlideRule, HardwarePlacementEngine, RuleContext


class TestHardwarePlacementEngine(unittest.TestCase):

    def test_rule_context_includes_drawer_slide_intent_by_default(self):
        context = RuleContext()

        self.assertEqual(
            context.hardware_profile["INTENT_DRAWER_SLIDE"],
            "DRAWER_SLIDE_SOFTCLOSE_450",
        )

    def test_drawer_slide_rule_emits_two_placements_per_drawer_face(self):
        rule = DrawerSlideRule()
        project = self._project_with_drawer_faces(1)

        placements = rule.apply(project, RuleContext())

        self.assertEqual(len(placements), 2)
        self.assertTrue(all(isinstance(p, HardwarePlacement) for p in placements))
        self.assertEqual(
            [p.description for p in placements],
            ["Left drawer slide", "Right drawer slide"],
        )

    def test_drawer_slide_rule_emits_six_placements_for_three_drawer_faces(self):
        rule = DrawerSlideRule()
        project = self._project_with_drawer_faces(3)

        placements = rule.apply(project, RuleContext())

        self.assertEqual(len(placements), 6)
        self.assertTrue(all(p.hardware_intent == "INTENT_DRAWER_SLIDE" for p in placements))

    def test_drawer_slide_rule_emits_no_placements_when_no_drawer_faces_exist(self):
        rule = DrawerSlideRule()
        project = SimpleNamespace(
            graph=SimpleNamespace(
                _by_role={
                    self._drawer_face_role(): [],
                }
            )
        )

        placements = rule.apply(project, RuleContext())

        self.assertEqual(placements, [])

    def test_hardware_placement_engine_includes_drawer_slide_rule(self):
        engine = HardwarePlacementEngine()

        self.assertEqual(
            engine.rules[-1].__class__.__name__,
            "DrawerSlideRule",
        )

    @staticmethod
    def _project_with_drawer_faces(count):
        faces = [
            SimpleNamespace(identity=SimpleNamespace(key=f"DRAWER_{idx + 1}"))
            for idx in range(count)
        ]
        return SimpleNamespace(
            graph=SimpleNamespace(
                _by_role={
                    TestHardwarePlacementEngine._drawer_face_role(): faces,
                }
            )
        )

    @staticmethod
    def _drawer_face_role():
        return type(
            "DrawerFaceRole",
            (),
            {
                "name": "DRAWER_FACE",
                "value": "DRAWER_FACE",
                "__hash__": object.__hash__,
            },
        )()


if __name__ == "__main__":
    unittest.main()
