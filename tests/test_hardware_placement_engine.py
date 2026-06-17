import unittest
from types import SimpleNamespace

from domain.anchors import HardwarePlacement, MountFace
from domain.builders import CabinetProject, Identity, SceneGraph, SceneNode
from domain.core_types import NodeCategory, NodeRole
from domain.manufacturing_compiler import ManufacturingCompiler
from domain.rules_engine import (
    DrawerSlideRule,
    HandleRule,
    HardwarePlacementEngine,
    RuleContext,
)


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

    def test_handle_rule_generates_placements_for_doors_and_drawer_fronts(self):
        project = self._project_with_handle_panels()

        placements = HandleRule().apply(project, RuleContext())

        self.assertEqual(len(placements), 2)
        self.assertTrue(all(p.hardware_intent == "INTENT_HANDLE" for p in placements))
        self.assertEqual(
            {p.host_node_id for p in placements},
            {"DOOR_1", "DRAWER_FRONT_1"},
        )
        self.assertTrue(all(p.anchor.face == MountFace.FRONT for p in placements))
        self.assertTrue(all(p.anchor.edge.name == "CENTER" for p in placements))

    def test_drawer_slide_placements_compile_into_machining_ops(self):
        project = self._project_with_one_drawer_face()
        context = RuleContext()

        HardwarePlacementEngine(context).process(project)
        self.assertEqual(len(project.placements), 2)

        ManufacturingCompiler().compile(project, context)

        drawer_face = project.graph.get_node("DRAWER_FACE_1")
        self.assertEqual(len(drawer_face.machining_ops), 2)
        self.assertTrue(all(op.op_type == "DRILL" for op in drawer_face.machining_ops))
        self.assertTrue(all(op.diameter == 3.0 for op in drawer_face.machining_ops))
        self.assertTrue(all(op.depth == 12.0 for op in drawer_face.machining_ops))
        self.assertEqual({op.face for op in drawer_face.machining_ops}, {"LEFT"})
        self.assertEqual(
            {op.local_y for op in drawer_face.machining_ops},
            {50.0, 350.0},
        )

    def test_handle_placements_compile_into_machining_ops(self):
        project = self._project_with_handle_panels()
        context = RuleContext()

        HardwarePlacementEngine(context).process(project)
        ManufacturingCompiler().compile(project, context)

        door = project.graph.get_node("DOOR_1")
        drawer_front = project.graph.get_node("DRAWER_FRONT_1")

        for node in [door, drawer_front]:
            handle_ops = [
                op for op in node.machining_ops
                if op.diameter == 5.0
                and op.depth == 18.0
                and op.face == "FRONT"
            ]

            self.assertEqual(len(handle_ops), 2)
            self.assertTrue(all(op.op_type == "DRILL" for op in handle_ops))
            self.assertEqual(
                {op.local_y for op in handle_ops},
                {node.height / 2.0 - 64.0, node.height / 2.0 + 64.0},
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

    @staticmethod
    def _project_with_one_drawer_face():
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


if __name__ == "__main__":
    unittest.main()
