import unittest

from types import SimpleNamespace

from domain.builders import CabinetProject, Identity, SceneGraph, SceneNode
from domain.core_types import NodeCategory, NodeRole
from domain.hardware_library import HardwareRegistry
from domain.manufacturing_compiler import ManufacturingCompiler
from domain.rules_engine import HardwarePlacementEngine, RuleContext
from manufacturing.extractor import ManufacturingExtractor
from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)


class TestDrawerSlideRuntimePackageContract(unittest.TestCase):

    def test_drawer_slide_drilling_survives_into_runtime_manufacturing_package(self):
        project = self._project_with_drawer_face()
        context = RuleContext()
        registry = HardwareRegistry()
        hardware = registry.get_hardware("DRAWER_SLIDE_SOFTCLOSE_450")

        self.assertIsNotNone(hardware)
        self.assertTrue(hardware.host_holes or hardware.target_holes)

        HardwarePlacementEngine(context).process(project)
        self.assertTrue(project.placements)
        self.assertTrue(
            any(
                placement.hardware_intent == "INTENT_DRAWER_SLIDE"
                for placement in project.placements
            )
        )

        ManufacturingCompiler().compile(project, context)

        source_ops = self._drawer_slide_ops_from_nodes(project)
        self.assertTrue(source_ops)

        panel_specs = ManufacturingExtractor.extract(project.graph)
        extracted_ops = [
            op
            for spec in panel_specs
            for op in spec.cnc_operations
            if self._is_drawer_slide_drill(op)
        ]
        self.assertTrue(extracted_ops)
        self.assertEqual(
            self._operation_signatures(extracted_ops),
            self._operation_signatures(source_ops),
        )

        runtime = ManufacturingRuntimePipelineBuilder().build(project.graph)
        runtime_ops = [
            op
            for op in runtime.manufacturing_package.machining_operations
            if self._is_drawer_slide_runtime_operation(op)
        ]

        self.assertTrue(runtime_ops)
        self.assertEqual(
            self._operation_signatures(runtime_ops),
            self._operation_signatures(source_ops),
        )

    @staticmethod
    def _project_with_drawer_face():
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
    def _drawer_slide_ops_from_nodes(project):
        ops = []
        for node in project.graph.physical_nodes:
            ops.extend(
                op
                for op in getattr(node, "machining_ops", [])
                if TestDrawerSlideRuntimePackageContract._is_drawer_slide_drill(op)
            )
        return ops

    @staticmethod
    def _is_drawer_slide_drill(operation):
        if getattr(operation, "op_type", "") != "DRILL":
            return False

        return (
            abs(float(getattr(operation, "diameter", 0.0)) - 3.0) < 0.1
            and abs(float(getattr(operation, "depth", 0.0)) - 12.0) < 0.1
            and str(getattr(operation, "face", "")).split(".")[-1] == "LEFT"
        )

    @staticmethod
    def _is_drawer_slide_runtime_operation(operation):
        if getattr(operation, "operation_type", "") != "DRILL":
            return False

        return (
            abs(float(getattr(operation, "diameter", 0.0)) - 3.0) < 0.1
            and abs(float(getattr(operation, "depth", 0.0)) - 12.0) < 0.1
            and str(getattr(operation, "face", "")).split(".")[-1] == "LEFT"
        )

    @staticmethod
    def _operation_signatures(operations):
        return sorted(
            {
                (
                    getattr(operation, "operation_type", getattr(operation, "op_type", "")),
                    round(float(getattr(operation, "diameter", 0.0)), 3),
                    round(float(getattr(operation, "depth", 0.0)), 3),
                    str(getattr(operation, "face", "")).split(".")[-1],
                    round(
                        float(
                            getattr(
                                operation,
                                "x",
                                getattr(operation, "local_x", 0.0),
                            )
                        ),
                        3,
                    ),
                    round(
                        float(
                            getattr(
                                operation,
                                "y",
                                getattr(operation, "local_y", 0.0),
                            )
                        ),
                        3,
                    ),
                    str(getattr(operation, "axis", "Z")).upper(),
                )
                for operation in operations
            }
        )


if __name__ == "__main__":
    unittest.main()
