import unittest

from domain.builders import Identity, SceneNode, WardrobeBuilder
from domain.core_types import NodeCategory, NodeRole
from domain.hardware_library import HardwareRegistry
from domain.manufacturing_compiler import ManufacturingCompiler
from domain.resolvers import CoordinateResolver
from domain.rules_engine import HardwarePlacementEngine, RuleContext


class TestUniversalPhysicalManufacturingContract(unittest.TestCase):

    DEFAULT_MANUFACTURING_SKUS = (
        "HINGE_BLUM_110_V1",
        "MINIFIX_15_V1",
        "CONFIRMAT_50_V1",
        "SHELF_PIN_5MM",
        "DRAWER_SLIDE_SOFTCLOSE_450",
        "HANDLE_128_BLACK",
    )

    def test_default_manufacturing_hardware_generates_physical_machining_operations(self):
        registry = HardwareRegistry()

        for sku in self.DEFAULT_MANUFACTURING_SKUS:
            with self.subTest(sku=sku):
                project, context = self._compiled_representative_project_for_sku(sku)
                self._assert_sku_has_physical_manufacturing_coverage(
                    project,
                    context,
                    registry,
                    sku,
                )

    def test_drawer_slide_standard_profile_override_generates_physical_machining_operations(self):
        context = RuleContext()
        context.hardware_profile["INTENT_DRAWER_SLIDE"] = "DRAWER_SLIDE_STANDARD_450"
        project, context = self._compiled_representative_project_for_sku(
            "DRAWER_SLIDE_STANDARD_450",
            context,
        )
        registry = HardwareRegistry()

        self._assert_sku_has_physical_manufacturing_coverage(
            project,
            context,
            registry,
            "DRAWER_SLIDE_STANDARD_450",
        )

    def _assert_sku_has_physical_manufacturing_coverage(
        self,
        project,
        context,
        registry,
        sku,
    ):
        hardware = registry.get_hardware(sku)

        self.assertIsNotNone(hardware, f"{sku} does not exist")
        self.assertTrue(
            hardware.host_holes or hardware.target_holes,
            f"{sku} has no host_holes or target_holes",
        )

        placements = self._placements_for_sku(project, context, sku)
        self.assertTrue(placements, f"No placements found for {sku}")

        matched_ops = []
        for placement in placements:
            matched_ops.extend(
                self._assert_placement_holes_generate_physical_ops(
                    project,
                    placement,
                    hardware,
                )
            )

        self.assertTrue(matched_ops, f"No machining operations matched {sku}")
        self.assertFalse(
            self._matching_virtual_ops(project, hardware),
            f"{sku} generated matching operations on virtual nodes",
        )

    def _assert_placement_holes_generate_physical_ops(self, project, placement, hardware):
        matched_ops = []

        if hardware.host_holes:
            host_node = project.graph.get_node(placement.host_node_id)
            self.assertIsNotNone(
                host_node,
                f"Missing host node {placement.host_node_id}",
            )
            self.assertEqual(
                host_node.category,
                NodeCategory.PHYSICAL,
                f"Host node {placement.host_node_id} is not physical",
            )
            host_matches = self._matching_ops_for_holes(
                host_node,
                placement,
                hardware.host_holes,
            )
            self.assertTrue(
                host_matches,
                f"No host hole machining ops for {hardware.sku} on {placement.host_node_id}",
            )
            matched_ops.extend(host_matches)

        if hardware.target_holes:
            target_node = project.graph.get_node(getattr(placement, "target_node_id", ""))
            self.assertIsNotNone(
                target_node,
                f"Missing target node {getattr(placement, 'target_node_id', '')}",
            )
            self.assertEqual(
                target_node.category,
                NodeCategory.PHYSICAL,
                f"Target node {placement.target_node_id} is not physical",
            )
            target_matches = self._matching_ops_for_holes(
                target_node,
                placement,
                hardware.target_holes,
            )
            self.assertTrue(
                target_matches,
                f"No target hole machining ops for {hardware.sku} on {placement.target_node_id}",
            )
            matched_ops.extend(target_matches)

        return matched_ops

    @staticmethod
    def _matching_ops_for_holes(node, placement, holes):
        matches = []
        for hole in holes:
            resolved = CoordinateResolver.resolve(
                node,
                placement.anchor,
                hole.offset_x,
                hole.offset_y,
            )
            expected_face = hole.face.value if hasattr(hole.face, "value") else str(hole.face)
            expected_face = str(expected_face if expected_face else resolved.face).split(".")[-1]
            expected_axis = getattr(hole, "axis", "Z")
            expected_through = getattr(hole, "is_through_hole", False)

            for op in getattr(node, "machining_ops", []):
                actual_face = str(op.face).split(".")[-1]
                if (
                    op.op_type == "DRILL"
                    and actual_face == expected_face
                    and abs(op.local_x - resolved.local_x) < 0.1
                    and abs(op.local_y - resolved.local_y) < 0.1
                    and abs(op.diameter - hole.diameter) < 0.1
                    and abs(op.depth - hole.depth) < 0.1
                    and getattr(op, "axis", "Z") == expected_axis
                    and getattr(op, "is_through", False) == expected_through
                ):
                    matches.append(op)
                    break
        return matches

    def _matching_virtual_ops(self, project, hardware):
        virtual_matches = []
        for node in project.graph._by_category[NodeCategory.VIRTUAL]:
            for holes in (hardware.host_holes, hardware.target_holes):
                for hole in holes:
                    virtual_matches.extend(
                        self._matching_ops_by_spec(node, hole)
                    )
        return virtual_matches

    @staticmethod
    def _matching_ops_by_spec(node, hole):
        expected_face = hole.face.value if hasattr(hole.face, "value") else str(hole.face)
        expected_face = str(expected_face).split(".")[-1]
        expected_axis = getattr(hole, "axis", "Z")
        expected_through = getattr(hole, "is_through_hole", False)

        return [
            op
            for op in getattr(node, "machining_ops", [])
            if op.op_type == "DRILL"
            and str(op.face).split(".")[-1] == expected_face
            and abs(op.diameter - hole.diameter) < 0.1
            and abs(op.depth - hole.depth) < 0.1
            and getattr(op, "axis", "Z") == expected_axis
            and getattr(op, "is_through", False) == expected_through
        ]

    @staticmethod
    def _placements_for_sku(project, context, sku):
        return [
            placement
            for placement in project.placements
            if context.hardware_profile.get(placement.hardware_intent) == sku
        ]

    def _compiled_representative_project_for_sku(self, sku, context=None):
        if context is None:
            context = RuleContext()

        project = self._representative_project()

        HardwarePlacementEngine(context).process(project)
        project.placements = self._placements_for_sku(project, context, sku)
        ManufacturingCompiler().compile(project, context)

        return project, context

    def _representative_project(self):
        cabinet = WardrobeBuilder(
            uid="UNIVERSAL_PHYSICAL_MANUFACTURING_CONTRACT",
            width=1000.0,
            height=2000.0,
            depth=600.0,
        )
        cabinet.add_divider(x_offset=400.0)
        cabinet.add_shelves(count=1, section_id="ROOT")
        cabinet.add_doors(2)
        project = cabinet.build()
        self._add_drawer_faces(project)
        return project

    @staticmethod
    def _add_drawer_faces(project):
        drawer_fronts = []
        for index in range(2):
            drawer_front = SceneNode(
                Identity(f"UNIVERSAL_PHYSICAL_DRAWER_FRONT_{index + 1}"),
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


if __name__ == "__main__":
    unittest.main()
