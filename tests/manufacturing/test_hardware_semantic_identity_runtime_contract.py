import inspect
import unittest
from types import SimpleNamespace


class TestHardwareSemanticIdentityRuntimeContract(unittest.TestCase):

    def test_minifix_identity_should_survive_runtime_pipeline(self):
        project, context = self._minifix_project()
        self._assert_runtime_identity_survives(
            project,
            context,
            intent="INTENT_MINIFIX_15",
            expected_family="MINIFIX",
            expected_sku="MINIFIX_15_V1",
        )

    def test_confirmat_identity_should_survive_runtime_pipeline(self):
        project, context = self._confirmat_project()
        self._assert_runtime_identity_survives(
            project,
            context,
            intent="INTENT_CONFIRMAT_50",
            expected_family="CONFIRMAT",
            expected_sku="CONFIRMAT_50_V1",
        )

    def test_shelf_pin_identity_should_survive_runtime_pipeline(self):
        project, context = self._shelf_pin_project()
        self._assert_runtime_identity_survives(
            project,
            context,
            intent="INTENT_SHELF_PIN",
            expected_family="SHELF_PIN",
            expected_sku="SHELF_PIN_5MM",
        )

    def test_drawer_slide_identity_should_survive_runtime_pipeline(self):
        project, context = self._drawer_slide_project()
        self._assert_runtime_identity_survives(
            project,
            context,
            intent="INTENT_DRAWER_SLIDE",
            expected_family="DRAWER_SLIDE",
            expected_sku="DRAWER_SLIDE_SOFTCLOSE_450",
        )

    def test_visualization_layer_must_not_infer_family_from_geometry_without_metadata(self):
        from scene_graph.manufacturing_marker_builder import ManufacturingMarkerBuilder

        node = SimpleNamespace(identity=SimpleNamespace(key="GENERIC_NODE"))
        operations = [
            SimpleNamespace(
                op_type="DRILL",
                diameter=15.0,
                depth=14.0,
                face="LEFT",
                metadata={},
            ),
            SimpleNamespace(
                op_type="DRILL",
                diameter=8.0,
                depth=34.0,
                face="LEFT",
                metadata={},
            ),
        ]

        markers = ManufacturingMarkerBuilder.build(node, operations)

        self.assertEqual([marker.operation_type for marker in markers], ["DRILL", "DRILL"])
        self.assertTrue(all(marker.visual_type == "ANNOTATION" for marker in markers))
        self.assertEqual(
            inspect.getsource(ManufacturingMarkerBuilder).count("hardware_family"),
            0,
        )

    def _assert_runtime_identity_survives(
        self,
        project,
        context,
        intent,
        expected_family,
        expected_sku,
    ):
        from domain.hardware_library import HardwareRegistry
        from domain.manufacturing_compiler import ManufacturingCompiler
        from manufacturing.extractor import ManufacturingExtractor
        from manufacturing.manufacturing_runtime_pipeline_builder import (
            ManufacturingRuntimePipelineBuilder,
        )

        registry = HardwareRegistry()
        hardware = registry.get_hardware(expected_sku)

        self.assertIsNotNone(hardware)
        self.assertEqual(getattr(hardware, "hardware_family", ""), expected_family)

        self._apply_placements(project, context, intent)
        self.assertTrue(
            any(
                placement.hardware_intent == intent
                for placement in getattr(project, "placements", [])
            )
        )

        ManufacturingCompiler().compile(project, context)

        source_ops = self._runtime_ops_for_intent(project, intent)
        self.assertTrue(source_ops)
        self.assertEqual(source_ops[0].metadata["hardware_family"], expected_family)
        self.assertEqual(source_ops[0].metadata["hardware_sku"], expected_sku)
        self.assertEqual(source_ops[0].metadata["hardware_intent"], intent)

        panel_specs = ManufacturingExtractor.extract(project.graph)
        extracted_ops = self._panel_ops_for_intent(panel_specs, intent)
        self.assertTrue(extracted_ops)
        self.assertEqual(extracted_ops[0].metadata["hardware_family"], expected_family)
        self.assertEqual(extracted_ops[0].metadata["hardware_sku"], expected_sku)
        self.assertEqual(extracted_ops[0].metadata["hardware_intent"], intent)

        runtime = ManufacturingRuntimePipelineBuilder().build(project.graph)
        runtime_ops = self._runtime_package_ops_for_intent(runtime, intent)
        self.assertTrue(runtime_ops)
        self.assertEqual(runtime_ops[0].metadata["hardware_family"], expected_family)
        self.assertEqual(runtime_ops[0].metadata["hardware_sku"], expected_sku)
        self.assertEqual(runtime_ops[0].metadata["hardware_intent"], intent)

    @staticmethod
    def _apply_placements(project, context, intent):
        from domain.core_types import JoineryType
        from domain.rules_engine import HardwarePlacementEngine, ShelfSupportRule, RuleContext, System32JoineryRule

        if intent == "INTENT_MINIFIX_15":
            HardwarePlacementEngine(
                RuleContext(preferred_connector=JoineryType.MINIFIX_15)
            ).process(project)
            return

        if intent == "INTENT_CONFIRMAT_50":
            placements = [
                placement
                for placement in System32JoineryRule().apply(project, context)
                if placement.hardware_intent == intent
            ]
            project.placements.extend(placements)
            return

        if intent == "INTENT_SHELF_PIN":
            project.placements.extend(ShelfSupportRule().apply(project, context))
            return

        if intent == "INTENT_DRAWER_SLIDE":
            HardwarePlacementEngine(context).process(project)
            return

        raise AssertionError(f"Unexpected intent: {intent}")

    @staticmethod
    def _runtime_ops_for_intent(project, intent):
        return [
            op
            for node in project.graph.physical_nodes
            for op in getattr(node, "machining_ops", [])
            if getattr(op, "op_type", "") == "DRILL"
            and getattr(op, "metadata", {}).get("hardware_intent") == intent
        ]

    @staticmethod
    def _panel_ops_for_intent(panel_specs, intent):
        return [
            op
            for spec in panel_specs
            for op in spec.cnc_operations
            if TestHardwareSemanticIdentityRuntimeContract._operation_type(op)
            == "DRILL"
            and getattr(op, "metadata", {}).get("hardware_intent") == intent
        ]

    @staticmethod
    def _runtime_package_ops_for_intent(runtime, intent):
        return [
            op
            for op in runtime.manufacturing_package.machining_operations
            if TestHardwareSemanticIdentityRuntimeContract._operation_type(op)
            == "DRILL"
            and getattr(op, "metadata", {}).get("hardware_intent") == intent
        ]

    @staticmethod
    def _operation_type(operation):
        return getattr(
            operation,
            "operation_type",
            getattr(operation, "op_type", ""),
        )

    @staticmethod
    def _minifix_project():
        from domain.builders import WardrobeBuilder

        project = WardrobeBuilder(
            uid="MINIFIX_RUNTIME_IDENTITY_CONTRACT",
            width=1000.0,
            height=2000.0,
            depth=600.0,
        ).build()
        from domain.rules_engine import RuleContext

        return project, RuleContext()

    @staticmethod
    def _confirmat_project():
        from domain.builders import WardrobeBuilder
        from domain.rules_engine import RuleContext

        cabinet = WardrobeBuilder(
            uid="CONFIRMAT_RUNTIME_IDENTITY_CONTRACT",
            width=1000.0,
            height=2000.0,
            depth=600.0,
        )
        cabinet.add_divider(x_offset=400.0)
        return cabinet.build(), RuleContext()

    @staticmethod
    def _shelf_pin_project():
        from domain.builders import WardrobeBuilder
        from domain.rules_engine import RuleContext

        project = WardrobeBuilder(
            uid="SHELF_PIN_RUNTIME_IDENTITY_CONTRACT",
            width=800.0,
            height=2000.0,
            depth=580.0,
        )
        project.add_shelves(count=1, section_id="ROOT")
        return project.build(), RuleContext()

    @staticmethod
    def _drawer_slide_project():
        from domain.builders import CabinetProject, Identity, SceneGraph, SceneNode
        from domain.core_types import NodeCategory, NodeRole

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

        from domain.rules_engine import RuleContext

        return project, RuleContext()


if __name__ == "__main__":
    unittest.main()
