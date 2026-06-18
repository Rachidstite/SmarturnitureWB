import unittest

from domain.builders import Identity, SceneNode, WardrobeBuilder
from domain.core_types import NodeRole
from domain.hardware_library import HardwareRegistry
from domain.manufacturing_compiler import ManufacturingCompiler
from domain.resolvers import CoordinateResolver
from domain.rules_engine import HardwarePlacementEngine, RuleContext


class TestUniversalHardwareMarkingCoverage(unittest.TestCase):

    def test_all_hardware_placements_have_registry_specs_and_machining_marks(self):
        project = self._project_with_doors_drawers_and_minifix_joinery()
        context = RuleContext()
        registry = HardwareRegistry()

        HardwarePlacementEngine(context).process(project)
        ManufacturingCompiler().compile(project, context)

        self.assertGreater(len(project.placements), 0)
        self.assert_required_intents_present(project.placements)

        for placement in project.placements:
            self.assertTrue(
                placement.hardware_intent,
                f"Placement missing hardware_intent: {placement}",
            )

            sku = context.hardware_profile.get(placement.hardware_intent)
            self.assertIsNotNone(
                sku,
                f"{placement.hardware_intent} is not mapped in hardware_profile",
            )

            hardware_spec = registry.get_hardware(sku)
            self.assertIsNotNone(
                hardware_spec,
                f"{sku} does not exist in HardwareRegistry",
            )
            self.assert_spec_has_holes_or_visual_marking_requirement(sku, hardware_spec)
            self.assert_placement_has_machining_op(project, placement, hardware_spec)

        self.assert_drawer_slides_mark_side_panels(project)
        self.assert_hinges_mark_door_panels(project)
        self.assert_handles_mark_door_and_drawer_fronts(project)
        self.assert_minifix_marks_15mm_and_8mm_holes(project)

    @staticmethod
    def _project_with_doors_drawers_and_minifix_joinery():
        cabinet = WardrobeBuilder(
            uid="UNIVERSAL_HARDWARE_COVERAGE",
            width=1000,
            height=2000,
            depth=600,
        )
        cabinet.add_doors(2)
        project = cabinet.build()

        drawer_fronts = []
        for index in range(2):
            drawer_front = SceneNode(
                Identity(f"UNIVERSAL_HARDWARE_COVERAGE_DRAWER_FRONT_{index + 1}"),
                NodeRole.DRAWER_FRONT,
                450.0,
                180.0,
                18.0,
                "MDF_18_WHITE",
            )
            project.graph.add_node(drawer_front)
            drawer_fronts.append(drawer_front)

        drawer_face_role = type(
            "DrawerFaceRole",
            (),
            {
                "name": "DRAWER_FACE",
                "value": "DRAWER_FACE",
                "__hash__": object.__hash__,
            },
        )()
        project.graph._by_role[drawer_face_role] = drawer_fronts
        return project

    def assert_required_intents_present(self, placements):
        intents = {placement.hardware_intent for placement in placements}

        self.assertIn("INTENT_HINGE", intents)
        self.assertIn("INTENT_HANDLE", intents)
        self.assertIn("INTENT_DRAWER_SLIDE", intents)
        self.assertIn("INTENT_MINIFIX_15", intents)

    def assert_spec_has_holes_or_visual_marking_requirement(self, sku, hardware_spec):
        has_holes = bool(hardware_spec.host_holes or hardware_spec.target_holes)
        has_visual_marking_requirement = any(
            bool(getattr(hardware_spec, attr_name, False))
            for attr_name in (
                "visual_marking_required",
                "visual_marking",
                "requires_visual_marking",
            )
        )

        self.assertTrue(
            has_holes or has_visual_marking_requirement,
            f"{sku} has no host_holes, target_holes, or visual marking requirement",
        )

    def assert_placement_has_machining_op(self, project, placement, hardware_spec):
        expected_matches = []

        host_node = project.graph.get_node(placement.host_node_id)
        if host_node:
            expected_matches.extend(
                self._expected_ops_for_holes(
                    host_node,
                    placement,
                    hardware_spec.host_holes,
                )
            )

        target_node = project.graph.get_node(getattr(placement, "target_node_id", ""))
        if target_node:
            expected_matches.extend(
                self._expected_ops_for_holes(
                    target_node,
                    placement,
                    hardware_spec.target_holes,
                )
            )

        self.assertTrue(
            expected_matches,
            f"{hardware_spec.sku} placement has no host or target hole expectations",
        )
        self.assertTrue(
            any(matches_node_ops for matches_node_ops in expected_matches),
            f"No machining_op generated for placement {placement}",
        )

    @staticmethod
    def _expected_ops_for_holes(node, placement, holes):
        matches = []
        for hole in holes:
            resolved = CoordinateResolver.resolve(
                node,
                placement.anchor,
                hole.offset_x,
                hole.offset_y,
            )
            face = hole.face.value if hasattr(hole.face, "value") else str(hole.face)
            face = str(face if face else resolved.face).split(".")[-1]

            matches.append(
                any(
                    str(op.face).split(".")[-1] == face
                    and abs(op.local_x - resolved.local_x) < 0.1
                    and abs(op.local_y - resolved.local_y) < 0.1
                    and abs(op.diameter - hole.diameter) < 0.1
                    for op in getattr(node, "machining_ops", [])
                )
            )
        return matches

    def assert_drawer_slides_mark_side_panels(self, project):
        side_panel_ops = [
            op
            for node in project.graph._by_role[NodeRole.SIDE_PANEL]
            for op in getattr(node, "machining_ops", [])
        ]

        self.assertTrue(
            any(
                op.op_type == "DRILL"
                and abs(op.diameter - 3.0) < 0.1
                and abs(op.depth - 12.0) < 0.1
                for op in side_panel_ops
            ),
            "Drawer slide placements must generate screw holes on side panels",
        )

    def assert_hinges_mark_door_panels(self, project):
        door_ops = [
            op
            for node in project.graph._by_role[NodeRole.DOOR_PANEL]
            for op in getattr(node, "machining_ops", [])
        ]

        self.assertTrue(
            any(
                op.op_type == "DRILL"
                and abs(op.diameter - 35.0) < 0.1
                and abs(op.depth - 12.5) < 0.1
                for op in door_ops
            ),
            "Hinge placements must generate 35mm cup holes on door panels",
        )

    def assert_handles_mark_door_and_drawer_fronts(self, project):
        for role in (NodeRole.DOOR_PANEL, NodeRole.DRAWER_FRONT):
            role_ops = [
                op
                for node in project.graph._by_role[role]
                for op in getattr(node, "machining_ops", [])
            ]

            self.assertTrue(
                any(
                    op.op_type == "DRILL"
                    and abs(op.diameter - 5.0) < 0.1
                    and abs(op.depth - 18.0) < 0.1
                    and str(op.face).split(".")[-1] == "FRONT"
                    for op in role_ops
                ),
                f"Handle placements must generate handle drill holes on {role.value}",
            )

    def assert_minifix_marks_15mm_and_8mm_holes(self, project):
        minifix_ops = [
            op
            for node in project.graph.physical_nodes
            for op in getattr(node, "machining_ops", [])
            if abs(op.diameter - 15.0) < 0.1 or abs(op.diameter - 8.0) < 0.1
        ]

        self.assertTrue(
            any(abs(op.diameter - 15.0) < 0.1 for op in minifix_ops),
            "Minifix placements must generate 15mm holes",
        )
        self.assertTrue(
            any(abs(op.diameter - 8.0) < 0.1 for op in minifix_ops),
            "Minifix placements must generate 8mm holes",
        )


if __name__ == "__main__":
    unittest.main()
