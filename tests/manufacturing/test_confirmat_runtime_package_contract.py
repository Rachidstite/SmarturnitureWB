import unittest

from domain.builders import WardrobeBuilder
from domain.core_types import NodeCategory
from domain.hardware_library import HardwareRegistry
from domain.manufacturing_compiler import ManufacturingCompiler
from domain.rules_engine import RuleContext, System32JoineryRule
from manufacturing.extractor import ManufacturingExtractor
from manufacturing.manufacturing_runtime_pipeline_builder import (
    ManufacturingRuntimePipelineBuilder,
)


class TestConfirmatRuntimePackageContract(unittest.TestCase):

    def test_confirmat_drilling_survives_into_runtime_manufacturing_package(self):
        project = WardrobeBuilder(
            uid="CONFIRMAT_RUNTIME_PACKAGE_CONTRACT",
            width=1000.0,
            height=2000.0,
            depth=600.0,
        )
        project.add_divider(x_offset=400.0)
        project = project.build()

        context = RuleContext()
        registry = HardwareRegistry()
        hardware = registry.get_hardware("CONFIRMAT_50_V1")

        self.assertIsNotNone(hardware)
        self.assertTrue(hardware.host_holes or hardware.target_holes)

        placements = [
            placement
            for placement in System32JoineryRule().apply(project, context)
            if placement.hardware_intent == "INTENT_CONFIRMAT_50"
        ]
        project.placements.extend(placements)

        self.assertTrue(project.placements)
        self.assertTrue(
            all(
                project.graph.get_node(placement.host_node_id).category
                == NodeCategory.PHYSICAL
                for placement in placements
            )
        )
        self.assertTrue(
            all(
                project.graph.get_node(placement.target_node_id).category
                == NodeCategory.PHYSICAL
                for placement in placements
            )
        )

        ManufacturingCompiler().compile(project, context)

        source_ops = self._confirmat_ops_from_nodes(project)
        self.assertTrue(source_ops)

        panel_specs = ManufacturingExtractor.extract(project.graph)
        extracted_ops = [
            op
            for spec in panel_specs
            for op in spec.cnc_operations
            if self._is_confirmat_drill(op)
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
            if self._is_confirmat_runtime_operation(op)
        ]

        self.assertTrue(runtime_ops)
        self.assertEqual(
            self._operation_signatures(runtime_ops),
            self._operation_signatures(source_ops),
        )

    @staticmethod
    def _confirmat_ops_from_nodes(project):
        ops = []
        for node in project.graph.physical_nodes:
            ops.extend(
                op
                for op in getattr(node, "machining_ops", [])
                if TestConfirmatRuntimePackageContract._is_confirmat_drill(op)
            )
        return ops

    @staticmethod
    def _is_confirmat_drill(operation):
        if getattr(operation, "op_type", "") != "DRILL":
            return False

        diameter = float(getattr(operation, "diameter", 0.0))
        depth = float(getattr(operation, "depth", 0.0))
        axis = str(getattr(operation, "axis", "Z")).upper()
        return (
            abs(diameter - 7.0) < 0.1
            and abs(depth - 18.0) < 0.1
        ) or (
            abs(diameter - 5.0) < 0.1
            and abs(depth - 34.0) < 0.1
            and axis == "X"
        )

    @staticmethod
    def _is_confirmat_runtime_operation(operation):
        operation_type = getattr(operation, "operation_type", "")
        diameter = float(getattr(operation, "diameter", 0.0))
        depth = float(getattr(operation, "depth", 0.0))
        axis = str(getattr(operation, "axis", "Z")).upper()
        return (
            operation_type == "DRILL"
            and (
                abs(diameter - 7.0) < 0.1
                and abs(depth - 18.0) < 0.1
                or (
                    abs(diameter - 5.0) < 0.1
                    and abs(depth - 34.0) < 0.1
                    and axis == "X"
                )
            )
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
